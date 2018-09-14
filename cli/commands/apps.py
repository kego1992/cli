# -*- coding: utf-8 -*-
import sys
import click
import click_spinner
import emoji

from .. import api
from .. import awesome
from .. import cli
from .. import options


def maintenance(enabled: bool) -> str:
    if enabled:
        return click.style('maintenance mode enabled', fg='red')
    else:
        return click.style('running', fg='green')


@cli.cli.command()
def apps():
    """
    List your applications
    """
    cli.user()
    click.echo(click.style('Applications', fg='magenta'))
    click.echo(click.style('============', fg='magenta'))

    with click_spinner.spinner():
        res = api.Apps.list()

    for app in res:
        click.echo(
            '\t'.join((
                click.style(app['name'], bold=True),
                maintenance(app['maintenance']),
                (
                    click.style('created:', dim=True) +
                    click.style(app['timestamp'])
                )
            ))
        )


@cli.cli.command(aliases=['apps:create'])
@click.argument('name', nargs=1, required=False)
@click.option('--team', type=str,
              help='Team name that owns this new Application')
def apps_create(name, team):
    """
    Create a new Asyncy App
    """
    cli.user()
    cli.track('Creating application')
    try:
        assert cli.run('git status 2&>1')
    except:
        click.echo('Please create your application '
                   'from a git-backed project folder.')
        click.echo(click.style('$ git init', bold=True, fg='magenta'))
        sys.exit(1)

    name = name or awesome.new()

    click.echo('Creating application... ', nl=False)
    with click_spinner.spinner():
        api.Apps.create(name=name, team=team)
    click.echo(click.style('√', fg='green'))

    click.echo('Adding git-remote... ', nl=False)
    cli.run(f'git remote add asyncy https://git.asyncy.com/{name}')
    click.echo(click.style('√', fg='green'))

    click.echo('\nNew application name: ' + click.style(name, bold=True))
    click.echo(
        'Found at ' +
        click.style(f'https://{name}.asyncyapp.com', fg='blue') +
        '\n'
    )

    click.echo(
        emoji.emojize(':party_popper:') +
        '  You are ready to build your first Asyncy App'
    )
    click.echo('- [ ] Write some stories')
    click.echo(
        '- [ ] ' +
        click.style('$ git add . && git commit -m "initial commit"',
                    fg='magenta')
    )
    click.echo(
        '- [ ] ' +
        click.style('$ git push asyncy master', fg='magenta')
    )
    click.echo(
        click.style('\nHINT:', fg='cyan') + ' run ' +
        click.style('$ asyncy bootstrap', fg='magenta') +
        ' for examples'
    )


@cli.cli.command(aliases=['apps:destroy'])
@options.app
@click.option('--confirm', is_flag=True,
              help='Do not prompt to confirm destruction.')
def apps_destroy(confirm, app):
    """
    Destory an application
    """
    cli.user()
    cli.track('Destroying application')
    if (
        confirm or
        click.confirm(f'Do you want to destory "{app}"?', abort=True)
    ):
        click.echo(f'Destroying application "{app}"...', nl=False)
        with click_spinner.spinner():
            api.Apps.destroy(app=app)
        click.echo(click.style('√', fg='green'))
