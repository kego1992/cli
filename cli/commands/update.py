# -*- coding: utf-8 -*-

import click
import click_spinner
import requests

from .start import start
from .. import cli


@cli.Cli.command()
@click.pass_context
def update(ctx):
    """
    Pull new updates to the Asyncy Stack
    """
    assert cli.user()
    cli.track('Update CLI')
    # update compose, pull new containes
    click.echo(click.style('Updating', bold=True))

    # Note cannot update via pip install...

    click.echo(click.style('   ->', fg='green') +
               ' docker-compose.yml... ', nl=False)
    with click_spinner.spinner():
        res = requests.get('https://raw.githubusercontent.com'
                           '/asyncy/stack-compose/master/docker-compose.yml')
        cli.write(res.text, f'{cli.home}/docker-compose.yml')
    click.echo('Done')

    click.echo(click.style('   ->', fg='green') + ' Pulling new services... ')
    cli.stream(f'{cli.dc} pull')
    click.echo(click.style('   ->', fg='green') + ' Shutting down stack... ')
    cli.stream(f'{cli.dc} down')
    click.echo('Done')

    ctx.invoke(start)
