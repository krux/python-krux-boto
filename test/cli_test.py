# -*- coding: utf-8 -*-
#
# © 2015-2016 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
import unittest
from logging import Logger
import sys

#
# Third party libraries
#

from mock import MagicMock, patch, call

#
# Internal libraries
#

from krux.stats import DummyStatsClient
from krux_boto.boto import Boto, Boto3, NAME
from krux_boto.cli import Application, main
from krux.cli import get_group
from krux_boto.util import RegionCode
from krux_boto import VERSION


class CLItest(unittest.TestCase):

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
        self.assertIsInstance(self.app.boto3, Boto3)

        # Verify the version info is specified
        self.assertIn(NAME, self.app._VERSIONS)
        self.assertEqual(VERSION, self.app._VERSIONS[NAME])

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

    @patch('krux_boto.cli.krux.cli.sys.exit')
    def test_main(self, mock_exit):
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
        warn_calls = []
        warn_calls.append(call('Getting regions via boto2'))

        for region in RegionCode.Region:
            warn_calls.append(call('Region: %s - %s', RegionCode[region].name, str(region)))

        warn_calls.append(call('Getting regions via boto3'))

        for region in RegionCode.Region:
            warn_calls.append(call('Region: %s - %s', RegionCode[region].name, str(region)))

        # Verify the mock sys.exit has been called
        mock_exit.assert_called_once_with(0)

    @patch.object(sys, 'argv', ['prog', 'arg1'])
    def test_inheritance(self):
        """
        krux_boto.cli.Application can be inherited properly
        """
        app = TestApplication()

        # Check that TestApplication inherits krux_boto.cli.Application
        self.assertIsInstance(app.boto, Boto)

        # Check the test CLI argument is handled correctly
        self.assertIn('test', app.args)
        self.assertEqual('arg1', app.args.test)


class TestApplication(Application):

    def __init__(self):
        # Call to the superclass to bootstrap.
        super(TestApplication, self).__init__(name='fake-unit-test-application')

    def add_cli_arguments(self, parser):
        super(TestApplication, self).add_cli_arguments(parser)

        group = get_group(parser, self.name)

        group.add_argument(
            'test',
            type=str,
            help='Purely exists for the unit test',
        )
