# -*- coding: utf-8 -*-

import sys

import click

from .list import list
from .. import cli


@cli.cli.command()
@click.pass_context
def start(ctx):
    """
    Start the Asyncy Stack
    """
    assert cli.user()
    cli.track('Start Stack')

    if cli.running(exit=False):
        click.echo(click.style('Stack is running already.'))
        sys.exit(0)

    click.echo(click.style('Starting Asyncy', bold=True))
    cli.stream(f'{cli.dc} up -d')
    click.echo(click.style('√', fg='green') + ' Stack is up!')
    ctx.invoke(list)
