# -*- coding: utf-8 -*-

import click
import click_spinner
import re
import emoji
import json
import storyscript
from storyscript import compiler, parser
import requests
import sys
from pygments.lexers import PythonLexer
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.history import FileHistory
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML

from .. import cli


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


welcome = (
    click.style('Λsyncy', fg='magenta') + ' ' +
    click.style(cli.VERSION, dim=True) + ' // ' +
    click.style('Storyscript', fg='cyan') + ' ' +
    click.style(storyscript.version, dim=True)
)


def save(filepath, story):
    """
    Save the stort to a file path
    """
    try:
        os.makedirs(os.path.basename(filepath))
    except:
        pass

    if os.path.exists(filepath):
        assert click.confirm('Override')

    with open(filepath, 'w+') as file:
        file.write('\n'.join(story) + '\n')


@cli.Cli.command()
def interact():
    """
    Write Storyscript interactively
    """
    assert cli.user()
    assert cli.running()

    session = PromptSession(history=FileHistory(f'{cli.home}/.history'))
    auto_suggest = AutoSuggestFromHistory()
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
            ('class:toolbar-text', ' to end scope'),
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
    click.echo(welcome)
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
                click.echo(emoji.emojize(':waving_hand:  Goodbye.'))
                sys.exit(0)

            elif user_input == '':
                # empty new line
                continue

            elif user_input in ('/exit', 'exit'):
                click.echo(emoji.emojize(':waving_hand:  Goodbye.'))
                sys.exit(0)

            elif user_input == '/save':
                filepath = click.prompt(emoji.emojize('Write to'))
                save(filepath)
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
