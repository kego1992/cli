# -*- coding: utf-8 -*-

from setuptools import find_packages, setup
from setuptools.command.install import install

from cli.version import version


classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Programming Language :: Python :: 3.6',
    'Topic :: Office/Business',
    'Topic :: Software Development :: Build Tools',
]

keywords = [
    'asyncy',
    'devops',
    'devtools',
    'microservices',
    'orchestration',
    'serverless',
    'storyscript',
]

requirements = [
    'asyncio==3.4.3',
    'click-alias==0.1.1a1',
    'click-help-colors==0.4',
    'click-spinner==0.1.8',
    'click==6.7',
    'emoji==0.5.0',
    'mixpanel==4.3.2',
    'prompt-toolkit==2.0.3',
    'Pygments==2.2.0',
    'raven==6.9.0',
    'requests==2.19.1',
    'storyscript>=0.5.0',
    'websockets==6.0',
]


setup(name='asyncy',
      version=version,
      description='Asyncy CLI',
      long_description='',
      classifiers=classifiers,
      download_url='https://github.com/asyncy/cli/archive/master.zip',
      keywords=' '.join(keywords),
      author='Asyncy',
      author_email='hello@asyncy.com',
      url='http://docs.asyncy.com/cli',
      license='MIT',
      packages=find_packages(exclude=['scripts', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=requirements,
      extras_require={},
      entry_points={
          'console_scripts': ['asyncy=cli.main:cli']
      })
