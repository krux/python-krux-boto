# -*- coding: utf-8 -*-
#
# © 2015 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
import unittest
import os
from logging import Logger, INFO

#
# Third party libraries
#

import boto
from argparse import ArgumentParser
from mock import MagicMock, patch

#
# Internal libraries
#

import krux_boto.boto
import krux.cli
import krux.logging
from krux_boto.boto import Boto, add_boto_cli_arguments, ACCESS_KEY, SECRET_KEY


class BotoTest(unittest.TestCase):

    def test_cli_region(self):
        """
        --boto-region arguments sets boto.cli_region variable correctly
        """
        region = 'us-west-2'
        self.boto = Boto(
            region=region,
        )

        self.assertEqual(region, self.boto.cli_region)

    def test_credential_logging_success(self):
        """
        --boto-access-key and --boto-secret-key sets corresponding environment variables correctly
        """
        # Mocking the logger to check for calls later
        mock_logger = MagicMock(spec=Logger, autospec=True)

        credential_map = {
            ACCESS_KEY: 'ABCDEFGHI',
            SECRET_KEY: '1A2B3C4D5E6F7G8H9I0',
        }

        # Mocking the os.environ dictionary as an empty dictionary
        with patch.dict('krux_boto.boto.os.environ', clear=True):
            self.boto = Boto(
                access_key=credential_map[ACCESS_KEY],
                secret_key=credential_map[SECRET_KEY],
                logger=mock_logger,
            )

            # Check the passed boto credentials are correctly set in the mocked os.environ dictionary
            self.assertIn(ACCESS_KEY, krux_boto.boto.os.environ)
            self.assertEqual(credential_map[ACCESS_KEY], krux_boto.boto.os.environ[ACCESS_KEY])
            self.assertIn(SECRET_KEY, krux_boto.boto.os.environ)
            self.assertEqual(credential_map[SECRET_KEY], krux_boto.boto.os.environ[SECRET_KEY])

        # Verify logging
        for key, val in credential_map.iteritems():
            mock_logger.debug.assert_not_called(
                'Passed boto credentials is empty. Falling back to environment variable %s',
                key,
            )
            obsc = val[0:3] + '[...]' + val[-3:]
            mock_logger.debug.assert_any_call('Setting boto credential %s to %s', key, obsc)
            mock_logger.info.assert_not_called(
                'Boto environment credential %s NOT explicitly set -- boto will look for a .boto file somewhere',
                key,
            )

    def test_credential_logging_empty(self):
        """
        Boto handles invalid --boto-access-key and --boto-secret-key values
        """
        # Mocking the logger to check for calls later
        mock_logger = MagicMock(spec=Logger, autospec=True)

        credential_map = {
            ACCESS_KEY: None,
            SECRET_KEY: None,
        }

        # Mocking the os.environ dictionary as an empty dictionary
        with patch.dict('krux_boto.boto.os.environ', clear=True):
            print krux_boto.boto.os.environ
            self.boto = Boto(
                access_key=credential_map[ACCESS_KEY],
                secret_key=credential_map[SECRET_KEY],
                logger=mock_logger,
            )

            # Check the passed boto credentials are correctly set in the mocked os.environ dictionary
            self.assertNotIn(ACCESS_KEY, krux_boto.boto.os.environ)
            self.assertNotIn(SECRET_KEY, krux_boto.boto.os.environ)

        # Verify the warning is logged
        for key, val in credential_map.iteritems():
            print mock_logger.debug.call_args_list
            mock_logger.debug.assert_any_call('Passed boto credentials is empty. Falling back to environment variable %s', key)
            mock_logger.debug.assert_not_called('Setting boto credential %s to %s', key, '<empty>')
            mock_logger.info.assert_any_call(
                'Boto environment credential %s NOT explicitly set -- boto will look for a .boto file somewhere',
                key,
            )

    def test_logging_level(self):
        """
        --boto-log-level arguments sets the log level for boto correctly
        """
        self.boto = Boto(
            log_level='info',
        )

        self.assertEqual(INFO, krux.logging.get_logger('boto').getEffectiveLevel())

    def test_get_attr_property(self):
        """
        Boto properties are accessible directly via krux_boto
        """
        # Mocking the logger to check for calls later
        mock_logger = MagicMock(spec=Logger, autospec=True)

        self.boto = Boto(
            logger=mock_logger,
        )

        # GOTCHA: Reset the logger to check only the property calling code, not the constructor
        mock_logger.debug.reset_mock()

        # Verify a property is returned
        # GOTCHA: ec2 property is arbitrarily chosen. Any property is sufficient to test
        self.assertEqual(boto.ec2, self.boto.ec2)

        # Verify logging
        mock_logger.debug.assert_called_once_with('Calling wrapped boto attribute: %s', 'ec2')
        mock_logger.debug.assert_not_called("Boto attribute '%s' is callable", 'connect_ec2')

    def test_get_attr_function(self):
        """
        Boto functions are accessible directly via krux_boto
        """
        # Mocking the logger to check for calls later
        mock_logger = MagicMock(spec=Logger, autospec=True)

        self.boto = Boto(
            logger=mock_logger,
        )

        # Verify a function can be called directly from krux_boto and returns the correct value
        # GOTCHA: connect_ec2 function is arbitrarily chosen. Any function is sufficient to test
        self.assertIsInstance(self.boto.connect_ec2(), boto.ec2.EC2Connection)

        # Verify logging
        mock_logger.debug.assert_any_call('Calling wrapped boto attribute: %s', 'connect_ec2')
        mock_logger.debug.assert_any_call("Boto attribute '%s' is callable", boto.connect_ec2)
