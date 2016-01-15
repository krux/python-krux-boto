# -*- coding: utf-8 -*-
#
# © 2014 Krux Digital, Inc.
#
"""
Package setup for krux-boto
"""
######################
# Standard Libraries #
######################
from __future__ import absolute_import
from setuptools import setup, find_packages

# We use the version to construct the DOWNLOAD_URL.
VERSION      = '0.0.7'

# URL to the repository on Github.
REPO_URL     = 'https://github.com/krux/python-krux-boto'
# Github will generate a tarball as long as you tag your releases, so don't
# forget to tag!
DOWNLOAD_URL = ''.join((REPO_URL, '/tarball/release/', VERSION))


setup(
    name             = 'krux-boto',
    version          = VERSION,
    author           = 'Jos Boumans',
    author_email     = 'jos@krux.com',
    description      = 'Library for interacting with boto built on krux-stdlib',
    url              = REPO_URL,
    download_url     = DOWNLOAD_URL,
    license          = 'All Rights Reserved.',
    packages         = find_packages(),
    install_requires = [
        'boto',
        'krux-stdlib',
    ],
    entry_points     = {
        'console_scripts': [
            'krux-boto-test = krux_boto.cli:main',
        ],
    },
    test_suite       = 'test',
)
