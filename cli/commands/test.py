# -*- coding: utf-8 -*-

import os
import sys

import click
import emoji
from storyscript.app import App

from .. import cli


@cli.cli.command()
@click.option('--debug', is_flag=True, help='Compile in debug mode')
def test(debug):
    """
    Test the Stories
    """
    assert cli.user()
    cli.track('Test Stories')
    click.echo(click.style('Compiling Stories', bold=True))
    try:
        stories = App.compile(os.getcwd(), debug=debug)
    except Exception as e:
        cli.track('Stories failed')
        cli.sentry.captureException()
        click.echo(click.style('X', fg='red') +
                   ' Errors found in Storyscript.')
        click.echo(str(e))
    else:
        cli.track('Stories passed')
        cli.write(stories, f'{cli.home}/stories.json')
        if stories['stories'] == {}:
            click.echo(click.style('   X', fg='red') + ' No stories found')
            sys.exit(1)
        else:
            click.echo(click.style('   √', fg='green') + ' Stories built.')

        # click.echo(click.style('Checking Services', bold=True))

        click.echo(click.style('√', fg='green') +
                   emoji.emojize(' Looking good! :thumbs_up:'))
