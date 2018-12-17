# -*- coding: utf-8 -*-
import pkgutil

import click

import emoji

from .. import cli


@cli.cli.command()
@click.argument('story', default='-',
                type=click.Choice(['http', 'every', 'function',
                                   'if', 'loop', 'twitter',
                                   'slack-bot', 'subscribe',
                                   'every', 'websocket', '-']))
def bootstrap(story):
    """
    Produce example stories as templates to work from.
    """
    if story != '-':
        data = pkgutil.get_data('cli', f'stories/{story}.story')
        click.echo(data)
        try:
            app_name = cli.get_app_name()
        except:
            app_name = 'Not created yet'

        cli.track('App Bootstrapped',
                  {'App name': app_name, 'Template used': story})

    else:
        click.echo(click.style('Choose a template', bold=True))
        click.echo(click.style('   http', fg='cyan') +
                   '      - serverless http endpoint')
        click.echo(click.style('   function', fg='cyan') +
                   '  - generic function')
        click.echo(click.style('   if', fg='cyan') +
                   '        - if/then')
        click.echo(click.style('   loop', fg='cyan') +
                   '      - for loop')
        click.echo(click.style('   twitter', fg='cyan') +
                   '   - stream tweets')
        click.echo('')

        click.echo(click.style('Coming soon', bold=True) +
                   ' -- Under active development')
        click.echo(click.style('   slack-bot', fg='cyan') +
                   ' - Slack bot')
        click.echo(click.style('   subscribe', fg='cyan') +
                   ' - event subscriptions')
        click.echo(click.style('   every', fg='cyan') +
                   '     - periodic run this')
        click.echo(click.style('   websocket', fg='cyan') +
                   ' - websocket support')
        click.echo('')

        click.echo(emoji.emojize(':backhand_index_pointing_right:') +
                   '  Run ' +
                   click.style('asyncy bootsrap _template_name_',
                               fg='magenta'))
        click.echo('')

        click.echo(click.style('More', bold=True))
        click.echo('    Examples at ' +
                   click.style('https://github.com/topics/asyncy-example',
                               fg='cyan'))
        click.echo('    Services at ' +
                   click.style('https://hub.asyncy.com', fg='cyan'))
        click.echo('')
