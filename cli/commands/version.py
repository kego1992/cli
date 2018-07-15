# -*- coding: utf-8 -*-

import click

import storyscript

from .. import cli


@cli.cli.command()
def version():
    """
    Show version number
    """
    click.echo(
        click.style('Λsyncy', fg='magenta') + ' ' +
        cli.version + click.style(' - ', dim=True) +
        click.style('Storyscript', fg='cyan') + ' ' +
        storyscript.version
    )
