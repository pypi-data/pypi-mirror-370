# perceval-topicbox

Perceval backend for Topicbox.

## Backends

The backend currently managed by this package support the next repository:

* Topicbox

## Requirements

 * Python >= 3.9

You will also need some other libraries for running the tool, you can find the
whole list of dependencies in [pyproject.toml](pyproject.toml) file.

## Installation

There are several ways to install perceval-topicbox on your system: packages or source 
code using Poetry or pip.

### PyPI

perceval-topicbox can be installed using pip, a tool for installing Python packages. 
To do it, run the next command:
```
$ pip install perceval-topicbox
```

### Source code

To install from the source code you will need to clone the repository first:
```
$ git clone https://github.com/bitergia-analytics/grimoirelab-perceval-topicbox
$ cd grimoirelab-perceval-topicbox
```

Then use pip or Poetry to install the package along with its dependencies.

#### Pip
To install the package from local directory run the following command:
```
$ pip install .
```
In case you are a developer, you should install perceval-topicbox in editable mode:
```
$ pip install -e .
```

#### Poetry
We use [poetry](https://python-poetry.org/) for dependency management and 
packaging. You can install it following its [documentation](https://python-poetry.org/docs/#installation).
Once you have installed it, you can install perceval-topicbox and the dependencies in 
a project isolated environment using:
```
$ poetry install
```
To spaw a new shell within the virtual environment use:
```
$ poetry shell
```

## Example

### Topicbox

You need an `account_id` and a group URL to fetch the messages.

- To obtain the `account_id`, open Network tab in the browser Devtool and identify the `accountId` in any
`/jmap` request made by the browser.

Run perceval with the Topicbox group URL and the account id to fetch the messages. For example:

```
$ perceval topicbox "https://mytopicbox.topicbox.com/groups/example" --account-id <account_id>
```

It can be run from a specific date using the `--from-date` parameter.

## License

Licensed under GNU General Public License (GPL), version 3 or later.
