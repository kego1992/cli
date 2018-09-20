# -*- coding: utf-8 -*-
import json
import os

import click
from storyscript.app import App

from cli import cli, options
from ..api import Config, Releases


@cli.cli.command(aliases=['deploy'])
@click.option('--message', is_flag=True, help='Deployment message')
@options.app
def deploy(app, message):
    config = Config.get(app)
    payload = json.loads(App.compile(os.getcwd()))
    Releases.create(config, payload, app, message)
    url = f'https://{app}.asyncyapp.com'
    click.echo(click.style('√', fg='green') +
               f' Deployed!\n'
               f'If your story listens to HTTP requests, visit {url}')
