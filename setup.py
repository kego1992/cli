from setuptools import find_packages, setup
from setuptools.command.install import install

classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Programming Language :: Python :: 3.6',
    'Topic :: Office/Business',
    'Topic :: Software Development :: Build Tools'
]

requirements = [
    'click==6.7',
    'click-spinner==0.1.8',
    'delegator.py==0.1.0',
    'emoji==0.5.0',
    'mixpanel==4.3.2',
    'prompt-toolkit==2.0.3',
    'Pygments==2.2.0',
    'raven==6.9.0',
    'requests==2.19.1',
    'storyscript==0.1.2'
    'click-didyoumean==0.0.3',
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
