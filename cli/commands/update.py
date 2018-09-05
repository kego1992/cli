# -*- coding: utf-8 -*-

import click

from .. import cli


@cli.cli.command()
def update():
    """
    Look for new version updates to CLI
    """
    # TODO create update command
    click.echo('Sorry, command not programmed yet.')
