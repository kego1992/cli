# -*- coding: utf-8 -*-

import click

from .. import cli


@cli.cli.command()
def version():
    """
    Show version number
    """
    from storyscript import version

    click.echo(
        click.style('Λsyncy', fg='magenta') + ' ' +
        cli.version + click.style(' - ', dim=True) +
        click.style('Storyscript', fg='cyan') + ' ' +
        version
    )
