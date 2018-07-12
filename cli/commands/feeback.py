# -*- coding: utf-8 -*-

import click

from cli import Cli


@Cli.Cli.command()
def feedback():
    """
    Give feedback
    """
    click.echo('Opening https://asyncy.click/feedback')
    click.launch('https://asyncy.click/feedback')
