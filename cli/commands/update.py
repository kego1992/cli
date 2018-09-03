# -*- coding: utf-8 -*-

import click
import click_spinner
import requests

from .. import cli


@cli.cli.command()
def update():
    """
    Look for new version updates to CLI
    """
    pass
