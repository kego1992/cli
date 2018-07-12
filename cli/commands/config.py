# -*- coding: utf-8 -*-

import click

from cli import Cli


@Cli.Cli.command(aliases=['config:set', 'config:get', 'config:del'], hidden=True)
def config():
    """
    Manage environment variables
    """
    if Cli.data['configuration']:
        click.echo(click.style('Storyscript variables:', dim=True))
        for name, value in Cli.data['configuration'].items():
            if not isinstance(value, dict):
                click.echo(click.style(name, fg='green') + f':  {value}')

        click.echo('')
        click.echo(click.style('Service variables:', dim=True))
        for name, value in Cli.data['configuration'].items():
            if isinstance(value, dict):
                click.echo(click.style(name, bold=True))
                for name, value in value.items():
                    click.echo('  ' + click.style(name, fg='green') + f':  {value}')

    else:
        click.echo(click.style('No configuration set yet.', bold=True))
        click.echo('    Set Storyscript variables by calling ' + click.style('$ ', dim=True) + click.style('asyncy config:set key=value', fg='magenta'))
        click.echo('    Set service specific variables by calling ' + click.style('$ ', dim=True) + click.style('asyncy config:set service key=value', fg='magenta'))


@Cli.Cli.command(aliases=['config:set'], hidden=True)
@click.argument('variables', nargs=-1)
def config_set(variables):
    """
    Set one or more environment variables

        $ asyncy config:set key=value foo=bar

    To set an environment variable to a specific service use

        $ asyncy config:set twitter oauth_token=value

    """
    assert Cli.user()
    Cli.track('Set variables')
    if variables:
        for keyval in variables:
            if '=' in keyval:
                key, val = tuple(keyval.split('=', 1))
                if '.' in key:
                    parent, key = tuple(key.split('.', 1))
                    service = Cli.data['configuration'].setdefault(parent.lower(), {})
                    service[key.upper()] = val
                else:
                    Cli.data['configuration'][key.upper()] = val
                click.echo(click.style(key.upper(), fg='green') + f':  {val}')
        Cli.save()
    else:
        click.echo(config_set.__doc__.strip())


@Cli.Cli.command(aliases=['config:get'], hidden=True)
@click.argument('variables', nargs=-1)
def config_get(variables):
    """
    Get one or more environment variables
    """
    assert Cli.user()
    Cli.track('Get variables')
    if variables:
        for name in variables:
            if '.' in name:
                service, name = tuple(name.split('.', 1))
                value = Cli.data['configuration'][service.lower()].get(name.upper(), None)
            else:
                if name in Cli.data['configuration']:
                    # could be a service here
                    value = Cli.data['configuration'][name]
                else:
                    value = Cli.data['configuration'].get(name.upper(), None)

            if value:
                if isinstance(value, dict):
                    for name, value in value.items():
                        click.echo(click.style(name.upper(), fg='green') + f':  {value}')
                else:
                    click.echo(click.style(name.upper(), fg='green') + f':  {value}')
    else:
        click.echo(config_get.__doc__.strip())


@Cli.Cli.command(aliases=['config:del', 'config:delete', 'config:rm'], hidden=True)
@click.argument('variables', nargs=-1)
def config_del(variables):
    """
    Get one or more environment variables
    """
    assert Cli.user()
    Cli.track('Delete variables')
    if variables:
        for name in variables:
            if name in Cli.data['configuration']:
                # could be a service here
                Cli.data['configuration'].pop(name)
                click.echo(click.style('Removed service configuration', fg='red') + f': {name}')
            elif Cli.data['configuration'].pop(name.upper(), None):
                click.echo(click.style('Removed', fg='red') + f': {name.upper()}')
        Cli.save()
    else:
        click.echo(config_del.__doc__.strip())
