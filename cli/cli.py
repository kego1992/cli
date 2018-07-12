import os
import sys
import json
import click
import delegator
import subprocess
from mixpanel import Mixpanel
from raven import Client
import click_spinner
from click_didyoumean import DYMGroup
from click_alias import ClickAliasedGroup

mp = Mixpanel('c207b744ee33522b9c0d363c71ff6122')
sentry = Client('https://007e7d135737487f97f5fe87d5d85b55@sentry.io/1206504')

data = None
home = os.path.expanduser('~/.asyncy')
dc = f'docker-compose -f {home}/docker-compose.yml'
dc_env = {}
VERSION = '0.0.9'


def track(message, extra={}):
    try:
        extra['version'] = VERSION
        mp.track(str(data['user']['id']), message, extra)
    except:
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
    if run('ps -q').out.strip():
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
        # save environment to engine
        run(f'''exec engine bash -c "echo '{json.dumps(data['configuration'])}' > /asyncy/config/environment.json"''')
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


def run(command):
    """
    docker-compose alias
    """
    return delegator.run(
        f'{dc} {command}',
        env=data['environment']
    )


class _cli(DYMGroup, ClickAliasedGroup):
    pass


@click.group(cls=_cli)
def Cli():
    """
    Hello! Welcome to Λsyncy Alpha

    We hope you enjoy and we look forward to your feedback.

    Docs: https://docs.asyncy.com/cli
    """
    init()
