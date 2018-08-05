# -*- coding: utf-8 -*-

"""
Produce a list of resources for the brew release.

    $ pip freeze | python scripts/brewery.py
"""

import re
import sys
import requests


resource = '''resource "{name}" do
  url "https://files.pythonhosted.org/{url}.tar.gz"
  sha256 "{sha}"
end
'''

sha_pattern = re.compile(
    r'data-clipboard-text="(\w{50,})"'
)

pkg_pattern = re.compile(
    r'<a href="https://files.pythonhosted.org/(.*).tar.gz">'
)

if __name__ == '__main__':
    for dep in sys.stdin.read().split():
        assert '==' in dep, 'Must specify exact version'
        name, version = tuple(dep.split('=='))
        res = requests.get(f'https://pypi.org/project/{name}/{version}')
        url = pkg_pattern.findall(res.text)[-1]
        sha = sha_pattern.findall(res.text)[-1]
        sys.stdout.write(resource.format(name=name, url=url, sha=sha))
