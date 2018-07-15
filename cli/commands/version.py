# -*- coding: utf-8 -*-

import click

import storyscript

from .. import cli


@cli.Cli.command()
def version():
    """
    Show version number
    """
    click.echo(
        click.style('Λsyncy', fg='magenta') + ' ' +
        click.style(cli.VERSION, dim=True) + ' // ' +
        click.style('Storyscript', fg='cyan') + ' ' +
        click.style(storyscript.version, dim=True)
    )
