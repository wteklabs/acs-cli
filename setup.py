"""Packaging settings"""

from codecs import open
from os.path import abspath, dirname, join
from subprocess import call

from setuptools import Command, find_packages, setup

from acs import __version__

this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.md'), encoding='utf-8') as file:
    long_description = file.read()

class RunTests(Command):
    """Run all tests."""
    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run all tests"""
        #call(['acs', '--config-file', 'tests/test_dcos_config.ini'])
        errno = call(['py.test', '--cov=acs', '--cov-report=term-missing', '--ignore=lib/python3.5/site-packages', '--runslow', '-s'])
        raise SystemExit(errno)

setup(
    name = 'acs',
    version = __version__,
    description = 'Azure Container Service command line tools',
    long_description = long_description,
    url = "http://github.com/rgardler/acs-scripts",
    author = 'Ross Gardler',
    author_email = 'ross.gardler@microsoft.com',
    license = 'Apache License v2',
    classifiers = [
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'
    ],
    keywords = 'cli',
    packages = find_packages(exclude=['docs', 'tests*']),
    install_requires = [
        'cryptography',
        'docopt',
        'paramiko',
        'sshtunnel',
        'scp'
    ],
    extras_require = {
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    entry_points = {
        'console_scripts': [
            'acs=acs.cli:main',
        ],
    },
    cmdclass = { 'test': RunTests},
)
