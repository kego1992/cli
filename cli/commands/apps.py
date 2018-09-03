# -*- coding: utf-8 -*-
import click_spinner
import click
import emoji

from .. import cli
from .. import api
from .. import options


def status2term(status: str) -> str:
    if status == 'running':
        return click.style('status:', dim=True)+click.style('running', fg='green')
    else:
        return click.style('status:', dim=True)+click.style('not running', fg='red')


@cli.cli.command()
def apps():
    """
    List your applications
    """
    cli.user()
    click.echo(click.style('Applications', fg='magenta'))
    click.echo(click.style('============', fg='magenta'))

    with click_spinner.spinner():
        res = api.apps.list()

    for app in res:
        click.echo(
            '\t'.join((
                click.style(app['name'], bold=True),
                status2term(app['status']),
                click.style('created:', dim=True)+click.style(app['created'])
        )))


@cli.cli.command(aliases=['apps:create'])
@click.argument('name', nargs=-1)
def apps_create(name):
    """
    Create a new Asyncy App
    """
    cli.user()
    cli.track('Creating application')
    try:
        assert cli.run('git status 2&>1')
    except:
        click.echo('Please create your application \
                    from a git-backed project folder.')

    click.echo('Creating application... ', nl=False)
    with click_spinner.spinner():
        res = api.apps.create(name)
    click.echo(click.style('√', fg='green'))

    click.echo('Adding git-remote... ', nl=False)
    cli.run(f'git remote add asyncy {res["remote"]}')
    click.echo(click.style('√', fg='green'))

    click.echo('\nNew application name: ' + click.style(res['name'], bold=True))
    click.echo('Found at ' + \
        click.style(f'https://{res["name"]}.asyncyapp.com', fg='blue') + '\n')

    click.echo(emoji.emojize(':party_popper:') + \
        '  You are ready to build your first Asyncy App')
    click.echo('- [ ] Write some stories')
    click.echo('- [ ] ' + \
        click.style('$ git add . && git commit -m "initial commit"',
                    fg='magenta'))
    click.echo('- [ ] ' + \
        click.style('$ git push asyncy master', fg='magenta'))
    click.echo(click.style('\nHINT:', fg='cyan') + ' run ' + \
        click.style('$ asyncy bootstrap', fg='magenta') + ' for examples')


@cli.cli.command(aliases=['apps:destroy'])
@options.app
@click.option('--confirm', is_flag=True, help='Do not prompt to confirm destruction.')
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
            api.apps.destroy(app)
        click.echo(click.style('√', fg='green'))
