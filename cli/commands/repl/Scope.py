# -*- coding: utf-8 -*-

from json import dumps


class Scope:
    def __init__(self):
        self._levels = [{}]

    def __len__(self):
        return len(self._levels)

    def __contains__(self, key):
        for c in self._levels:
            if key in c:
                return True
        return False

    def pop(self):
        self._levels.pop(0)

    def add(self):
        self._levels.insert(0, {})

    def update(self, data):
        self._levels[-1].update(data)

    def dumps(self):
        # TODO merge a list of keys
        return dumps(self._levels, indent=4)

    def __getitem__(self, key):
        for c in self._levels:
            if key in c:
                return c[key]
        raise KeyError(f'UndefinedVariable "{key}"')

    def indent(self):
        return ' ' * (4 * (len(self) - 1))
