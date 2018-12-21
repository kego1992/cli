# -*- coding: utf-8 -*-
import json
import os
import sys

import click

import emoji

from .. import cli


@cli.cli.command()
@click.option('--debug', is_flag=True, help='Compile in debug mode')
def test(debug):
    """
    Test the Stories
    """
    from storyscript.App import App
    cli.user()
    cli.track('Test Stories')
    click.echo(click.style('Compiling Stories...', bold=True))
    try:
        stories = json.loads(App.compile(os.getcwd(), debug=debug))
    except Exception as e:
        cli.track('Stories failed')
        cli.sentry.captureException()
        click.echo(click.style('X', fg='red') +
                   ' Errors found in Storyscript.')
        click.echo(str(e))
    else:
        cli.track('Stories passed')
        if stories['stories'] == {}:
            click.echo(click.style('\tX', fg='red') + ' No stories found')
            sys.exit(1)
        else:
            for k, v in stories['stories'].items():
                click.echo(click.style('\t√', fg='green') + f' {k}')

        # click.echo(click.style('Checking Services', bold=True))

        click.echo(click.style('√', fg='green') +
                   emoji.emojize(' Looking good! :thumbs_up:'))
        click.echo()
        click.echo('Deploy your app with:')
        cli.print_command('asyncy deploy')
