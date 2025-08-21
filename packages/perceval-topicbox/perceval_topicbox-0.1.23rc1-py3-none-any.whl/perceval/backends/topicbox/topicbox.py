# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Jose Javier Merchante <jjmerchante@bitergia.com>
#

import datetime
import json
import logging

import dateutil.tz

from grimoirelab_toolkit.datetime import str_to_datetime, datetime_to_utc
from grimoirelab_toolkit.uris import urijoin

from ...backend import (Backend,
                        BackendCommand,
                        BackendCommandArgumentParser)
from ...client import HttpClient
from ...errors import BackendError

CATEGORY_MESSAGE = 'message'

MAX_MESSAGES_PER_PAGE = 100

JMAP_CLIENT_CAPABILITIES = [
    "urn:ietf:params:jmap:mail",
    "urn:ietf:params:jmap:core",
    "https://www.topicbox.com/dev/organisation"
]

DEFAULT_DATETIME = datetime.datetime(1970, 1, 1, 0, 0, 0,
                                     tzinfo=dateutil.tz.tzutc())
DEFAULT_LAST_DATETIME = datetime.datetime(2100, 1, 1, 0, 0, 0,
                                          tzinfo=dateutil.tz.tzutc())

logger = logging.getLogger(__name__)


class Topicbox(Backend):
    """Topicbox backend for Perceval.

    This class retrieves the email messages stored in Topicbox group
    using the JSON Meta Application Protocol (JMAP).
    Initialize this class passing the URL of a Topicbox group.
    The origin of the data will be set to the value of `uri`.

    :param uri: URI of the Topicbox group
    :param account_id: account id for Topicbox's JMAP
    :param tag: label used to mark the data
    :param archive: archive to store/retrieve items
    """
    version = '0.1.0'

    CATEGORIES = [CATEGORY_MESSAGE]

    DATE_FIELD = 'sentAt'
    MESSAGE_ID_FIELD = 'messageId'

    def __init__(self, uri, account_id, tag=None, archive=None,
                 max_items=MAX_MESSAGES_PER_PAGE, ssl_verify=True):
        origin = uri

        super().__init__(origin, tag=tag, archive=archive, ssl_verify=ssl_verify)

        self.uri = uri
        self.group_tag = uri.rstrip('/').split('/')[-1]
        self.account_id = account_id
        self.max_items = max_items

        self.client = None

    def fetch(self, category=CATEGORY_MESSAGE, filter_classified=False,
              from_date=DEFAULT_DATETIME, to_date=DEFAULT_LAST_DATETIME):
        """Fetch the emails from a Topicbox group.

        The method retrieves from Topicbox the messages using the
        JMAP protocol after the given date.

        :param category: the category of items to fetch
        :param filter_classified: remove classified fields from the resulting items
        :param from_date: obtain messages created since this date
        :param to_date: obtain messages until a specific date

        :returns: a generator of messages
        """
        if not from_date:
            from_date = DEFAULT_DATETIME
        if not to_date:
            to_date = DEFAULT_LAST_DATETIME

        from_date = datetime_to_utc(from_date)
        to_date = datetime_to_utc(to_date)

        kwargs = {
            'from_date': from_date,
            'to_date': to_date
        }
        items = super().fetch(category,
                              filter_classified=filter_classified,
                              **kwargs)

        return items

    def fetch_items(self, category, **kwargs):
        """Fetch the messages.

        :param category: the category of items to fetch
        :param kwargs: backend arguments

        :returns: a generator of items
        """
        from_date = kwargs['from_date']
        to_date = kwargs['to_date']

        logger.info(f"Fetching messages on '{self.uri}' from {from_date} to {to_date}")

        group = self.client.group(self.group_tag)

        if not group:
            raise BackendError(cause=f'Group {self.uri} not found.')

        mailbox_id = group['archiveMailboxId']
        items = self.client.messages(mailbox_id, from_date, to_date)

        return items

    @classmethod
    def has_archiving(cls):
        """Returns whether it supports archiving items on the fetch process.

        :returns: this backend does not support items archive
        """
        return False

    @classmethod
    def has_resuming(cls):
        """Returns whether it supports to resume the fetch process.

        :returns: this backend supports items resuming
        """
        return True

    @staticmethod
    def metadata_id(item):
        """Extracts the identifier from a message item."""

        return str(item[Topicbox.MESSAGE_ID_FIELD][0])

    @staticmethod
    def metadata_updated_on(item):
        """Extracts the update time from a message item.

        The timestamp is extracted from 'Date' field.
        This date is converted to UNIX timestamp format.

        :param item: item generated by the backend

        :returns: a UNIX timestamp
        """
        ts = item[Topicbox.DATE_FIELD]
        ts = str_to_datetime(ts)

        return ts.timestamp()

    @staticmethod
    def metadata_category(item):
        """Extracts the category from a message item.

        This backend only generates one type of item which is
        'message'.
        """
        return CATEGORY_MESSAGE

    def _init_client(self, from_archive=False):
        """Init client"""

        base_uri = self.uri.split('/groups')[0]
        return TopicboxClient(base_uri=base_uri, account_id=self.account_id,
                              max_items=self.max_items)


