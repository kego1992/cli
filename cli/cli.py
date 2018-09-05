# -*- coding: utf-8 -*-

import json
import os
import subprocess
import sys

import click
from click_alias import ClickAliasedGroup
from click_didyoumean import DYMGroup
import click_help_colors
import emoji
from mixpanel import Mixpanel
from raven import Client
import requests

from .version import version


if not os.getenv('TOXENV'):
    mp = Mixpanel('c207b744ee33522b9c0d363c71ff6122')
    sentry = Client(
        'https://007e7d135737487f97f5fe87d5d85b55@sentry.io/1206504'
    )
else:
    mp = None
    sentry = Client()

data = None
home = os.path.expanduser('~/.asyncy')
token = None



def track(message, extra={}):
    try:
        extra['version'] = version
        mp.track(str(data['user']['id']), message, extra)
    except Exception:
        # ignore issues with tracking
        pass


def write(content: str, location: str):
    dir = os.path.dirname(location)
    if dir and not os.path.exists(dir):
        os.makedirs(dir)

    if isinstance(content, (list, dict)):
        content = json.dumps(content, indent=2)

    with open(location, 'w+') as file:
        file.write(content)


def user():
    """
    Get the active user
    """
    if (data or {}).get('user'):
        return data['user']

    else:
        click.echo(
            'Hi! Thank you for using ' +
            click.style('Λsyncy', fg='magenta')
        )
        click.echo('Please login to get started.')
        email = click.prompt(click.style('Email', fg='magenta'),
                             type=str)
        password = click.prompt(click.style('Password', fg='magenta'),
                                type=str, hide_input=True)
        res = requests.post(
            'https://alpha.asyncy.com/login',
            data=json.dumps({'email': email, 'password': password})
        )
        if res.status_code == 200:
            write(res.text, f'{home}/.config')
            write('', f'{home}/.history')
            init()
            click.echo(
                emoji.emojize(':waving_hand:') +
                f'  Welcome {data["user"]["name"]}.'
            )
            track('Logged into CLI')
            return data['user']

        else:
            click.echo('Sorry, failed to login. Please try again.')
            sys.exit(1)


def init():
    global data
    if os.path.exists(f'{home}/.config'):
        with open(f'{home}/.config', 'r') as file:
            data = json.load(file)
            sentry.user_context({
                'id': data['user']['id'],
                'email': data['user']['email']
            })


def stream(cmd: str):
    process = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == b'' and process.poll() is not None:
            break
        if output:
            click.echo(output.strip())


def run(cmd: str):
    output = subprocess.run(
        cmd.split(' '),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return str(output.stdout.decode('utf-8').strip())


# def _colorize(text, color=None):
#     # PATCH for https://github.com/r-m-n/click-help-colors/pull/3
#     from click.termui import _ansi_colors, _ansi_reset_all
#     if not color:
#         return text
#     try:
#         return '\033[%dm' % (_ansi_colors[color]) + text + _ansi_reset_all
#     except ValueError:
#         raise TypeError('Unknown color %r' % color)
#
#
# click_help_colors._colorize = _colorize


class Cli(DYMGroup, ClickAliasedGroup,
          click_help_colors.HelpColorsGroup):
    pass


@click.group(cls=Cli,
             help_headers_color='yellow',
             help_options_color='magenta')
def cli():
    """
    Hello! Welcome to Λsyncy

    We hope you enjoy and we look forward to your feedback.

    Documentation: https://docs.asyncy.com
    """
    init()
