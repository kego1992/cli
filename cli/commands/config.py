# -*- coding: utf-8 -*-

import click

import click_spinner

from .. import api
from .. import cli
from .. import options


@cli.cli.command()
@options.app
def config(app):
    """
    List environment variables.

    asyncy config:get -- Get one or more variables.

    asyncy config:set -- Set one or more variables.

    asyncy config:del -- Delete one or more variables.

    """
    cli.user()

    click.echo('Fetching config... ', nl=False)
    with click_spinner.spinner():
        config = api.Config.get(app)
    click.echo(click.style('√', fg='green'))

    if config:
        click.echo(click.style('Storyscript variables:', dim=True))
        for name, value in config.items():
            if not isinstance(value, dict):
                click.echo(click.style(name, fg='green') + f':  {value}')

        click.echo('')
        click.echo(click.style('Service variables:', dim=True))
        for name, value in config.items():
            if isinstance(value, dict):
                click.echo(click.style(name, bold=True))
                for _name, _value in value.items():
                    click.echo('  ' + click.style(_name, fg='green') +
                               f':  {_value}')

    else:
        click.echo(click.style('No configuration set yet.', bold=True))
        click.echo('\nSet Storyscript environment ' +
                   click.style('$ ', dim=True) +
                   click.style('asyncy config:set key=value', fg='magenta'))
        click.echo('Set service environment ' +
                   click.style('$ ', dim=True) +
                   click.style('asyncy config:set service.key=value',
                               fg='magenta'))


@cli.cli.command(aliases=['config:set'])
@click.argument('variables', nargs=-1)
@click.option('--message', '-m', nargs=1, default=None,
              help='(optional) Message why variable(s) were created.')
@options.app
def config_set(variables, app, message):
    """
    Set one or more environment variables

        $ asyncy config:set key=value foo=bar

    To set an environment variable to a specific service use

        $ asyncy config:set twitter.oauth_token=value

    """
    cli.user()
    cli.track('Set variables')

    click.echo('Fetching config... ', nl=False)
    with click_spinner.spinner():
        config = api.Config.get(app=app)
    click.echo(click.style('√', fg='green'))

    if variables:
        for keyval in variables:
            key, val = tuple(keyval.split('=', 1))
            # TODO validate against a regexp pattern
            if '.' in key:
                service, key = tuple(key.split('.', 1))
                config.setdefault(service.lower(), {})[key.upper()] = val
            else:
                config[key.upper()] = val

            click.echo(click.style(key.upper(), fg='green') + f':  {val}')

        click.echo('\nSettting config and deploying new release... ', nl=False)
        with click_spinner.spinner():
            release = api.Config.set(config=config, app=app, message=message)
        click.echo(click.style('√', fg='green'))
        click.echo(
            f'Deployed new release... ' +
            click.style(f'v{release["id"]}', bold=True, fg='magenta')
        )

    else:
        click.echo(config_set.__doc__.strip())


@cli.cli.command(aliases=['config:get'])
@click.argument('variables', nargs=-1)
@options.app
def config_get(variables, app):
    """
    Get one or more environment variables
    """
    cli.user()
    cli.track('Get variables')
    if variables:

        click.echo('Fetching config... ', nl=False)
        with click_spinner.spinner():
            config = api.Config.get(app=app)
        click.echo(click.style('√', fg='green'))

        for name in variables:
            if '.' in name:
                service, name = tuple(name.split('.', 1))
                value = config[service.lower()].get(name.upper(), None)
            else:
                if name in config:
                    # could be a service here
                    value = config[name]
                else:
                    value = config.get(name.upper(), None)

            if value:
                if isinstance(value, dict):
                    for name, value in value.items():
                        click.echo(click.style(name.upper(), fg='green') +
                                   f':  {value}')
                else:
                    click.echo(click.style(name.upper(), fg='green') +
                               f':  {value}')
            else:
                click.echo(click.style(f'No variable named "{name.upper()}".',
                                       fg='red'))
    else:
        click.echo(config_get.__doc__.strip())


@cli.cli.command(aliases=['config:del'])
@click.argument('variables', nargs=-1)
@click.option('--message', '-m', nargs=1, default=None,
              help='(optional) Message why variable(s) were deleted.')
@options.app
def config_del(variables, app, message):
    """
    Delete one or more environment variables
    """
    cli.user()
    cli.track('Delete variables')
    if variables:

        click.echo('Fetching config... ', nl=False)
        with click_spinner.spinner():
            config = api.Config.get(app=app)
        click.echo(click.style('√', fg='green'))

        for key in variables:
            removed = False
            if key in config:
                if type(config.pop(key)) is dict:
                    click.echo(click.style('Removed service',
                                           fg='red') + f': {key}')
                else:
                    removed = True
            elif key.upper() in config:
                config.pop(key.upper())
                removed = True
            elif '.' in key:
                service, key = tuple(key.split('.', 1))
                if service in config and key.upper() in config[service]:
                    config[service].pop(key.upper())
                    removed = True

            if removed:
                click.echo(
                    click.style('Removed', fg='red') + f': {key.upper()}')

        click.echo('\nSetting config and deploying new release... ', nl=False)
        with click_spinner.spinner():
            release = api.Config.set(config=config, app=app, message=message)
        click.echo(click.style('√', fg='green'))
        click.echo(f'Deployed new release... ' +
                   click.style(f'v{release["id"]}', bold=True, fg='magenta'))

    else:
        click.echo(config_del.__doc__.strip())
