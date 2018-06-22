
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
dc = 'docker-compose -f .asyncy/docker-compose.yml'
VERSION = '0.0.4'


def track(message, extra={}):
    extra['version'] = VERSION
    mp.track(str(data['user']['id']), message, extra)


def write(content, location):
    dir = os.path.dirname(location)
    if not os.path.exists(dir):
        os.makedirs(dir)

    if isinstance(content, (list, dict)):
        content = json.dumps(content)

    with open(location, 'w+') as file:
        file.write(content)


def user():
    """
    Get the active user
    """
    return (data or {}).get('user')


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
    """
    👋  Hello! Welcome to Λsyncy Alpha

    We hope you enjoy and we look forward to your feedback.

    Docs: https://docs.asyncy.com/cli
    """
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
        write('.asyncy', '.gitignore')
        delegator.run('git add .gitignore && git commit -m "initial commit"')
        click.echo(click.style('√', fg='green') + ' Setup repository.')
        ctx.invoke(update)
        click.echo(cli.__doc__)

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
    track('Update CLI')
    # update compose, pull new containes
    click.echo(click.style('Updating', bold=True))

    click.echo(click.style('   ->', fg='green') + ' CLI... ', nl=False)
    with click_spinner.spinner():
        res = delegator.run('pip install -U asyncy')
        assert res.return_code == 0, res.err
    click.echo('Done')

    click.echo(click.style('   ->', fg='green') + ' docker-compose.yml... ', nl=False)
    with click_spinner.spinner():
        res = requests.get('https://raw.githubusercontent.com/asyncy/stack-compose/master/docker-compose.yml')
        write(res.text, '.asyncy/docker-compose.yml')
    click.echo('Done')

    click.echo(click.style('   ->', fg='green') + ' Pulling new services... ', nl=False)
    with click_spinner.spinner():
        delegator.run(f'{dc} pull')
        delegator.run(f'{dc} down')
    click.echo('Done')

    ctx.invoke(start)


@cli.command()
@click.pass_context
def start(ctx):
    """
    Start the Asyncy Stack
    """
    assert user()
    track('Start Stack')

    res = delegator.run(f'{dc} ps -q')
    if res.out != '':
        click.echo(click.style('Stack is running already.'))
        sys.exit(0)

    click.echo(click.style('Starting Asyncy... ', bold=True), nl=False)
    with click_spinner.spinner():
        res = delegator.run(f'{dc} up -d',
                            env=data['environment'])
    click.echo('Done')
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
    click.echo('    Your App --      ' + click.style('http://asyncy.net', fg='cyan'))
    click.echo('    Metrics --       ' + click.style('http://grafana.asyncy.net', fg='cyan') + ' user & pass = admin')
    click.echo('    Documentation -- ' + click.style('http://docs.asyncy.com', fg='cyan'))
    click.echo('    Asyncy Hub --    ' + click.style('http://hub.asyncy.com', fg='cyan'))
    click.echo('    Feedback --      ' + click.style('http://asyncy.click/feedback', fg='cyan'))


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

        # click.echo(click.style('Checking Services', bold=True))
        # click.echo('   👉  TODO')

        click.echo(click.style('√', fg='green') + ' Looking good! 🦄')


@cli.command()
@click.argument('story', default='-',
                type=click.Choice(['http', 'every', 'function',
                                   'if', 'loop', 'twitter',
                                   'slack-bot', 'subscribe',
                                   'every', 'websocket',  '-']))
def bootstrap(story):
    """
    Produce example stories as templates to work from.
    """
    assert user()
    track('Bootstrap story')
    if story != '-':
        with open(f'cli/stories/{story}.story', 'r') as file:
            click.echo(file.read())

    else:
        click.echo(click.style('Choose a template', bold=True))
        click.echo(click.style('   http', fg='cyan') + '      - serverless http endpoint')
        click.echo(click.style('   function', fg='cyan') + '  - generic function')
        click.echo(click.style('   if', fg='cyan') + '        - if/then')
        click.echo(click.style('   loop', fg='cyan') + '      - for loop')
        click.echo(click.style('   twitter', fg='cyan') + '   - stream tweets')
        click.echo('')

        click.echo(click.style('Coming soon', bold=True) + ' -- Under active development 🖖')
        click.echo(click.style('   slack-bot', fg='cyan') + ' - Slack bot')
        click.echo(click.style('   subscribe', fg='cyan') + ' - event subscriptions')
        click.echo(click.style('   every', fg='cyan') + '     - periodic run this')
        click.echo(click.style('   websocket', fg='cyan') + ' - websocket support')
        click.echo('')

        click.echo('👉  Run ' + click.style('asyncy bootsrap _template_name_', fg='magenta'))
        click.echo('')

        click.echo(click.style('More', bold=True))
        click.echo('    Examples at ' + click.style('https://github.com/topics/asyncy-example', fg='cyan'))
        click.echo('    Services at ' + click.style('https://hub.asyncy.com', fg='cyan'))
        click.echo('')


@cli.command()
@click.option('--follow', '-f', is_flag=True, help='Follow the logs')
def logs(follow):
    """
    Show compose logs
    """
    assert user()
    track('Show Logs')
    if follow:
        stream(f'{dc} logs -f')
    else:
        click.echo(delegator.run(f'{dc} logs').out)


@cli.command()
def feedback():
    """
    Give feedback
    """
    click.launch('https://asyncy.click/feedback')


@cli.command()
def version():
    """
    Show version number
    """
    click.echo(VERSION)


@cli.command()
def status():
    """
    Show stack status and health
    """
    assert user()
    track('Stack Status')
    res = delegator.run(f'{dc} ps')
    click.echo(res.out)


@cli.command()
def shutdown():
    """
    Show stack status and health
    """
    assert user()
    track('Stack Shutdown')
    stream(f'{dc} down')


@cli.command()
@click.option('--force', '-f', is_flag=True, help='Forse push')
def deploy(force):
    """
    Deploy your application. Alias for

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
    click.echo('Your http endpoints resolve to ' + click.style('http://asyncy.net', fg='cyan'))


if __name__ == '__main__':
    cli()
