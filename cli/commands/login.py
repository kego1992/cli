# -*- coding: utf-8 -*-

import os
import click
import requests
import delegator
import emoji
import json
import sys

from cli import Cli
from .update import update


@Cli.Cli.command()
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
        Cli.write(res.text, f'{Cli.home}/data.json')
        Cli.init()
        click.echo(emoji.emojize(f":waving_hand:  Welcome {Cli.data['user']['name']}."))
        Cli.track('Logged into CLI')
        delegator.run('git init')
        delegator.run('git remote add asyncy http://git.asyncy.net/app')
        if not os.path.exists(Cli.home):
            os.mkdir(Cli.home)
        Cli.write('', f'{Cli.home}/.history')
        click.echo(click.style('√', fg='green') + ' Setup repository.')
        ctx.invoke(update)
        click.echo('')
        click.echo('Success! ' + emoji.emojize(':party_popper:'))
        click.echo(click.style('Time to write your Story!', bold=True))
        click.echo('')
        click.echo('Opening ' + click.style('https://docs.asyncy.com/quick-start/#your-first-story', fg='cyan'))
        click.launch('https://docs.asyncy.com/quick-start/#your-first-story')

    else:
        click.echo('Please signup at ' + click.style('https://asyncy.com', fg='cyan'))
        sys.exit(1)
