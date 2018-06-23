from setuptools import find_packages, setup
from setuptools.command.install import install

classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Environment :: Plugins',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Programming Language :: Python :: 3.6',
    'Topic :: Office/Business',
    'Topic :: Software Development :: Build Tools',
    'Topic :: Software Development :: Compilers'
]

requirements = [
    'click',
    'requests',
    'delegator.py',
    'storyscript',
    'mixpanel',
    'click-spinner',
    'emoji',
    'raven',
    'pygments'
]

setup(name='asyncy',
      version='0.0.6',
      description='Asyncy CLI',
      long_description='',
      classifiers=classifiers,
      download_url='https://github.com/asyncy/cli/archive/master.zip',
      keywords='',
      author='Asyncy',
      author_email='noreply@asyncy.com',
      url='http://docs.asyncy.com/cli',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=requirements,
      extras_require={ },
      entry_points={
          'console_scripts': ['asyncy=cli.cli:cli']
      })
