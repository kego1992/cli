# -*- coding: utf-8 -*-

import sys

import click
import delegator
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
        res = delegator.run('git status -s')
        if res.out != '':
            cli.track('Unstagged changes')
            click.echo(click.style('There are unstagged changes.', fg='red'))
            click.echo('The following files need to be '
                       'commited before deploying your app.')
            click.echo(res.out.replace('?', '--'))
            click.echo(click.style('Note:', fg='cyan') + ' Asyncy runs ' +
                       click.style('git push asyncy master', fg='magenta') +
                       emoji.emojize(' to deploy :rocket:'))
            sys.exit(1)

    cli.stream('git push asyncy master')
    click.echo('Your http endpoints resolve to ' +
               click.style('http://asyncy.net', fg='cyan'))
