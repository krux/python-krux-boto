# -*- coding: utf-8 -*-
#
# © 2014-2019 Salesforce.com
#

"""
Package setup for krux-boto
"""

#
# Standard libraries
#
from __future__ import absolute_import
from setuptools import setup, find_packages
from os import path
import json

# To avoid the dependency cycle, read version from a non-py file version.json.
_VERSION_PATH = path.join(path.dirname(__file__), 'version.json')
with open(_VERSION_PATH, 'r') as f:
    VERSION = json.load(f).get('VERSION')

# URL to the repository on Github.
REPO_URL = 'https://github.com/krux/python-krux-boto'
# Github will generate a tarball as long as you tag your releases, so don't
# forget to tag!
DOWNLOAD_URL = ''.join((REPO_URL, '/tarball/release/', VERSION))

setup(
    name='krux-boto',
    version=VERSION,
    author='Jos Boumans',
    author_email='jos@krux.com',
    maintainer='Peter Han',
    maintainer_email='phan@krux.com',
    description='Library for interacting with boto built on krux-stdlib',
    url=REPO_URL,
    download_url=DOWNLOAD_URL,
    license='All Rights Reserved.',
    packages=find_packages(),
    package_data={
        '': ['../version.json']
    },
    install_requires=[
        'krux-stdlib',
        'boto',
        'boto3',
        'enum34',
        'six',
    ],
    tests_require=[
        'coverage',
        'mock',
        'nose',
    ],
    entry_points={
        'console_scripts': [
            'krux-boto-test = krux_boto.cli:main',
        ],
    },
    test_suite='test',
    python_requires='>=2.7, <4',
)
