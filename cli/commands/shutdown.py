# -*- coding: utf-8 -*-

import click

from .. import cli


@cli.Cli.command()
def shutdown():
    """
    Shutdown Asyncy services
    """
    assert cli.user()
    cli.track('Stack Shutdown')
    cli.stream(f'{cli.dc} down')
