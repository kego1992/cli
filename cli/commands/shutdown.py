# -*- coding: utf-8 -*-

from .. import cli


@cli.cli.command()
def shutdown():
    """
    Shutdown Asyncy services
    """
    assert cli.user()
    cli.track('Stack Shutdown')
    cli.stream(f'{cli.dc} down')
