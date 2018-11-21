# -*- coding: utf-8 -*-

"""
    Copied from https://github.com/click-contrib/click-didyoumean

    Extension for the python ``click`` module to provide
    a group with a git-like *did-you-mean* feature.
"""

import difflib

import click


__version__ = '0.0.3'


class DYMMixin(object):  # pylint: disable=too-few-public-methods
    """
    Mixin class for click MultiCommand inherited classes
    to provide git-like *did-you-mean* functionality when
    a certain command is not registered.
    """
    def __init__(self, *args, **kwargs):
        self.max_suggestions = kwargs.pop('max_suggestions', 3)
        self.cutoff = kwargs.pop('cutoff', 0.5)
        super(DYMMixin, self).__init__(*args, **kwargs)

    def resolve_command(self, ctx, args):
        """
        Overrides clicks ``resolve_command`` method
        and appends *Did you mean ...* suggestions
        to the raised exception message.
        """
        try:
            return super(DYMMixin, self).resolve_command(ctx, args)
        except click.exceptions.UsageError as error:
            error_msg = str(error)
            original_cmd_name = click.utils.make_str(args[0])
            matches = difflib.get_close_matches(
                original_cmd_name,
                map(lambda c: c.replace('_', ':'),
                    self.list_commands(ctx)),
                self.max_suggestions,
                self.cutoff
            )
            if matches:
                matches = '\n    '.join(
                    map(lambda m: click.style(m, fg='magenta'), matches)
                )
                error_msg += f'\n\nDid you mean one of these?\n    {matches}'

            raise click.exceptions.UsageError(error_msg, error.ctx)


class DYMGroup(DYMMixin, click.Group):
    """
    click Group to provide git-like
    *did-you-mean* functionality when a certain
    command is not found in the group.
    """


class DYMCommandCollection(DYMMixin, click.CommandCollection):
    """
    click CommandCollection to provide git-like
    *did-you-mean* functionality when a certain
    command is not found in the group.
    """
