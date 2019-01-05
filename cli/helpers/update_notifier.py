import pkg_resources

import requests
from texttable import Texttable


def get_latest_version(name):
    url = 'https://pypi.python.org/pypi/{}/json'.format(name)
    return requests.get(url).json()['info']['version']


def notify(name):
    """
    notify of about the new available cli version.
    """
    current_version = pkg_resources.get_distribution(name).version
    latest_version = get_latest_version(name)

    if(current_version != latest_version):
        table = Texttable()
        table.set_cols_align(['c'])
        table.add_rows([
            ['Update available {} --> {}'
             .format(current_version, latest_version)],
            ['Run "pip install {} -U" to update'.format(
                name)]])
        print(table.draw())
