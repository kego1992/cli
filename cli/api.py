# -*- coding: utf-8 -*-

import requests

from . import cli


# TODO link the commands below with GraphQL queries

class config:
    @staticmethod
    def get(app: str):
        return {
            'apple': 'orange',
            'twitter': {'oauth': 'abc'}
        }

    @staticmethod
    def set(config: {}, app: str, release: bool):
        pass

    @staticmethod
    def update(config: {}, app: str, release: bool):
        pass


class releases:
    @staticmethod
    def list(app: str, limit: int):
        return [
            {'version': '2', 'title': 'Blah blah', 'created': '5 days ago'},
            {'version': '1', 'title': 'Blah blah', 'created': '5 days ago'}
        ]

    @staticmethod
    def rollback(version: str, app: str):
        return {'version': '3'}


class apps:
    @staticmethod
    def list():
        return [
            {'name': 'smart-einstein-23', 'status': 'running', 'created': '5 days ago'}
        ]

    @staticmethod
    def create(name: str):
        return {'name': 'pink-piggie-13', 'remote': 'https://git.asyncy.com/pink-piggie-13'}

    @staticmethod
    def destroy(app: str):
        pass
