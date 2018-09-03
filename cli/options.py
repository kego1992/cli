# -*- coding: utf-8 -*-

import click

from .cli import run


try:
    _app = run('git remote get-url asyncy').strip().split('/')[3]
except:
    _app = None


app = click.option(
    '--app', '-a',
    default=_app,
    help=f'(required) [default: {_app}] app to run command against'
)


release = click.option(
    '--release',
    default=True,
    help='Deploy a new release after changes apply.'
)
