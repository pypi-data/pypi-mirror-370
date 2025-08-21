#!/usr/bin/env python3
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
import os
import unittest.mock

import httpretty
from dateutil.tz import tzutc

from perceval.backend import BackendCommandArgumentParser
from perceval.backends.topicbox.topicbox import (Topicbox,
                                                 TopicboxCommand,
                                                 TopicboxClient)

TOPICBOX_GROUPS = 'data/topicbox/topicbox_groups.json'
TOPICBOX_MESSAGES = 'data/topicbox/topicbox_messages.json'
TOPICBOX_PAGE_1 = 'data/topicbox/topicbox_messages_page_1.json'
TOPICBOX_PAGE_2 = 'data/topicbox/topicbox_messages_page_2.json'

TOPICBOX_JMAP_URL = 'http://example.com/jmap'
TOPICBOX_GROUP_URL = 'http://example.com/groups/test_group'


def read_file(filename, mode='r'):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), mode) as f:
        content = f.read()
    return content


def setup_http_server():
    topicbox_msgs = read_file(TOPICBOX_MESSAGES)

    http_requests = []

    def request_callback(method, uri, headers):
        last_request = httpretty.last_request()
        body = topicbox_msgs
        http_requests.append(last_request)
        return 200, headers, body

    httpretty.register_uri(httpretty.POST,
                           TOPICBOX_JMAP_URL,
                           responses=[
                               httpretty.Response(body=request_callback)
                           ])

    return http_requests


class TestTopicboxBackend(unittest.TestCase):
    """Topicbox backend tests"""

    def test_initialization(self):
        """Test whether attributes are initialized"""

        topicbox = Topicbox(uri=TOPICBOX_GROUP_URL,
                            account_id='acc_id',
                            tag='test',
                            max_items=10)

        self.assertEqual(topicbox.uri, TOPICBOX_GROUP_URL)
        self.assertEqual(topicbox.tag, 'test')
        self.assertEqual(topicbox.account_id, 'acc_id')
        self.assertEqual(topicbox.group_tag, 'test_group')
        self.assertEqual(topicbox.max_items, 10)

        # When tag is empty or None it will be set to
        # the value in the origin
        topicbox = Topicbox(TOPICBOX_GROUP_URL, 'acc_id')
        self.assertEqual(topicbox.uri, TOPICBOX_GROUP_URL)
        self.assertEqual(topicbox.tag, TOPICBOX_GROUP_URL)

        Topicbox(TOPICBOX_GROUP_URL, 'acc_id', tag='')
        self.assertEqual(topicbox.uri, TOPICBOX_GROUP_URL)
        self.assertEqual(topicbox.tag, TOPICBOX_GROUP_URL)

    def test_has_archiving(self):
        """Test if it returns False when has_archiving is called"""

        self.assertEqual(Topicbox.has_archiving(), False)

    def test_has_resuming(self):
        """Test if it returns True when has_resuming is called"""

        self.assertEqual(Topicbox.has_resuming(), True)

    @httpretty.activate
    @unittest.mock.patch('perceval.backends.topicbox.topicbox.TopicboxClient.group')
    def test_fetch(self, group_patch):
        """Test whether it fetches a set of messages"""

        group_patch.return_value = {'archiveMailboxId': 'test_group'}
        setup_http_server()

        backend = Topicbox(TOPICBOX_GROUP_URL, 'acc_id')
        messages = [m for m in backend.fetch()]

        expected = [
            ['message-1', '1af8c390de5940fbbef8daab31dd2e23ae9a514f', 1619071380.0],
            ['message-2', 'd64fbfa6c18670f7b25d5cb0b9fc7db461c9fcee', 1619080429.0],
            ['message-3', '191bcf17f547d9d953c834895d0f3d6dfee42aac', 1619080613.0]
        ]

        self.assertEqual(len(messages), len(expected))

        for i, message in enumerate(messages):
            self.assertEqual(message['data']['id'], expected[i][0])
            self.assertEqual(message['data']['threadId'], 'Thread-id-1')
            self.assertEqual(message['origin'], TOPICBOX_GROUP_URL)
            self.assertEqual(message['uuid'], expected[i][1])
            self.assertEqual(message['updated_on'], expected[i][2])
            self.assertEqual(message['category'], 'message')
            self.assertEqual(message['tag'], TOPICBOX_GROUP_URL)

    @httpretty.activate
    @unittest.mock.patch('perceval.backends.topicbox.topicbox.TopicboxClient.group')
    def test_search_fields(self, group_patch):
        """Test whether the search_fields is properly set"""

        group_patch.return_value = {'archiveMailboxId': 'test_group'}
        setup_http_server()

        backend = Topicbox(TOPICBOX_GROUP_URL, 'acc_id')
        messages = [m for m in backend.fetch()]

        for message in messages:
            self.assertEqual(backend.metadata_id(message['data']), message['search_fields']['item_id'])


