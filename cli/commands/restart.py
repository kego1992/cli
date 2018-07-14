# -*- coding: utf-8 -*-

import click

from .. import cli
from .shutdown import shutdown
from .start import start


@cli.Cli.command()
@click.pass_context
def restart(ctx):
    """
    Restart the stack
    """
    ctx.invoke(shutdown)
    ctx.invoke(start)
