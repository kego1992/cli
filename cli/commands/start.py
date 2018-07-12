# -*- coding: utf-8 -*-

import click
import sys

from cli import Cli
from .list import list


@Cli.Cli.command()
@click.pass_context
def start(ctx):
    """
    Start the Asyncy Stack
    """
    assert Cli.user()
    Cli.track('Start Stack')

    if Cli.running(exit=False):
        click.echo(click.style('Stack is running already.'))
        sys.exit(0)

    click.echo(click.style('Starting Asyncy', bold=True))
    Cli.stream(f'{Cli.dc} up -d')
    click.echo(click.style('√', fg='green') + ' Stack is up!')
    ctx.invoke(list)
