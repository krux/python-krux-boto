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
        self.app = Application()

        self.assertEqual(NAME, self.app.name)
        self.assertEqual(NAME, self.app.parser.description)
        self.assertIsInstance(self.app.stats, DummyStatsClient)
        self.assertEqual(NAME, self.app.logger.name)

        self.assertIsInstance(self.app.boto, Boto)

    def test_add_cli_arguments(self):
        self.app = Application()

        args = vars(self.app.args)

        self.assertIn('boto_access_key', args)
        self.assertIn('boto_secret_key', args)
        self.assertIn('boto_region', args)
        self.assertIn('boto_log_level', args)

    def test_main(self):
        mock_logger = MagicMock(spec=Logger, autospec=True)

        with patch(
            target='krux_boto.cli.krux.cli.krux.logging.get_logger',
            return_value=mock_logger,
        ):
            main()

        mock_logger.warn.assert_any_call('Connected to region: %s', 'us-east-1')
        for region in boto.connect_ec2().get_all_regions():
            mock_logger.warn.assert_any_call('Region: %s', region.name)