class TestTopicboxCommand(unittest.TestCase):
    """Tests for TopicboxCommand class"""

    def test_backend_class(self):
        """Test if the backend class is Topicbox"""

        self.assertIs(TopicboxCommand.BACKEND, Topicbox)

    def test_setup_cmd_parser(self):
        """Test if the parser object is correctly initialized"""

        parser = TopicboxCommand.setup_cmd_parser()
        self.assertIsInstance(parser, BackendCommandArgumentParser)
        self.assertEqual(parser._backend, Topicbox)

        args = [
            TOPICBOX_GROUP_URL,
            '--account-id', 'acc_id',
            '--tag', 'test',
            '--from-date', '2020-01-01',
            '--max-items', '10'
        ]
        parsed_args = parser.parse(*args)
        self.assertEqual(parsed_args.uri, TOPICBOX_GROUP_URL)
        self.assertEqual(parsed_args.account_id, 'acc_id')
        self.assertEqual(parsed_args.tag, 'test')
        self.assertEqual(parsed_args.max_items, 10)
        self.assertEqual(parsed_args.from_date, datetime.datetime(2020, 1, 1, tzinfo=tzutc()))


class TestTopicboxClient(unittest.TestCase):
    """Tests for Topicbox client class"""

    def test_init(self):
        """Test initialization"""

        client = TopicboxClient(base_uri='http://example.com',
                                account_id='account1',
                                max_items=30)

        self.assertIsInstance(client, TopicboxClient)
        self.assertEqual(client.account_id, 'account1')
        self.assertEqual(client.max_items, 30)

    @httpretty.activate
    def test_group(self):
        """Test find group id from identifier"""

        # Set up a mock HTTP server
        body = read_file(TOPICBOX_GROUPS)
        httpretty.register_uri(httpretty.POST,
                               TOPICBOX_JMAP_URL,
                               body=body, status=200)

        expected_1 = json.loads(body)['methodResponses'][0][1]['list'][0]
        expected_2 = json.loads(body)['methodResponses'][0][1]['list'][1]

        # Call API
        client = TopicboxClient(base_uri='http://example.com',
                                account_id='account1',
                                max_items=35)

        group_1 = client.group('mailbox1')
        self.assertEqual(group_1, expected_1)

        group_2 = client.group('mailbox2')
        self.assertEqual(group_2, expected_2)

    @httpretty.activate
    def test_emails(self):
        """Test Emails/query request"""

        # Set up a mock HTTP server
        body = read_file(TOPICBOX_MESSAGES)
        httpretty.register_uri(httpretty.POST,
                               TOPICBOX_JMAP_URL,
                               body=body, status=200)

        # Call API
        client = TopicboxClient(base_uri='http://example.com',
                                account_id='account1',
                                max_items=35)
        messages = client.messages('mailbox1')

        self.assertEqual(len(list(messages)), 3)

        # Check request payload
        request_payload = {
            "using": [
                "urn:ietf:params:jmap:mail",
                "urn:ietf:params:jmap:core",
                "https://www.topicbox.com/dev/organisation"
            ],
            "methodCalls": [
                [
                    "Email/query",
                    {
                        "accountId": "account1",
                        "calculateTotal": True,
                        "limit": 35,
                        "position": 0,
                        "collapseThreads": False,
                        "sort": [
                            {
                                "property": "receivedAt",
                                "isAscending": True
                            }
                        ],
                        "filter": {
                            "operator": "AND",
                            "conditions": [
                                {
                                    "inMailbox": "mailbox1"
                                },
                                {
                                    "after": "1970-01-01T00:00:00Z"
                                },
                                {
                                    "before": "2100-01-01T00:00:00Z"
                                }
                            ]
                        }
                    },
                    "0"
                ],
                [
                    "Email/get",
                    {
                        "accountId": "account1",
                        "#ids": {
                            "name": "Email/query",
                            "path": "/ids",
                            "resultOf": "0"
                        },
                        "fetchHTMLBodyValues": True,
                        "properties": None
                    },
                    "1"
                ]
            ]
        }

        req = httpretty.last_request()

        self.assertEqual(req.method, 'POST')
        self.assertRegex(req.path, '/jmap')
        self.assertDictEqual(json.loads(req.parsed_body), request_payload)

    @httpretty.activate
    def test_messages_pagination(self):
        """Test Emails/query request with pagination"""

        # Set up a mock HTTP server
        bodies = [
            read_file(TOPICBOX_PAGE_1),
            read_file(TOPICBOX_PAGE_2)
        ]

        http_requests = []

        def request_callback(method, uri, headers):
            last_request = httpretty.last_request()
            http_requests.append(last_request)
            body = bodies.pop(0)
            return [200, headers, body]

        httpretty.register_uri(httpretty.POST,
                               TOPICBOX_JMAP_URL,
                               body=request_callback,
                               status=200)

        # Call API
        client = TopicboxClient(base_uri='http://example.com',
                                account_id='account1',
                                max_items=2)
        messages = [m for m in client.messages('mailbox1')]

        self.assertEqual(len(list(messages)), 3)

        expected_messages = ['message-1', 'message-2', 'message-3']

        request_payload_1 = {
            "using": [
                "urn:ietf:params:jmap:mail",
                "urn:ietf:params:jmap:core",
                "https://www.topicbox.com/dev/organisation"
            ],
            "methodCalls": [
                [
                    "Email/query",
                    {
                        "accountId": "account1",
                        "calculateTotal": True,
                        "limit": 2,
                        "position": 0,
                        "collapseThreads": False,
                        "sort": [
                            {
                                "property": "receivedAt",
                                "isAscending": True
                            }
                        ],
                        "filter": {
                            "operator": "AND",
                            "conditions": [
                                {
                                    "inMailbox": "mailbox1"
                                },
                                {
                                    "after": "1970-01-01T00:00:00Z"
                                },
                                {
                                    "before": "2100-01-01T00:00:00Z"
                                }
                            ]
                        }
                    },
                    "0"
                ],
                [
                    "Email/get",
                    {
                        "accountId": "account1",
                        "#ids": {
                            "name": "Email/query",
                            "path": "/ids",
                            "resultOf": "0"
                        },
                        "fetchHTMLBodyValues": True,
                        "properties": None
                    },
                    "1"
                ]
            ]
        }

        request_payload_2 = {
            "using": [
                "urn:ietf:params:jmap:mail",
                "urn:ietf:params:jmap:core",
                "https://www.topicbox.com/dev/organisation"
            ],
            "methodCalls": [
                [
                    "Email/query",
                    {
                        "accountId": "account1",
                        "calculateTotal": True,
                        "limit": 2,
                        "position": 2,
                        "collapseThreads": False,
                        "sort": [
                            {
                                "property": "receivedAt",
                                "isAscending": True
                            }
                        ],
                        "filter": {
                            "operator": "AND",
                            "conditions": [
                                {
                                    "inMailbox": "mailbox1"
                                },
                                {
                                    "after": "1970-01-01T00:00:00Z"
                                },
                                {
                                    "before": "2100-01-01T00:00:00Z"
                                }
                            ]
                        }
                    },
                    "0"
                ],
                [
                    "Email/get",
                    {
                        "accountId": "account1",
                        "#ids": {
                            "name": "Email/query",
                            "path": "/ids",
                            "resultOf": "0"
                        },
                        "fetchHTMLBodyValues": True,
                        "properties": None
                    },
                    "1"
                ]
            ]
        }

        self.assertEqual(len(http_requests), 2)

        req = http_requests[0]
        self.assertEqual(req.method, 'POST')
        self.assertRegex(req.path, '/jmap')
        self.assertDictEqual(json.loads(req.parsed_body), request_payload_1)

        req = http_requests[1]
        self.assertEqual(req.method, 'POST')
        self.assertRegex(req.path, '/jmap')
        self.assertDictEqual(json.loads(req.parsed_body), request_payload_2)

        for i, message in enumerate(messages):
            self.assertEqual(message['id'], expected_messages[i])
            self.assertEqual(message['threadId'], 'Thread-id-1')


if __name__ == "__main__":
    unittest.main(warnings='ignore')
