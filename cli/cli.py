# -*- coding: utf-8 -*-

import json
import os
import subprocess
import sys

import click
from click_alias import ClickAliasedGroup
from click_didyoumean import DYMGroup
import click_help_colors
from mixpanel import Mixpanel
from raven import Client

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
api_endpoint = 'cli.asyncy.com/v1'


def track(message, extra={}):
    try:
        extra['version'] = version
        mp.track(str(data['user']['id']), message, extra)
    except Exception:
        # ignore issues with tracking
        pass


def user(exit=True):
    """
    Get the active user
    """
    if (data or {}).get('user'):
        return True
    elif exit:
        click.echo('Please login to Asyncy with ', nl=False)
        click.echo(click.style('`asyncy login`', fg='magenta'))
        sys.exit(1)
    else:
        return False


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
    output = subprocess.run(cmd.split(' '), check=True, stdout=subprocess.PIPE)
    return str(output.stdout)


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
