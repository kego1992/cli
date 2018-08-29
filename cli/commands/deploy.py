# -*- coding: utf-8 -*-
import subprocess
import sys

import click
import emoji

from .. import cli


@cli.cli.command()
@click.option('--force', '-f', is_flag=True, help='Forse push')
def deploy(force):
    """
    Deploy your application. Alias for

        git push asyncy master
    """
    assert cli.user()
    cli.track('Deploy App')
    if not force:
        res = cli.run('git status -s', raw=True)
        if res.stdout.decode('utf-8') != '':
            cli.track('Unstagged changes')
            click.echo(click.style('There are unstagged changes.', fg='red'))
            click.echo('The following files need to be '
                       'commited before deploying your app.')
            click.echo(res.stdout.decode('utf-8').replace('?', '--'))
            click.echo(click.style('Note:', fg='cyan') + ' Asyncy runs ' +
                       click.style('git push asyncy master', fg='magenta') +
                       emoji.emojize(' to deploy :rocket:'))
            sys.exit(1)

    cli.stream('git push asyncy master')
    click.echo('Your http endpoints resolve to ' +
               click.style('http://asyncy.net', fg='cyan'))
