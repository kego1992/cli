# -*- coding: utf-8 -*-

import click

import requests

from .. import cli
from .. import options


@cli.cli.command()
@click.option('--follow', '-f', is_flag=True, help='Follow the logs')
@options.app
def logs(follow, app):
    """
    Show application logs
    """
    click.echo('Sorry, command not programmed yet.')
    #
    # cli.user()
    # cli.track('Show Logs')
    # # TODO pygments the log output
    # if follow:
    #     try:
    #         import asyncio
    #         import websockets
    #
    #         url = (
    #             f'wss://{logs_endpoint}/logs/stream'
    #             f'?app={app}&token={cli.data["user"]["token"]}'
    #         )
    #
    #         async def runner():
    #             async with websockets.connect(url) as ws:
    #                 click.echo(await ws.recv())
    #
    #         asyncio.get_event_loop().run_until_complete(runner())
    #
    #     except KeyboardInterrupt:
    #         pass
    # else:
    #     url = (
    #         f'https://{logs_endpoint}/logs'
    #         f'?app={app}&token={cli.data["user"]["token"]}'
    #     )
    #     r = requests.get(url)
    #     click.echo(r.text)
