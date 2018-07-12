# -*- coding: utf-8 -*-

import click
import emoji
import os

from cli import Cli


@Cli.Cli.command()
@click.argument('story', default='-',
                type=click.Choice(['http', 'every', 'function',
                                   'if', 'loop', 'twitter',
                                   'slack-bot', 'subscribe',
                                   'every', 'websocket',  '-']))
def bootstrap(story):
    """
    Produce example stories as templates to work from.
    """
    assert Cli.user()
    Cli.track('Bootstrap story')
    if story != '-':
        with open(os.path.join(os.path.dirname(__file__),
                               f'../stories/{story}.story'), 'r') as file:
            click.echo(file.read())

    else:
        click.echo(click.style('Choose a template', bold=True))
        click.echo(click.style('   http', fg='cyan') + '      - serverless http endpoint')
        click.echo(click.style('   function', fg='cyan') + '  - generic function')
        click.echo(click.style('   if', fg='cyan') + '        - if/then')
        click.echo(click.style('   loop', fg='cyan') + '      - for loop')
        click.echo(click.style('   twitter', fg='cyan') + '   - stream tweets')
        click.echo('')

        click.echo(click.style('Coming soon', bold=True) + ' -- Under active development')
        click.echo(click.style('   slack-bot', fg='cyan') + ' - Slack bot')
        click.echo(click.style('   subscribe', fg='cyan') + ' - event subscriptions')
        click.echo(click.style('   every', fg='cyan') + '     - periodic run this')
        click.echo(click.style('   websocket', fg='cyan') + ' - websocket support')
        click.echo('')

        click.echo(emoji.emojize(':backhand_index_pointing_right:  Run ' + click.style('asyncy bootsrap _template_name_', fg='magenta')))
        click.echo('')

        click.echo(click.style('More', bold=True))
        click.echo('    Examples at ' + click.style('https://github.com/topics/asyncy-example', fg='cyan'))
        click.echo('    Services at ' + click.style('https://hub.asyncy.com', fg='cyan'))
        click.echo('')
