# Asyncy CI

![Requires.io](https://img.shields.io/requires/github/asyncy/cli.svg?style=flat-square)
![CircleCI](https://img.shields.io/circleci/project/github/asyncy/cli.svg?style=flat-square)
![Codecov](https://img.shields.io/codecov/c/github/asyncy/cli.svg?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/asyncy.svg?style=flat-square)


The Asyncy CLI is used to manage Asyncy from the command line.

## Overview

The goals of this project is to provide a utility for developers to interact with all of Asyncy features/services.

## Installation

```shell
$ brew install brew/asyncy/brew
```

✨🍰✨

## Usage

```shell
$ asyncy

Usage: asyncy [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  login
  ...
```

## Issues

For problems directly related to the CLI, [add an issue on GitHub](https://github.com/asyncy/cli/issues/new).

For other issues, [submit a support ticket](mailto:support@asyncy.com)

[Contributors](https://github.com/asyncy/cli/contributors)

## Developing

Run
```sh
virtualenv venv --python=python3
source venv/bin/activate
pip install -r requirements.txt
python -m cli.main
```

Test
```sh
pip install tox
source venv/bin/activate
tox
```

Install
```sh
python setup.py install
```
