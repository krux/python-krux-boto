# -*- coding: utf-8 -*-
#
# © 2015 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
import unittest
from logging import Logger

#
# Third party libraries
#

import boto
from argparse import ArgumentParser
from mock import MagicMock, patch

#
# Internal libraries
#

from krux.cli import get_parser
from krux.logging import get_logger
from krux.stats import get_stats, DummyStatsClient
from krux_boto.boto import Boto, add_boto_cli_arguments, NAME
from krux_boto.cli import Application, main


class CliTest(unittest.TestCase):

    def test_init(self):
        """
        CLI constructor creates all the required private properties
        """
        self.app = Application()

        # There are not much we can test except all the objects are under the correct name
        self.assertEqual(NAME, self.app.name)
        self.assertEqual(NAME, self.app.parser.description)
        # The dummy stats client has no awareness of the name. Just check the class.
        self.assertIsInstance(self.app.stats, DummyStatsClient)
        self.assertEqual(NAME, self.app.logger.name)

        self.assertIsInstance(self.app.boto, Boto)

    def test_add_cli_arguments(self):
        """
        All the necessary arguments for krux_boto are added
        """
        self.app = Application()

        args = vars(self.app.args)

        self.assertIn('boto_access_key', args)
        self.assertIn('boto_secret_key', args)
        self.assertIn('boto_region', args)
        self.assertIn('boto_log_level', args)

    def test_main(self):
        """
        Main method runs correctly
        """
        # Mocking the logger to check for calls later
        mock_logger = MagicMock(spec=Logger, autospec=True)

        # get_logger() function returns the mocked logger from above
        with patch(
            target='krux_boto.cli.krux.cli.krux.logging.get_logger',
            return_value=mock_logger,
        ):
            main()

        # Verify the current region and all regions are logged as warning
        mock_logger.warn.assert_any_call('Connected to region: %s', 'us-east-1')
        for region in boto.connect_ec2().get_all_regions():
            mock_logger.warn.assert_any_call('Region: %s', region.name)
