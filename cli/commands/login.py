# -*- coding: utf-8 -*-

import click
import delegator
import emoji
import json
import os
import requests
import sys

from .. import cli
from .update import update


@cli.Cli.command()
@click.option('--email', help='Your email address',
              prompt=True)
@click.option('--password', help='Password',
              prompt=True, hide_input=True)
@click.pass_context
def login(ctx, email, password):
    """
    Login to Asyncy
    """
    res = requests.post(
        'https://alpha.asyncy.com/login',
        data=json.dumps({'email': email, 'password': password})
    )
    if res.status_code == 200:
        cli.write(res.text, f'{cli.home}/data.json')
        cli.init()
        click.echo(emoji.emojize(':waving_hand:') +
                   f'  Welcome {cli.data["user"]["name"]}.')
        cli.track('Logged into CLI')
        delegator.run('git init')
        delegator.run('git remote add asyncy http://git.asyncy.net/app')
        if not os.path.exists(cli.home):
            os.mkdir(cli.home)
        cli.write('', f'{cli.home}/.history')
        click.echo(click.style('√', fg='green') + ' Setup repository.')
        ctx.invoke(update)
        click.echo('')
        click.echo('Success! ' + emoji.emojize(':party_popper:'))
        click.echo(click.style('Time to write your Story!', bold=True))
        click.echo('')
        click.echo('Opening ' +
                   click.style('https://docs.asyncy.com'
                               '/quick-start/#your-first-story', fg='cyan'))
        click.launch('https://docs.asyncy.com/quick-start/#your-first-story')

    else:
        click.echo('Please signup at ' +
                   click.style('https://asyncy.com', fg='cyan'))
        sys.exit(1)
