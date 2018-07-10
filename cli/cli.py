import os
import re
import sys
import json
import click
import requests
import delegator
import storyscript
from glob import glob
import subprocess
from mixpanel import Mixpanel
from raven import Client
import click_spinner
import emoji
from click_didyoumean import DYMGroup
from os.path import expanduser

mp = Mixpanel('c207b744ee33522b9c0d363c71ff6122')
sentry = Client('https://007e7d135737487f97f5fe87d5d85b55@sentry.io/1206504')

data = None
home = expanduser('~/.asyncy')
dc = f'docker-compose -f {home}/docker-compose.yml'
dc_env = {}
VERSION = '0.0.8'


def track(message, extra={}):
    extra['version'] = VERSION
    mp.track(str(data['user']['id']), message, extra)


def write(content, location):
    dir = os.path.dirname(location)
    if dir and not os.path.exists(dir):
        os.makedirs(dir)

    if isinstance(content, (list, dict)):
        content = json.dumps(content)

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
            sentry.user_context({
                'id': data['user']['id'],
                'email': data['user']['email']
            })


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


@click.group(cls=DYMGroup)
def cli():
    """
    Hello! Welcome to Λsyncy Alpha

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
        write(res.text, f'{home}/data.json')
        init()
        click.echo(emoji.emojize(f":waving_hand:  Welcome {data['user']['name']}."))
        track('Logged into CLI')
        delegator.run('git init')
        delegator.run('git remote add asyncy http://git.asyncy.net/app')
        if not os.path.exists(home):
            os.mkdir(home)
        write('', f'{home}/.history')
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

    # Note cannot update via pip install...

    click.echo(click.style('   ->', fg='green') + ' docker-compose.yml... ', nl=False)
    with click_spinner.spinner():
        res = requests.get('https://raw.githubusercontent.com/asyncy/stack-compose/master/docker-compose.yml')
        write(res.text, f'{home}/docker-compose.yml')
    click.echo('Done')

    click.echo(click.style('   ->', fg='green') + ' Pulling new services... ')
    stream(f'{dc} pull')
    click.echo(click.style('   ->', fg='green') + ' Shutting down stack... ')
    stream(f'{dc} down')
    click.echo('Done')

    ctx.invoke(start)


@cli.command()
@click.pass_context
def restart(ctx):
    """
    Restart the stack
    """
    ctx.invoke(shutdown)
    ctx.invoke(start)


class Scope:
    def __init__(self):
        self._levels = [{'a':1}]

    def __len__(self):
        return len(self._levels)

    def __contains__(self, key):
        for c in self._levels:
            if key in c:
                return True
        return False

    def pop(self):
        self._levels.pop(0)

    def add(self):
        self._levels.insert(0, {})

    def update(self, data):
        self._levels[-1].update(data)

    def dumps(self):
        # TODO merge a list of keys
        return json.dumps(self._levels, indent=4)

    def __getitem__(self, key):
        for c in self._levels:
            if key in c:
                return c[key]
        raise KeyError(f'UndefinedVariable "{key}"')

    def indent(self):
        return ' ' * (4 * (len(self) - 1))


@cli.command()
def interact():
    """
    Write Storyscript interactively
    """
    assert user()
    assert running()
    from pygments.lexers import PythonLexer
    from prompt_toolkit.lexers import PygmentsLexer
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit import PromptSession
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.styles import Style
    from prompt_toolkit.formatted_text import HTML

    session = PromptSession(history=FileHistory(f'{home}/.history'))
    auto_suggest = AutoSuggestFromHistory()
    from storyscript import compiler, parser
    Compiler = compiler.Compiler()
    Parser = parser.Parser()

    scope = Scope()
    kb = KeyBindings()

    @kb.add('s-tab')
    def _(event):
        if len(scope) > 1:
            scope.pop()
        event.app.exit(0)

    # TODO capture ctr-d events and exit safely
    @kb.add('c-d')
    def _(event):
        event.app.exit(1)

    def bottom_toolbar():
        return [
            ('class:toolbar-key', ' Shift+Tab'),
            ('class:toolbar-text', ' will end scope'),
            ('class:toolbar-key', ' /data'),
            ('class:toolbar-text', ' will show variables'),
            ('class:toolbar-key', ' /save /help /exit'),
        ]
        return bt

    style = Style.from_dict({
        'toolbar-text': '#4512ab bg:#aaaaaa',
        'toolbar-key': '#4512ab bg:#ffffff',
        'bottom-toolbar': '#4512ab bg:#4512ab',
    })

    # https://python-prompt-toolkit.readthedocs.io/en/latest/
    click.echo(click.style('Λsyncy', fg='magenta') + f' {VERSION} -- ' + click.style('Storyscript', fg='cyan') + f' {storyscript.version}')
    click.echo(click.style('Type "/" for commands and "ctr+r" for history.', bold=True))
    lexer = PygmentsLexer(PythonLexer)
    story = []
    block = []

    _patterns = re.compile(r'((.* as (\w+(, )?)+)|try|catch|finally)$').match
    def should_indent(line):
        return (
            line.startswith(('if ', 'unless ', 'else if ', 'else ',
                             'when ', 'while ', 'function '))
            or _patterns(line)
        )

    while 1:
        try:
            if len(scope) > 1:
                text = '...' + (' ' * (len(scope) - 1) * 4)
            else:
                text = '>>> '
            user_input = session.prompt(text,
                                        lexer=lexer,
                                        key_bindings=kb,
                                        bottom_toolbar=bottom_toolbar,
                                        style=style,
                                        auto_suggest=auto_suggest)
            if user_input == 1:
                click.echo(emoji.emojize('Goodbye.'))
                sys.exit(0)

            elif user_input == '':
                # empty new line
                continue

            elif user_input == '/exit':
                sys.exit(0)

            elif user_input == '/save':
                to = click.prompt('Path')
                if os.path.exists(to):
                    assert click.confirm('Override')
                    with open(to, 'w+') as file:
                        file.write('\n'.join(story) + '\n')
                        sys.exit(0)

            elif user_input == '/data':
                click.echo(scope.dumps())
                continue

            elif user_input == '/story':
                click.echo('\n'.join(story))
                continue

            elif user_input == '/block':
                click.echo('\n'.join(block))
                continue

            elif user_input in scope:
                # echo out a value
                click.echo(scope[user_input])
                continue

            elif user_input:

                if should_indent(user_input):
                    try:
                        # syntax check this line
                        # TODO output = storyscript.loads(f'{user_input.strip()}\n    pass')
                        output = compiler.Compiler().compile(Parser.parse(f'{user_input.strip()}\n    a = 1\n'))
                        # append to story
                        story.append(f'{scope.indent()}{user_input}')
                        block.append(f'{scope.indent()}{user_input}')
                        # enter the scope
                        scope.add()

                    except Exception as e:
                        click.echo(click.style(str(e), fg='red'))
                        raise

                    # back to prompt, cannot commit until block is finished
                    continue

            try:
                # add block to compiler
                lines = Compiler.compile(Parser.parse(user_input or '\n'.join(block)))
                if user_input:
                    story.append(f'{scope.indent()}{user_input}')
                    if scope:
                        block.append(f'{scope.indent()}{user_input}')

                if user_input == 0:
                    # reset the block
                    block = []
                else:
                    continue

            except Exception as e:
                click.echo(click.style(str(e), fg='red'))
                continue

            with click_spinner.spinner():
                # TODO assert service exist in Hub
                #      the hub data should be built locally to quicker requests

                # send to engine
                res = requests.post('http://engine.asyncy.net/interact',
                                    data=lines,
                                    timeout=10)
                res.raise_for_status()
                data = res.json()

            if data.get('output'):
                click.echo(data['output'])

            elif data.get('error'):
                click.echo(click.echo(data['error'], fg='red'))

            if data.get('context'):
                scope.update(data['context'])

        except KeyboardInterrupt:
            pass


@cli.command()
@click.pass_context
def start(ctx):
    """
    Start the Asyncy Stack
    """
    assert user()
    track('Start Stack')

    if running(exit=False):
        click.echo(click.style('Stack is running already.'))
        sys.exit(0)

    click.echo(click.style('Starting Asyncy... ', bold=True), nl=False)
    with click_spinner.spinner():
        res = run('up -d')
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
        stories = storyscript.loads(os.getcwd())
    except Exception as e:
        track('Stories failed')
        sentry.captureException()
        click.echo(click.style('X', fg='red') + ' Errors found in Storyscript.')
        click.echo(str(e))
    else:
        track('Stories passed')
        write(stories, f'{home}/stories.json')
        stories = json.loads(application)
        if stories['stories'] == {}:
            click.echo(click.style('   X', fg='red') + ' No stories found')
            sys.exit(1)
        else:
            click.echo(click.style('   √', fg='green') + ' Stories built.')

        # click.echo(click.style('Checking Services', bold=True))

        click.echo(click.style('√', fg='green') + emoji.emojize(' Looking good! :thumbs_up:'))


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
        with open(os.path.join(os.path.dirname(__file__),
                               f'stories/{story}.story'), 'r') as file:
            click.echo(file.read())

    else:
        click.echo(click.style('Choose a template', bold=True))
        click.echo(click.style('   http', fg='cyan') + '      - serverless http endpoint')
        click.echo(click.style('   function', fg='cyan') + '  - generic function')
        click.echo(click.style('   if', fg='cyan') + '        - if/then')
        click.echo(click.style('   loop', fg='cyan') + '      - for loop')
        click.echo(click.style('   twitter', fg='cyan') + '   - stream tweets')
        click.echo('')

        click.echo(click.style('Coming soon', bold=True) + ' -- Under active development')
        click.echo(click.style('   slack-bot', fg='cyan') + ' - Slack bot')
        click.echo(click.style('   subscribe', fg='cyan') + ' - event subscriptions')
        click.echo(click.style('   every', fg='cyan') + '     - periodic run this')
        click.echo(click.style('   websocket', fg='cyan') + ' - websocket support')
        click.echo('')

        click.echo(emoji.emojize(':backhand_index_pointing_right:  Run ' + click.style('asyncy bootsrap _template_name_', fg='magenta')))
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
    assert running()
    track('Show Logs')
    if follow:
        stream(f'{dc} logs -f')
    else:
        click.echo(run('logs').out)


@cli.command()
def feedback():
    """
    Give feedback
    """
    click.echo('Open https://asyncy.click/feedback')
    click.launch('https://asyncy.click/feedback')


@cli.command()
def version():
    """
    Show version number
    """
    click.echo(click.style('Λsyncy', fg='magenta') + f' {VERSION}')
    click.echo(click.style('Storyscript', fg='cyan') + f' {storyscript.version}')


@cli.command()
def status():
    """
    Show stack services and health
    """
    assert user()
    assert running()
    track('Stack ps')
    click.echo(click.style('Listing Asyncy containers... ', bold=True), nl=False)
    with click_spinner.spinner():
        click.echo(run('ps').out)


@cli.command()
def shutdown():
    """
    Show stack status and health
    """
    assert user()
    track('Stack Shutdown')
    click.echo(click.style('Shutdown Asyncy... ', bold=True), nl=False)
    with click_spinner.spinner():
        run('down')
    click.echo('Done')


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
                       emoji.emojize(' to deploy :rocket:'))
            sys.exit(1)

    stream('git push asyncy master')
    track('Deployed App')
    click.echo('Your http endpoints resolve to ' + click.style('http://asyncy.net', fg='cyan'))


@cli.command()
@click.option('--pager', '-p', is_flag=True, help='Review payload only')
@click.option('--message', '-m',
              help='A short or long message about what went wrong.')
def support(pager, message):
    """
    Upload a support bundle
    """
    assert user()
    track('Support Bundle')

    if not pager and not message:
        click.echo(click.style('Tell us a little about what happened.', bold=True))
        message = click.prompt('Message')

    click.echo(click.style('Building support bundle... ', bold=True), nl=False)
    with click_spinner.spinner():

        def file(path):
            return path, json.loads(run(f'exec -T bootstrap cat {path}').out or 'null')

        def read(path):
            with open(path, 'r') as file:
                return path, file.read()

        def container(id):
            data = json.loads(delegator.run(f'docker inspect {id}').out or '[null]')[0]
            if data:
                return data['Name'], data
            else:
                return id, None

        bundle = {
            'message': message,
            'files': {
                'volume': dict(map(file, ('/asyncy/config/stories.json', '/asyncy/config/services.json', '/asyncy/config/environment.json'))),
                'stories': dict(map(read, (glob('*.story') + glob('**/*.story'))))
            },
            'logs': run('logs').out.split('\n'),
            'versions': {
                'docker': delegator.run('docker version').out.split('\n'),
                'compose': run('version').out.split('\n')
            },
            'containers': dict(map(container, run('ps -q').out.split('\n')))
        }

    click.echo('Done')

    if pager:
        from pygments import highlight
        from pygments.lexers import JsonLexer
        from pygments.formatters import TerminalFormatter
        click.echo_via_pager(highlight(json.dumps(bundle, indent=2), JsonLexer(), TerminalFormatter()))

    else:
        click.echo(click.style('Uploading support bundle... ', bold=True), nl=False)
        with click_spinner.spinner():
            sentry.captureMessage(f'Support Bundle: {message[:20]}', extra=bundle)
        click.echo('Done')


if __name__ == '__main__':
    cli()
