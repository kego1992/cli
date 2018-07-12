# -*- coding: utf-8 -*-

import click
import sys
import emoji
import delegator

from cli import Cli


@Cli.Cli.command()
@click.option('--force', '-f', is_flag=True, help='Forse push')
def deploy(force):
    """
    Deploy your application. Alias for

        git push asyncy master
    """
    assert Cli.user()
    Cli.track('Deploy App')
    if not force:
        res = delegator.run('git status -s')
        if res.out != '':
            Cli.track('Unstagged changes')
            click.echo(click.style('There are unstagged changes.', fg='red'))
            click.echo('The following files need to be commited before deploying your app.')
            click.echo(res.out.replace('?', '--'))
            click.echo(click.style('Note:', fg='cyan') + ' Asyncy runs ' +
                       click.style('git push asyncy master', fg='magenta') +
                       emoji.emojize(' to deploy :rocket:'))
            sys.exit(1)

    Cli.stream('git push asyncy master')
    click.echo('Your http endpoints resolve to ' + click.style('http://asyncy.net', fg='cyan'))
