# -*- coding: utf-8 -*-

import click

from .. import cli


@cli.cli.command()
def login():
    cli.user()
    click.echo(
        'You are logged in as ' +
        click.style(cli.data['user']['email'], fg='cyan')
    )
