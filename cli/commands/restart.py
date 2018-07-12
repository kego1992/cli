# -*- coding: utf-8 -*-

import click

from cli.Cli import Cli
from .shutdown import shutdown
from .start import start


@Cli.command()
@click.pass_context
def restart(ctx):
    """
    Restart the stack
    """
    ctx.invoke(shutdown)
    ctx.invoke(start)
