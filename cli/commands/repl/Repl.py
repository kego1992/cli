# -*- coding: utf-8 -*-

import json
import os
import re
import sys

import click
import click_spinner
import emoji
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from pygments.lexers import PythonLexer
import requests
import storyscript
from storyscript import compiler, parser

from .Scope import Scope
from ... import cli


class Repl:
    _patterns = re.compile(r'((.* as (\w+(, )?)+)|try|catch|finally)$').match

    toolbar = [
        ('class:toolbar-key', ' Shift+Tab'),
        ('class:toolbar-text', ' to end scope'),
        ('class:toolbar-key', ' /data'),
        ('class:toolbar-text', ' will show variables'),
        ('class:toolbar-key', ' /save /help /exit'),
    ]

    # https://python-prompt-toolkit.readthedocs.io/en/latest/
    def __init__(self):
        self.session = PromptSession(
            history=FileHistory(f'{cli.home}/.history')
        )
        self.auto_suggest = AutoSuggestFromHistory()
        self.compile = compiler.Compiler().compile
        self.parse = parser.Parser().parse
        self.scope = Scope()
        self.kb = self.keybinding()
        self.lexer = PygmentsLexer(PythonLexer)
        self.requests = requests.Session()
        self.style = Style.from_dict({
            'toolbar-text': '#4512ab bg:#aaaaaa',
            'toolbar-key': '#4512ab bg:#ffffff',
            'bottom-toolbar': '#4512ab bg:#4512ab',
        })
        self.story = []
        self.block = []

    def prompt_text(self):
        if len(self.scope) > 1:
            return '...' + (' ' * (len(self.scope) - 1) * 4)
        else:
            return '>>> '

    def should_indent(self, line):
        return (
            line.startswith(('if ', 'unless ', 'else if ', 'else ',
                             'when ', 'while ', 'function ')) or
            self._patterns(line)
        )

    def interact(self):
        while 1:
            user_input = self.session.prompt(
                self.prompt_text(),
                lexer=self.lexer,
                key_bindings=self.kb,
                bottom_toolbar=lambda: self.toolbar,
                style=self.style,
                auto_suggest=self.auto_suggest
            )

            if user_input == 1 or user_input == 'exit':
                break

            elif user_input == 0:
                lines = self.write_block()
                self.block = []
                self.submit(lines)

            elif user_input[0] == '/':
                getattr(self, f'command_{user_input[1:]}', self.command_none)()

            elif user_input in self.scope:
                # echo out a value
                click.echo(self.scope[user_input])

            elif self.should_indent(user_input):
                self.write_in_block(user_input)

            elif user_input != '':
                lines = self.write(user_input)
                if lines and self.block == []:
                    self.submit(lines)

    def write_block(self):
        try:
            return self.compile(self.parse('\n'.join(self.block)))

        except Exception as e:
            self.handle_exception(e)

    def write_in_block(self, user_input):
        try:
            # syntax check this line
            compiler.Compiler().compile(
                self.parse(f'{user_input.strip()}\n    a = 1\n')
            )
            # append to story
            line = f'{self.scope.indent()}{user_input}'
            self.story.append(line)
            self.block.append(line)
            # enter the scope
            self.scope.add()

        except Exception as e:
            self.handle_exception(e)

    def write(self, user_input):
        try:
            # add block to compiler
            lines = self.compile(self.parse(user_input))
            self.story.append(f'{self.scope.indent()}{user_input}')
            if self.scope:
                self.block.append(f'{self.scope.indent()}{user_input}')
            return lines

        except Exception as e:
            self.handle_exception(e)

    def handle_exception(self, exception):
        click.echo(click.style(str(exception), fg='red'))

    def submit(self, lines):
        with click_spinner.spinner():
            # TODO assert service exist in Hub
            #      the hub data should be built locally to quicker requests

            # send to engine
            res = self.requests.post(
                'http://engine.asyncy.net/interact',
                data=lines,
                timeout=10
            )
            res.raise_for_status()
            data = res.json()

        self.handle_output(data)

    def handle_output(self, data):
        """
        Handle output from the Engine
        """
        if data.get('output'):
            click.echo(data['output'])

        elif data.get('error'):
            click.echo(click.echo(data['error'], fg='red'))

        if data.get('context'):
            self.scope.update(data['context'])

    def command_exit(self):
        click.echo(emoji.emojize(':waving_hand:  Goodbye.'))
        sys.exit(0)

    def command_save(self):
        path = click.prompt(emoji.emojize('Write to'))
        self.save(path)
        sys.exit(0)

    def command_none(self):
        click.echo('Command not found')

    def command_data(self):
        click.echo(self.scope.dumps())

    def command_story(self):
        click.echo('\n'.join(self.story))

    def command_block(self):
        click.echo('\n'.join(self.block))

    def keybinding(self):
        kb = KeyBindings()

        @kb.add('s-tab')
        def kb_stab(event):
            if len(self.scope) > 1:
                self.scope.pop()
            event.app.exit(0)

        # TODO capture ctr-d events and exit safely
        @kb.add('c-d')
        def kb_cb(event):
            event.app.exit(1)

        return kb

    def save(self, filepath):
        """
        Save the stort to a file path
        """
        try:
            os.makedirs(os.path.basename(filepath))
        except Exception:
            pass

        if os.path.exists(filepath):
            assert click.confirm('Override')

        with open(filepath, 'w+') as file:
            file.write('\n'.join(self.story) + '\n')
