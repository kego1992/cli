# -*- coding: utf-8 -*-

import click
import click_spinner
import requests

from cli import Cli
from .start import start


@Cli.Cli.command()
@click.pass_context
def update(ctx):
    """
    Pull new updates to the Asyncy Stack
    """
    assert Cli.user()
    Cli.track('Update CLI')
    # update compose, pull new containes
    click.echo(click.style('Updating', bold=True))

    # Note cannot update via pip install...

    click.echo(click.style('   ->', fg='green') + ' docker-compose.yml... ', nl=False)
    with click_spinner.spinner():
        res = requests.get('https://raw.githubusercontent.com/asyncy/stack-compose/master/docker-compose.yml')
        Cli.write(res.text, f'{Cli.home}/docker-compose.yml')
    click.echo('Done')

    click.echo(click.style('   ->', fg='green') + ' Pulling new services... ')
    Cli.stream(f'{Cli.dc} pull')
    click.echo(click.style('   ->', fg='green') + ' Shutting down stack... ')
    Cli.stream(f'{Cli.dc} down')
    click.echo('Done')

    ctx.invoke(start)
