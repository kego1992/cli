# -*- coding: utf-8 -*-

import click

from .shutdown import shutdown
from .start import start
from .. import cli


@cli.cli.command()
@click.pass_context
def restart(ctx):
    """
    Restart the stack
    """
    ctx.invoke(shutdown)
    ctx.invoke(start)
