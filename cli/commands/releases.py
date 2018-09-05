# -*- coding: utf-8 -*-
import sys
import click
import click_spinner


from .. import api
from .. import cli
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
        res = api.Releases.list(app, limit=limit)

    if res:
        for release in res:
            click.echo(
                '\t'.join((
                    click.style(f'v{release["id"]}', bold=True),
                    click.style('created:', dim=True) +
                    click.style(release['timestamp']),
                    click.style(release['message'], fg='blue'),
                ))
            )
    else:
        click.echo('No releases yet.')


@cli.cli.command(aliases=['releases:rollback'])
@click.argument('version', nargs=1, required=False)
@options.app
def releases_rollback(version, app):
    """
    Rollback release to a previous release.
    """
    cli.user()

    if not version:
        click.echo(f'Getting latest release... ', nl=False)
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
