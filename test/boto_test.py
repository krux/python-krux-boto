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

    def _get_parser(self, args=[]):
        # Get the argparse namespace object with the given args
        parser = krux.cli.get_parser()
        add_boto_cli_arguments(parser)
        namespace = parser.parse_args(args)

        # Return a mock ArgumentParser object as a parser
        # It has a function called 'parse_args' with the return value is the namespace variable defined above
        return MagicMock(
            spec=ArgumentParser,
            parse_args=MagicMock(return_value=namespace)
        )

    def setUp(self):
        self.boto = Boto(parser=self._get_parser())

    def test_get_region(self):
        self.assertIsNotNone(self.boto.cli_region)