class TopicboxClient(HttpClient):
    """Client for retrieving emails from Topicbox

    :param base_uri: Base URL of the Topicbox web application
    :param account_id: account id for Topicbox's JMAP
    :param max_items: max number of messages items per query
    """
    def __init__(self, base_uri, account_id, max_items=MAX_MESSAGES_PER_PAGE):
        self.account_id = account_id
        self.max_items = max_items
        self.jmap_uri = urijoin(base_uri, 'jmap')

        super().__init__(base_url=self.jmap_uri)

    def group(self, identifier):
        """Get group info associated to an identifier"""

        request = {
            "using": JMAP_CLIENT_CAPABILITIES,
            "methodCalls": [[
                "Group/get", {
                    "accountId": self.account_id,
                    "ids": None
                }, "0"
            ]]
        }
        res = self.fetch(self.jmap_uri, payload=json.dumps(request), method=HttpClient.POST)
        data = res.json()

        for group in data['methodResponses'][0][1]['list']:
            if group['identifier'] == identifier:
                return group

        return None

    def messages(self, mailbox_id, from_date=DEFAULT_DATETIME, to_date=DEFAULT_LAST_DATETIME):
        """Fetch Topicbox mailbox messages

        :param mailbox_id: archive Mailbox id for a group
        :param from_date: obtain messages created since this date
        :param to_date: obtain messages until a specific date
        """
        position = 0

        from_date_iso = from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        to_date_iso = to_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        request = {
            "using": JMAP_CLIENT_CAPABILITIES,
            "methodCalls": [
                [
                    "Email/query", {
                        "accountId": self.account_id,
                        "calculateTotal": True,
                        "limit": self.max_items,
                        "position": position,
                        "collapseThreads": False,
                        "sort": [{"property": "receivedAt", "isAscending": True}],
                        "filter": {
                            "operator": "AND",
                            "conditions": [
                                {"inMailbox": mailbox_id},
                                {"after": from_date_iso},
                                {"before": to_date_iso}
                            ]
                        }
                    }, "0"
                ],
                [
                    "Email/get", {
                        "accountId": self.account_id,
                        "#ids": {"name": "Email/query", "path": "/ids", "resultOf": "0"},
                        "fetchHTMLBodyValues": True,
                        "properties": None
                    }, "1"
                ]
            ]
        }

        while True:
            request['methodCalls'][0][1]['position'] = position
            res = self.fetch(self.jmap_uri, payload=json.dumps(request), method=HttpClient.POST)
            data = res.json()

            messages = data['methodResponses'][1][1]['list']
            for message in messages:
                yield message

            total = data['methodResponses'][0][1]['total']
            position += len(messages)
            if position >= total:
                break


class TopicboxCommand(BackendCommand):
    """Class to run Topicbox backend from the command line."""

    BACKEND = Topicbox

    @classmethod
    def setup_cmd_parser(cls):
        """Returns the Topicbox argument parser."""

        parser = BackendCommandArgumentParser(cls.BACKEND,
                                              from_date=True,
                                              to_date=True)
        # Required arguments
        group = parser.parser.add_argument_group('Topicbox arguments')
        group.add_argument('uri',
                           help="URL of the Topicbox group")
        group.add_argument('--account-id', dest='account_id',
                           type=str, help="Account ID for Topicbox")
        group.add_argument('--max-items', dest='max_items',
                           default=MAX_MESSAGES_PER_PAGE, type=int,
                           help="Max number of messages per query.")

        return parser
