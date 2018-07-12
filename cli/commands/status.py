# -*- coding: utf-8 -*-

import click
import click_spinner

from cli import Cli


@Cli.Cli.command()
def status():
    """
    Show stack services and health
    """
    assert Cli.user()
    assert Cli.running()
    Cli.track('Stack ps')
    click.echo(click.style('Listing Asyncy containers... ', bold=True), nl=False)
    with click_spinner.spinner():
        click.echo(Cli.run('ps').out)
