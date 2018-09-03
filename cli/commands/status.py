# -*- coding: utf-8 -*-

import click
import click_spinner

from .. import cli


@cli.cli.command()
def status():
    """
    Show Asyncy status
    """
    # TODO get asyncy component
    pass
