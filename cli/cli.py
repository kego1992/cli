# -*- coding: utf-8 -*-

import json
import os
import subprocess
import sys
import time
from urllib.parse import urlencode
from uuid import uuid4

import click

from click_alias import ClickAliasedGroup

import click_help_colors

import click_spinner

import emoji

from raven import Client

import requests

from .helpers.didyoumean import DYMGroup
from .helpers.update_notifier import notify
from .version import version


if not os.getenv('TOXENV'):
    enable_reporting = True
    sentry = Client(
        'https://007e7d135737487f97f5fe87d5d85b55@sentry.io/1206504'
    )
else:
    enable_reporting = False
    sentry = Client()

data = None
home = os.path.expanduser('~/.asyncy')


def get_access_token():
    return data['access_token']


def track(event_name, extra: dict = None):
    try:
        if extra is None:
            extra = {}

        extra['CLI version'] = version

        if enable_reporting:
            requests.post('https://stories.asyncyapp.com/track/event', json={
                'id': str(data['id']),
                'event_name': event_name,
                'event_props': extra
            })
    except Exception:
        # ignore issues with tracking
        pass


def find_asyncy_yml():
    current_dir = os.getcwd()
    while True:
        if os.path.exists(f'{current_dir}{os.path.sep}asyncy.yml'):
            return f'{current_dir}/asyncy.yml'
        elif current_dir == os.path.dirname(current_dir):
            break
        else:
            current_dir = os.path.dirname(current_dir)

    return None


def get_app_name() -> str:
    file = find_asyncy_yml()
    assert file is not None
    import yaml
    with open(file, 'r') as s:
        return yaml.load(s).pop('app_name')


def write(content: str, location: str):
    dir = os.path.dirname(location)
    if dir and not os.path.exists(dir):
        os.makedirs(dir)

    if isinstance(content, (list, dict)):
        content = json.dumps(content, indent=2)

    with open(location, 'w+') as file:
        file.write(content)


def user() -> dict:
    """
    Get the active user
    """
    global data

    if data:
        return data

    else:
        click.echo(
            'Hi! Thank you for using ' +
            click.style('Asyncy', fg='magenta') + '.'
        )
        click.echo('Please login with GitHub to get started.')

        state = uuid4()

        query = {
            'state': state
        }

        url = f'https://stories.asyncyapp.com/github?{urlencode(query)}'

        click.launch(url)
        click.echo()
        click.echo('Visit this link if your browser '
                   'doesn\'t open automatically:')
        click.echo(url)
        click.echo()

        with click_spinner.spinner():
            while True:
                try:
                    url = 'https://stories.asyncyapp.com/github/oauth_callback'
                    res = requests.get(f'{url}?state={state}')

                    if res.text == 'null':
                        raise IOError()

                    res.raise_for_status()
                    write(res.text, f'{home}/.config')
                    init()
                    break
                except IOError:
                    time.sleep(0.5)
                    # just try again
                    pass
                except KeyboardInterrupt:
                    click.echo('Login failed. Please try again.')
                    sys.exit(1)
        click.echo(
            emoji.emojize(':waving_hand:') +
            f'  Welcome {data["name"]}!'
        )
        click.echo()
        click.echo('Create a new app with:')
        print_command('asyncy apps:create')

        click.echo()

        click.echo('To list all your apps:')
        print_command('asyncy apps')

        click.echo()
        track('Login Completed')
        try:
            if enable_reporting:
                requests.post(
                    'https://stories.asyncyapp.com/track/profile',
                    json={
                        'id': str(data['id']),
                        'profile': {
                            'Name': data['name'],
                            'Email': data.get('email'),
                            'GitHub Username': data.get('username'),
                            'Timezone': time.tzname[time.daylight]
                        }
                    })
        except:
            # Ignore tracking errors
            pass
        return data


def print_command(command):
    click.echo(click.style(f'$ {command}', fg='magenta'))


def assert_project():
    try:
        name = get_app_name()
        if not name:
            raise Exception()
    except:
        click.echo(click.style('No Asyncy application found.', fg='red'))
        click.echo()
        click.echo('Create an application with:')
        print_command('asyncy apps:create')
        sys.exit(1)


def init():
    global data
    if os.path.exists(f'{home}/.config'):
        with open(f'{home}/.config', 'r') as file:
            data = json.load(file)
            sentry.user_context({
                'id': data['id'],
                'email': data['email']
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

    def format_commands(self, ctx, formatter):
        rows = []
        for sub_command in self.list_commands(ctx):
            cmd = self.get_command(ctx, sub_command)
            if cmd is None:
                continue
            if hasattr(cmd, 'hidden') and cmd.hidden:
                continue
            if sub_command in self._commands:
                aliases = ','.join(sorted(self._commands[sub_command]))
                if ':' in aliases:
                    sub_command = f'  {aliases}'
                else:
                    sub_command = aliases
            cmd_help = cmd.short_help or ''
            rows.append((sub_command, cmd_help))
        if rows:
            with formatter.section('Commands'):
                formatter.write_dl(rows)


@click.group(cls=Cli,
             help_headers_color='yellow',
             help_options_color='magenta')
def cli():
    """
    Hello! Welcome to Asyncy

    We hope you enjoy and we look forward to your feedback.

    Documentation: https://docs.asyncy.com
    """
    init()


@cli.resultcallback()
def process_result(result):
    return notify('asyncy')
