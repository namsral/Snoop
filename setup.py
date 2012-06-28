#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'A daemon to track iPhones on a WiFi network',
    'license': 'MIT',
    'author': 'Lars Wiegman',
    'url': 'http://github.com/namsral/snoop',
    'author_email': 'lars+snoop@namsral.com',
    'version': '0.1',
    'install_requires': ['tornado>=2.0'],
    'packages': ['snoop'],
    'name': 'snoop',
    'entry_points': {
        'console_scripts': [
            'snoop = snoop.app:main',
            ],
        },
}

setup(**config)