# -*- coding: utf-8 -*-
import subprocess
import sys
import click_spinner

import click

from .. import cli
from .. import api
from .. import options


@cli.cli.command()
@click.option('--limit', '-n', nargs=1, default=20,
              help='List N latest releases')
@options.app
def releases(app, limit):
    """
    List application releases

    More:

    $ asyncy releases:rollback
    """
    cli.user()

    click.echo(click.style('Releases', fg='magenta'))
    click.echo(click.style('========', fg='magenta'))

    with click_spinner.spinner():
        res = api.releases.list(app, limit=limit)

    if res:
        for release in res:
            click.echo(
                '\t'.join((
                    click.style(f"v{release['version']}", bold=True),
                    release['title'],
                    click.style('created:', dim=True) +
                    click.style(release['created'])
                ))
            )
    else:
        click.echo('No releases yet.')



@cli.cli.command(aliases=['releases:rollback'])
@click.argument('version', nargs=-1, default=None)
@options.app
def releases_rollback(version, app):
    """
    Rollback release to a previous version. The default is the previous release.
    """
    cli.user()

    if not version:
        res = api.releases.list(app, limit=1)
        version = res[0]['version']

    click.echo(f'Rolling back to v{version}... ', nl=False)
    with click_spinner.spinner():
        res = api.releases.rollback(version, app)
    click.echo(click.style('√', fg='green'))
    click.echo(f'Rollback scheduled... v{res["version"]}')
