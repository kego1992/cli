# -*- coding: utf-8 -*-

import click
import click_spinner

from .. import cli


@cli.Cli.command()
def status():
    """
    Show stack services and health
    """
    assert cli.user()
    assert cli.running()
    cli.track('Stack ps')
    click.echo(click.style('Listing Asyncy containers... ', bold=True),
               nl=False)
    with click_spinner.spinner():
        click.echo(cli.run('ps').out)
