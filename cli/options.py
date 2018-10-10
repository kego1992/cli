# -*- coding: utf-8 -*-

import click

from .cli import run


try:
    from . import cli
    _app = cli.get_app_name()
except:
    _app = None


app = click.option(
    '--app', '-a',
    default=_app,
    help=f'(required) [default: {_app}] app to run command against'
)
