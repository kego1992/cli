# -*- coding: utf-8 -*-
import subprocess
import sys

import click

import click_spinner

import emoji

from .. import api
from .. import awesome
from .. import cli
from .. import options
from ..helpers.datetime import parse_psql_date_str, reltime


def maintenance(enabled: bool) -> str:
    if enabled:
        return 'in maintenance'
    else:
        return 'running'


@cli.cli.command()
def apps():
    """
    List your applications
    """
    from texttable import Texttable
    cli.user()

    with click_spinner.spinner():
        res = api.Apps.list()

    count = 0
    # Heads up! Texttable does not like colours.
    # So don't use click.style here.
    table = Texttable(max_width=800)
    table.set_deco(Texttable.HEADER)
    table.set_cols_align(['l', 'l', 'l'])
    all_apps = [['NAME', 'STATE', 'CREATED']]
    for app in res:
        count += 1
        date = parse_psql_date_str(app['timestamp'])
        all_apps.append([
            app['name'],
            maintenance(app['maintenance']),
            reltime(date)
        ])

    table.add_rows(rows=all_apps)

    if count == 0:
        click.echo('No application found. Create your first app with')
        click.echo(click.style('$ asyncy apps:create', fg='magenta'))
    else:
        click.echo(table.draw())


def _is_git_repo_good():
    try:
        assert cli.run('git status 2&>1')
    except:
        click.echo('Please create your application '
                   'from a git-backed project folder.')
        click.echo(click.style('$ git init', bold=True, fg='magenta'))
        sys.exit(1)

    try:
        # This will raise an error if a remote by the name of asyncy does
        # not exist.
        remote = cli.run('git remote get-url asyncy')
        click.echo(
            click.style('There appears to be git remote '
                        f'named asyncy already ({remote}).\n', fg='red'))
        click.echo('If you\'re trying to create a new app, please create a\n'
                   'new directory with a git repository '
                   'in there.')
        sys.exit(1)
    except subprocess.CalledProcessError:
        # This just means that the remote does not exist, which is OK.
        pass


@cli.cli.command(aliases=['apps:create'])
@click.argument('name', nargs=1, required=False)
@click.option('--team', type=str,
              help='Team name that owns this new Application')
def apps_create(name, team):
    """
    Create a new Asyncy App
    """
    cli.user()
    asyncy_yaml = cli.find_asyncy_yml()
    if asyncy_yaml is not None:
        click.echo(
            click.style('There appears to be an Asyncy project in '
                        f'{asyncy_yaml} already.\n', fg='red'))
        click.echo(
            click.style('Are you trying to deploy? '
                        'Try the following:', fg='red'))
        click.echo(click.style('$ asyncy deploy', fg='magenta'))
        sys.exit(1)
    # _is_git_repo_good()

    name = name or awesome.new()

    click.echo('Creating application... ', nl=False)
    with click_spinner.spinner():
        api.Apps.create(name=name, team=team)
    click.echo(click.style('√', fg='green'))

    # click.echo('Adding git-remote... ', nl=False)
    # cli.run(f'git remote add asyncy https://git.asyncy.com/{name}')
    # click.echo(click.style('√', fg='green'))
    click.echo('Creating asyncy.yml...', nl=False)
    cli.write(f'app_name: {name}\n', 'asyncy.yml')

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
    cli.track('App Created', {'App name': name})
    click.echo('- [ ] Write some stories')
    click.echo('- [ ] ' + click.style('$ asyncy deploy', fg='magenta'))
    click.echo(
        click.style('\nHINT:', fg='cyan') + ' run ' +
        click.style('$ asyncy bootstrap', fg='magenta') + ' for examples'
    )


@cli.cli.command(aliases=['apps:url'])
@options.app
def apps_url(app):
    """
    Returns the full url of your application.
    Great to use with $(asyncy apps:url) in bash.
    """
    cli.user()
    cli.assert_project()
    print_nl = False
    import os
    if os.isatty(sys.stdout.fileno()):
        print_nl = True

    click.echo(f'https://{app}.asyncyapp.com', nl=print_nl)


@cli.cli.command(aliases=['apps:destroy'])
@options.app
@click.option('--confirm', is_flag=True,
              help='Do not prompt to confirm destruction.')
def apps_destroy(confirm, app):
    """
    Destroy an application
    """
    cli.user()
    cli.assert_project()
    if (
        confirm or
        click.confirm(f'Do you want to destroy "{app}"?', abort=True)
    ):
        click.echo(f'Destroying application "{app}"...', nl=False)
        with click_spinner.spinner():
            api.Apps.destroy(app=app)
            cli.track('App Destroyed', {'App name': app})
        click.echo(click.style('√', fg='green'))
