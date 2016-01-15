# -*- coding: utf-8 -*-
#
# © 2015 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
import unittest

#
# Third party libraries
#

import boto
from argparse import ArgumentParser
from mock import MagicMock, patch

#
# Internal libraries
#

import krux.cli
import krux.logging
from krux_boto import Boto, add_boto_cli_arguments


class BotoTest(unittest.TestCase):

    parser_patcher = None

    def _setup_parser(self, args=[]):
        # Get the argparse namespace object with the given args
        parser = krux.cli.get_parser()
        add_boto_cli_arguments(parser)
        namespace = parser.parse_args(args)

        # If there is an existing patch, close it
        if self.parser_patcher is not None:
            self.parser_patcher.stop()
            self.parser_patcher = None

        # Patch the krux_boto.boto.get_parser function to return an ArgumentParser always
        # GOTCHA: Because get_parser is globally imported into krux_boto.boto, this is the path
        self.parser_patcher = patch(
            target='krux_boto.boto.get_parser',
            spec=ArgumentParser,
            # The return value of the get_parser function has a function called 'parse_args'
            # The return value of the parse_args is the namespace variable defined above
            return_value=MagicMock(parse_args=MagicMock(return_value=namespace))
        )
        mock_parser = self.parser_patcher.start()

    def setUp(self):
        parser = self._setup_parser()
        self.boto = Boto(parser=parser)

    def tearDown(self):
        self.parser_patcher.stop()
        self.parser_patcher = None

    def test_get_region(self):
        self.assertIsNotNone(self.boto.cli_region)
