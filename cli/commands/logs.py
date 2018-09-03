# -*- coding: utf-8 -*-

import click

from .. import cli
from .. import options


@cli.cli.command()
@click.option('--follow', '-f', is_flag=True, help='Follow the logs')
@options.app
def logs(follow, app):
    """
    Show compose logs
    """
    cli.user()
    cli.track('Show Logs')
    # TODO pygments the log output
    if follow:
        try:
            import asyncio
            import websockets

            url = 'wss://{cli.api_endpoint}/logs/stream\
                         ?app={app}&token={cli.token}'
            async def runner():
                async with websockets.connect(url) as ws:
                    click.echo(await ws.recv())

            asyncio.get_event_loop().run_until_complete(runner())

        except KeyboardInterrupt:
            pass
    else:
        url = 'https://{cli.api_endpoint}/logs\
                       ?app={app}&token={cli.token}'
        r = requests.get(url)
        click.echo(r.text)
