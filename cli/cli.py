# -*- coding: utf-8 -*-

import json
import os
import subprocess
import sys

import click
from click_alias import ClickAliasedGroup
from click_didyoumean import DYMGroup
import click_help_colors
import click_spinner
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
dc = f'docker-compose -f {home}/docker-compose.yml'
dc_env = {}


def track(message, extra={}):
    try:
        extra['version'] = version
        mp.track(str(data['user']['id']), message, extra)
    except Exception:
        # ignore issues with tracking
        pass


def write(content, location):
    dir = os.path.dirname(location)
    if dir and not os.path.exists(dir):
        os.makedirs(dir)

    if isinstance(content, (list, dict)):
        content = json.dumps(content, indent=2)

    with open(location, 'w+') as file:
        file.write(content)


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


def running(exit=True):
    cmd = 'ps -q | xargs docker inspect -f "{{ .State.ExitCode }}"'
    services = run(cmd).stdout.decode('utf-8').splitlines()
    if services and len(services) == services.count('0'):
        return True

    if exit:
        click.echo('Asyncy is not running. Start the stack with ', nl=False)
        click.echo(click.style('`asyncy start`', fg='magenta'))
        sys.exit(1)
    else:
        return False


def init():
    global data
    if os.path.exists(f'{home}/data.json'):
        with open(f'{home}/data.json', 'r') as file:
            data = json.load(file)
            data.setdefault('configuration', {})
            sentry.user_context({
                'id': data['user']['id'],
                'email': data['user']['email']
            })


def save():
    click.echo(click.style('Updating application...', bold=True), nl=False)
    with click_spinner.spinner():
        # save configuration
        write(data, f'{home}/data.json')
        write(json.dumps(data['configuration']), f'{home}/tmp_config.json')
        # save environment to engine
        run(f'cp {home}/tmp_config.json asyncy_engine_1:'
            f'/asyncy/config/environment.json', compose=False)

        # restart engine
        run(f'restart engine')
    click.echo('Done.')


def stream(cmd):
    process = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == b'' and process.poll() is not None:
            break
        if output:
            click.echo(output.strip())


def run(command, compose=True, raw=False):
    """
    docker-compose alias
    """
    # fat_env - we need this as there could be docker variables
    # in the OS's environment.
    fat_env = {**dict(os.environ), **data['environment']}

    docker = 'docker'
    if compose:
        docker = dc

    if not raw:
        command = f'{docker} {command}'

    return subprocess.run(
        command,
        shell=True, stdout=subprocess.PIPE, check=True, env=fat_env)


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
    Hello! Welcome to Λsyncy Alpha

    We hope you enjoy and we look forward to your feedback.

    Documentation: https://docs.asyncy.com
    """
    init()
