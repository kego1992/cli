
# -*- coding: utf-8 -*-

import os
import sys
import json
import click
import requests
import delegator
from storyscript.app import App
import subprocess
from mixpanel import Mixpanel
from raven import Client
import click_spinner

mp = Mixpanel('c207b744ee33522b9c0d363c71ff6122')
sentry = Client('https://007e7d135737487f97f5fe87d5d85b55@sentry.io/1206504')
data = None


def track(message, extra={}):
    global data
    extra['version'] = 'v0.0.1'
    mp.track(str(data['user']['id']), message, extra)


def write(content, location):
    dir = os.path.dirname(location)
    if not os.path.exists(dir):
        os.makedirs(dir)

    if isinstance(content, (list, dict)):
        content = json.dumps(content)

    with open(location, 'w+') as file:
        file.write(content)


def read(path):
    path = os.path.join(os.path.dirname(__file__), path)
    with open(path, 'r') as file:
        return file.read()


def user():
    """
    Get the active user
    """
    global data
    assert data
    return data['user']


def init():
    global data
    if os.path.exists('.asyncy/data.json'):
        with open('.asyncy/data.json', 'r') as file:
            data = json.load(file)
            sentry.user_context({
                'id': data['user']['id'],
                'email': data['user']['email']
            })


def stream(cmd):
    process = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            click.echo(output.strip())


@click.group()
def cli():
    init()


@cli.command()
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
        write(res.text, '.asyncy/data.json')
        init()
        click.echo(f"👋  Welcome {data['user']['name']}.")
        track('Logged into CLI')
        delegator.run('git init')
        delegator.run('git remote add asyncy http://git.asyncy.net/alpha')
        if not os.path.exists('.asyncy/'):
            os.mkdir('.asyncy/')
        click.echo(click.style('√', fg='green') + ' Setup repository.')
        ctx.invoke(update)

    else:
        click.echo('Please signup at ' + click.style('https://asyncy.com', fg='cyan'))
        sys.exit(1)


@cli.command()
@click.pass_context
def update(ctx):
    """
    Pull new updates to the Asyncy Stack
    """
    assert user()
    track('Update Stack')
    # update compose, pull new containes
    click.echo(click.style('Updating Asyncy', bold=True))
    click.echo(click.style('   ->', fg='green') + ' Update docker-compose.yml')
    with click_spinner.spinner():
        res = requests.get('https://raw.githubusercontent.com/asyncy/stack-compose/master/docker-compose.yml')
        write(res.text, '.asyncy/docker-compose.yml')
    click.echo(click.style('   ->', fg='green') + ' Shutdown the stack')
    with click_spinner.spinner():
        delegator.run('docker-compose -f .asyncy/docker-compose.yml down')
    click.echo(click.style('   ->', fg='green') + ' Pulling new services')
    with click_spinner.spinner():
        delegator.run('docker-compose -f .asyncy/docker-compose.yml pull')
    ctx.invoke(start)


@cli.command()
@click.pass_context
def start(ctx):
    """
    Start the Asyncy Stack
    """
    assert user()
    track('Start Stack')

    res = delegator.run('docker-compose -f .asyncy/docker-compose.yml ps -q')
    if res.out != '':
        click.echo(click.style('Stack is running already.'))
        sys.exit(0)

    click.echo(click.style('Starting Asyncy', bold=True))
    with click_spinner.spinner():
        res = delegator.run('docker-compose -f .asyncy/docker-compose.yml up -d',
                            env=data['environment'])
    if res.return_code != 0:
        click.echo(res.err)
        click.echo(click.style('Error starting docker', fg='red'))
        track('Error starting stack', {'sentry': sentry.captureMessage(res.err)})
        sys.exit(1)
    else:
        click.echo(click.style('   √', fg='green') + ' Stack is up!')
        ctx.invoke(ls)


@cli.command()
def ls():
    """
    List services and user interfaces
    """
    assert user()
    track('List Services')
    click.echo(click.style('Services', bold=True))
    click.echo('    Documentation -- ' + click.style('http://docs.asyncy.com', fg='cyan'))
    click.echo('    Asyncy Hub -- ' + click.style('http://hub.asyncy.com', fg='cyan'))
    click.echo('    Your App -- ' + click.style('http://asyncy.net', fg='cyan'))
    click.echo('    Metric Dashboard -- ' + click.style('http://grafana.asyncy.net', fg='cyan'))


@cli.command()
def test():
    """
    Test the Stories
    """
    assert user()
    track('Test Stories')
    click.echo(click.style('Compiling Stories', bold=True))
    try:
        stories = App.compile(os.getcwd())
    except Exception as e:
        track('Stories failed')
        sentry.captureException()
        click.echo(click.style('X', fg='red') + ' Errors found in Storyscript.')
        click.echo(str(e))
    else:
        track('Stories passed')
        write(stories, '.asyncy/stories.json')
        stories = json.loads(application)
        if stories['stories'] == {}:
            click.echo(click.style('   X', fg='red') + ' No stories found')
            sys.exit(1)
        else:
            click.echo(click.style('   √', fg='green') + ' Stories built.')
            click.echo(click.style('   ?', fg='cyan') + ' Data found at .asyncy/stories.json')

        click.echo(click.style('Checking Services', bold=True))
        click.echo('   👉 TODO')

        click.echo(click.style('√', fg='green') + ' Looking good! 🦄')


@cli.command()
@click.argument('story', default='-',
                type=click.Choice(['http', 'every', 'function', '-']))
def bootstrap(story):
    """
    Produce example stories as templates to work from.
    """
    assert user()
    track('Bootstrap story')
    if story != '-':
        click.echo(read(f'stories/{story}.story'))
    else:
        click.echo(click.style('Choose', bold=True))
        click.echo(click.style('   http', fg='cyan') + ' - a http endpoint')
        click.echo(click.style('   function', fg='cyan') + ' - a generic function')
        click.echo(click.style('   every', fg='cyan') + ' - a periodic call')
        click.echo('')
        click.echo('Then run ' + click.style('asyncy bootsrap http', fg='magenta'))


@cli.command()
@click.option('--follow', '-f', is_flag=True, help='Follow the logs')
def logs(follow):
    """
    Show compose logs
    """
    assert user()
    track('Show Logs')
    follow = ' --follow' if follow else ''
    stream(f'docker-compose -f .asyncy/docker-compose.yml logs{follow}')


@cli.command()
def status():
    """
    Show stack status and health
    """
    assert user()
    track('Stack Status')
    res = delegator.run('docker-compose -f .asyncy/docker-compose.yml ps')
    click.echo(res.out)


@cli.command()
def shutdown():
    """
    Show stack status and health
    """
    assert user()
    track('Stack Shutdown')
    stream('docker-compose -f .asyncy/docker-compose.yml down')


@cli.command()
@click.option('--force', '-f', is_flag=True, help='Forse push')
def deploy(force):
    """
    Deploy your Story project

        git push asyncy master
    """
    assert user()
    track('Deploy App')
    if not force:
        res = delegator.run('git status -s')
        if res.out != '':
            track('Unstagged changes')
            click.echo(click.style('There are unstagged changes.', fg='red'))
            click.echo('The following files need to be commited before deploying your app.')
            click.echo(res.out.replace('?', '--'))
            click.echo(click.style('Note:', fg='cyan') + ' Asyncy runs ' +
                       click.style('git push asyncy master', fg='magenta') +
                       ' to deploy 🚀')
            sys.exit(1)

    stream('git push asyncy master')
    track('Deployed App')


if __name__ == '__main__':
    cli()
