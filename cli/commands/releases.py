# -*- coding: utf-8 -*-
import sys

import click

import click_spinner

from .. import api
from .. import cli
from .. import options
from ..helpers.datetime import parse_psql_date_str, reltime


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
    cli.assert_project()

    # click.echo(click.style('Releases', fg='magenta'))
    # click.echo(click.style('========', fg='magenta'))

    with click_spinner.spinner():
        res = api.Releases.list(app, limit=limit)

    if res:
        from texttable import Texttable
        table = Texttable(max_width=800)
        table.set_deco(Texttable.HEADER)
        table.set_cols_align(['l', 'l', 'l'])
        all_releases = [['VERSION', 'CREATED', 'MESSAGE']]
        for release in res:
            date = parse_psql_date_str(release['timestamp'])
            all_releases.append([
                f'v{release["id"]}',
                reltime(date),
                release['message']
            ])
        table.add_rows(rows=all_releases)
        click.echo(table.draw())
    else:
        click.echo(f'No releases yet for app {app}.')


@cli.cli.command(aliases=['releases:rollback'])
@click.argument('version', nargs=1, required=False)
@options.app
def releases_rollback(version, app):
    """
    Rollback release to a previous release.
    """
    cli.user()
    cli.assert_project()

    if not version:
        click.echo(f'Getting latest release for app {cli.get_app_name()}... ',
                   nl=False)
        with click_spinner.spinner():
            res = api.Releases.get(app=app)
            version = int(res[0]['id']) - 1
        click.echo(click.style('√', fg='green'))

    if int(version) == 0:
        click.echo('Unable to rollback a release before v1.')
        sys.exit(1)

    click.echo(f'Rolling back to v{version}... ', nl=False)
    with click_spinner.spinner():
        res = api.Releases.rollback(version=version, app=app)
    click.echo(click.style('√', fg='green'))
    click.echo(f'Deployed new release... ' +
               click.style(f'v{res["id"]}', bold=True, fg='magenta'))
