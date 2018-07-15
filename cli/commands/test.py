# -*- coding: utf-8 -*-

import os
import sys

import click
import emoji
import storyscript

from .. import cli


@cli.cli.command()
def test():
    """
    Test the Stories
    """
    assert cli.user()
    cli.track('Test Stories')
    click.echo(click.style('Compiling Stories', bold=True))
    try:
        stories = storyscript.loads(os.getcwd())
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
