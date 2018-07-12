# -*- coding: utf-8 -*-

import click
import storyscript
import emoji
import json
import sys

from cli import Cli


@Cli.Cli.command()
def test():
    """
    Test the Stories
    """
    assert Cli.user()
    Cli.track('Test Stories')
    click.echo(click.style('Compiling Stories', bold=True))
    try:
        stories = storyscript.loads(os.getcwd())
    except Exception as e:
        Cli.track('Stories failed')
        sentry.captureException()
        click.echo(click.style('X', fg='red') + ' Errors found in Storyscript.')
        click.echo(str(e))
    else:
        Cli.track('Stories passed')
        Cli.write(stories, f'{Cli.home}/stories.json')
        stories = json.loads(application)
        if stories['stories'] == {}:
            click.echo(click.style('   X', fg='red') + ' No stories found')
            sys.exit(1)
        else:
            click.echo(click.style('   √', fg='green') + ' Stories built.')

        # click.echo(click.style('Checking Services', bold=True))

        click.echo(click.style('√', fg='green') + emoji.emojize(' Looking good! :thumbs_up:'))
