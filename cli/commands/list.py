
# -*- coding: utf-8 -*-

import click

from .. import cli


@cli.cli.command()
def list():
    """
    List services and user interfaces
    """
    cli.track('List Services')
    click.echo(click.style('Services', bold=True))
    click.echo('    Your App --      ' +
               click.style('http://asyncy.net', fg='cyan'))
    click.echo('    Metrics --       ' +
               click.style('http://grafana.asyncy.net', fg='cyan') +
               ' login: admin@admin')
    click.echo('    Documentation -- ' +
               click.style('http://docs.asyncy.com', fg='cyan'))
    click.echo('    Asyncy Hub --    ' +
               click.style('http://hub.asyncy.com', fg='cyan'))
    click.echo('    Feedback --      ' +
               click.style('http://asyncy.click/feedback', fg='cyan'))
