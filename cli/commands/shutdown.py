# -*- coding: utf-8 -*-

import click

from cli import Cli


@Cli.Cli.command()
def shutdown():
    """
    Shutdown Asyncy services
    """
    assert Cli.user()
    Cli.track('Stack Shutdown')
    Cli.stream(f'{dc} down')
