# -*- coding: utf-8 -*-

import os
import sys
from json import dumps
import click
import requests

from . import cli


graphql_endpoint = os.getenv(
    'ASYNCY_GRAPHQL',
    'https://api.asyncy.com/graphql'
)


def graphql(query, **variables):
    res = requests.post(
        graphql_endpoint,
        data=dumps({
            'query': query,
            'variables': variables
        }),
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {cli.data["access_token"]}'
        }
    )
    data = res.json()
    if 'errors' in data:
        for error in data['errors']:
            click.echo(click.style('Error: ', fg='red') + error['message'])
        sys.exit(1)
    return data


class Config:
    @staticmethod
    def get(app: str):
        res = graphql(
            """
            query($app: UUID!){
              allReleases(condition: {appUuid: $app},
                          first: 1, orderBy: ID_DESC){
                nodes{
                  config
                }
              }
            }
            """,
            app=Apps.get_uuid_from_hostname(app)
        )
        try:
            return res['data']['allReleases']['nodes'][0]['config'] or {}
        except:
            return {}

    @staticmethod
    def set(config: {}, app: str, message: str) -> dict:
        return Releases.create(config, None, app,
                               message or 'Update environment')


class Releases:
    @staticmethod
    def list(app: str, limit: int):
        res = graphql(
            """
            query($app: UUID!){
              allReleases(condition: {appUuid: $app},
                        first: 30, orderBy: ID_DESC){
                nodes{
                  id
                  message
                  timestamp
                  state
                }
              }
            }
            """,
            app=Apps.get_uuid_from_hostname(app)
        )
        try:
            return res['data']['allReleases']['nodes']
        except:
            return []

    @staticmethod
    def rollback(version: str, app: str):
        app = Apps.get_uuid_from_hostname(app)
        res = graphql(
            """
            query($app: UUID!, $version: Int!){
              releaseByAppUuidAndId( appUuid: $app, id: $version){
                config
                payload
              }
            }
            """,
            app=app,
            version=version
        )
        release = res['data']['releaseByAppUuidAndId']

        res = graphql(
            """
            mutation ($data: CreateReleaseInput!){
              createRelease(input: $data) {
                release { id }
              }
            }
            """,
            data={
                'release': {
                    'appUuid': app,
                    'message': f'Rollback to v{version}',
                    'config': release['config'] or {},
                    'payload': release['payload'],
                    'ownerUuid': cli.data['id']
                }
            }
        )
        return res['data']['createRelease']['release']

    @staticmethod
    def get(app: str):
        res = graphql(
            """
            query($app: UUID!){
              allReleases(condition: {appUuid: $app},
                          first: 1, orderBy: ID_DESC){
                nodes{
                  id
                  state
                }
              }
            }
            """,
            app=Apps.get_uuid_from_hostname(app)
        )
        try:
            return res['data']['allReleases']['nodes']
        except:
            return []

    @staticmethod
    def create(config: {}, payload: {}, app: str, message: str) -> dict:
        res = graphql(
            """
            mutation ($data: CreateReleaseInput!){
              createRelease(input: $data) {
                release { id }
              }
            }
            """,
            data={
                'release': {
                    'appUuid': Apps.get_uuid_from_hostname(app),
                    'message': message or 'Deploy app',
                    'config': config,
                    'payload': payload
                }
            }
        )
        return res['data']['createRelease']['release']


class Apps:
    @staticmethod
    def get_uuid_from_hostname(app: str) -> str:
        res = graphql(
            """
            query($app: Hostname!){
              app: appDnsByHostname(hostname: $app){
                appUuid
              }
            }
            """,
            app=app
        )
        return res['data']['app']['appUuid']

    @staticmethod
    def maintenance(app: str, maintenance: bool):
        if maintenance is None:
            res = graphql(
                """
                query($app: UUID!){
                  app: appByUuid(uuid: $app){
                    maintenance
                  }
                }
                """,
                app=Apps.get_uuid_from_hostname(app)
            )
            return res['data']['app']['maintenance']
        else:
            graphql(
                """
                mutation ($data: UpdateAppByUuidInput!){
                  updateAppByUuid(input: $data){
                    app{
                      uuid
                    }
                  }
                }
                """,
                data={
                    'uuid': Apps.get_uuid_from_hostname(app),
                    'appPatch': {
                        'maintenance': maintenance
                    }
                }
            )

    @staticmethod
    def list() -> list:
        res = graphql(
            """
            query{
              allApps(condition: {deleted: false}, orderBy: NAME_ASC){
                nodes{
                  name
                  timestamp
                  maintenance
                }
              }
            }
            """
        )
        return res['data']['allApps']['nodes']

    @staticmethod
    def create(name: str, team: str) -> dict:
        res = graphql(
            """
            mutation ($data: CreateAppInput!){
              createApp(input: $data) {
                app{
                  name
                }
              }
            }
            """,
            data={
                'app': {
                    'ownerUuid': cli.data['id'],
                    'name': name
                }
            }
        )
        return res['data']['createApp']['app']

    @staticmethod
    def destroy(app: str):
        graphql(
            """
            mutation ($data: UpdateAppByUuidInput!){
              updateAppByUuid(input: $data){
                app{
                  uuid
                }
              }
            }
            """,
            data={
                'uuid': Apps.get_uuid_from_hostname(app),
                'appPatch': {
                    'deleted': True
                }
            }
        )
