# -*- coding: utf-8 -*-
#
# © 2015-2016 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
import unittest
from logging import Logger, INFO

#
# Third party libraries
#

import boto
from argparse import ArgumentParser
from mock import MagicMock, patch
from six import iteritems

#
# Internal libraries
#

import krux_boto.boto
import krux.cli
import krux.logging
from krux_boto.boto import Boto, Boto3, add_boto_cli_arguments, ACCESS_KEY, SECRET_KEY, REGION, get_boto, get_boto3


class GetBotoTest(unittest.TestCase):
    FAKE_LOG_LEVEL = 'critical'
    FAKE_ACCESS_KEY = 'FAKE_ACCESS_KEY'
    FAKE_SECRET_KEY = 'FAKE_SECRET_KEY'
    FAKE_REGION = 'us-gov-west-1'  # This is a region that Krux will never use.

    _FAKE_COMMAND = [
        'krux-boto',
        '--boto-log-level', FAKE_LOG_LEVEL,
        '--boto-access-key', FAKE_ACCESS_KEY,
        '--boto-secret-key', FAKE_SECRET_KEY,
        '--boto-region', FAKE_REGION,
        '--foo',  # Adding an extra CLI argument to make sure this gets ignored without an error
    ]

    def setUp(self):
        self.args = MagicMock(
            boto_log_level=self.FAKE_LOG_LEVEL,
            boto_access_key=self.FAKE_ACCESS_KEY,
            boto_secret_key=self.FAKE_SECRET_KEY,
            boto_region=self.FAKE_REGION
        )

        self.logger = MagicMock()
        self.stats = MagicMock()

    @patch('krux_boto.boto.Boto')
    def test_get_boto_with_args(self, mock_boto):
        """
        get_boto correctly passes the arguments to Boto contructor
        """
        get_boto(self.args, self.logger, self.stats)

        mock_boto.assert_called_once_with(
            log_level=self.args.boto_log_level,
            access_key=self.args.boto_access_key,
            secret_key=self.args.boto_secret_key,
            region=self.args.boto_region,
            logger=self.logger,
            stats=self.stats,
        )

    @patch('sys.argv', _FAKE_COMMAND)
    @patch('krux_boto.boto.Boto')
    @patch('krux_boto.boto.get_logger')
    @patch('krux_boto.boto.get_stats')
    def test_get_boto_without_args(self, mock_get_stats, mock_get_logger, mock_boto):
        """
        get_boto correctly parses the CLI arguments and pass them to Boto contructor
        """
        mock_get_stats.return_value = self.stats
        mock_get_logger.return_value = self.logger

        get_boto()

        mock_boto.assert_called_once_with(
            log_level=self.args.boto_log_level,
            access_key=self.args.boto_access_key,
            secret_key=self.args.boto_secret_key,
            region=self.args.boto_region,
            logger=self.logger,
            stats=self.stats,
        )

    @patch('krux_boto.boto.Boto3')
    def test_get_boto3_with_args(self, mock_boto3):
        """
        get_boto3 correctly passes the arguments to Boto3 contructor
        """
        get_boto3(self.args, self.logger, self.stats)

        mock_boto3.assert_called_once_with(
            log_level=self.args.boto_log_level,
            access_key=self.args.boto_access_key,
            secret_key=self.args.boto_secret_key,
            region=self.args.boto_region,
            logger=self.logger,
            stats=self.stats,
        )

    @patch('sys.argv', _FAKE_COMMAND)
    @patch('krux_boto.boto.Boto3')
    @patch('krux_boto.boto.get_logger')
    @patch('krux_boto.boto.get_stats')
    def test_get_boto3_without_args(self, mock_get_stats, mock_get_logger, mock_boto3):
        """
        get_boto3 correctly parses the CLI arguments and pass them to Boto3 contructor
        """
        mock_get_stats.return_value = self.stats
        mock_get_logger.return_value = self.logger

        get_boto3()

        mock_boto3.assert_called_once_with(
            log_level=self.args.boto_log_level,
            access_key=self.args.boto_access_key,
            secret_key=self.args.boto_secret_key,
            region=self.args.boto_region,
            logger=self.logger,
            stats=self.stats,
        )


class BotoTest(unittest.TestCase):

    def test_region_no_env(self):
        """
        Region default correct if environment not set
        """
        region = 'us-west-1'
        with patch.dict('krux_boto.boto.os.environ', {}):
            self.boto = Boto()
            # Check that the region has correct default
            self.assertEqual(self.boto.cli_region, 'us-east-1')

    def test_region_no_env_cli(self):
        """
        Region CLI input works fine with no environment variable set
        """
        region = 'us-west-1'
        with patch.dict('krux_boto.boto.os.environ', {}):
            self.boto = Boto(
                region=region
            )
            #Check region can be set with command line argument with no environment variables
            self.assertEqual(self.boto.cli_region, region)

    def test_region_default(self):
        """
        --boto-region sets default region correctly
        """
        # Mocking the os.environ dictionary as an empty dictionary
        with patch.dict('krux_boto.boto.os.environ', {REGION: 'us-west-2'}):
            self.boto = Boto()
            # Check the region is correctly set in the mocked os.environ dictionary
            self.assertIn(REGION, krux_boto.boto.os.environ)
            self.assertEqual(self.boto.cli_region, krux_boto.boto.os.environ[REGION])

    def test_region_cli_input(self):
        """
        --boto-region set correctly with command line input
        """
        region = 'us-east-1'
        # Mocking the os.environ dictionary as an empty dictionary
        with patch.dict('krux_boto.boto.os.environ', {REGION: 'us-west-2'}):
            self.boto = Boto(
                region=region,
            )
            # Check the region is correctly set in the mocked os.environ dictionary
            self.assertIn(REGION, krux_boto.boto.os.environ)
            self.assertNotEqual(self.boto.cli_region, krux_boto.boto.os.environ[REGION])
            self.assertEqual(self.boto.cli_region, region)

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
        for key, val in iteritems(credential_map):
            self.assertTrue(
                ('Passed boto credentials is empty. Falling back to environment variable %s', key)
                not in mock_logger.debug.call_args_list
            )
            obsc = val[0:3] + '[...]' + val[-3:]
            mock_logger.debug.assert_any_call('Setting boto credential %s to %s', key, obsc)
            self.assertTrue(
                ('Boto environment credential %s NOT explicitly set -- boto will look for a .boto file somewhere', key)
                not in mock_logger.info.call_args_list
            )

    def test_credential_logging_empty(self):
        """
        Boto handles invalid --boto-access-key and --boto-secret-key values
        """
        # Mocking the logger to check for calls later
        mock_logger = MagicMock(spec=Logger, autospec=True)

        credential_map = {
            ACCESS_KEY: '',
            SECRET_KEY: '',
        }

        # Mocking the os.environ dictionary as an empty dictionary
        with patch.dict('krux_boto.boto.os.environ', clear=True):
            self.boto = Boto(
                access_key=credential_map[ACCESS_KEY],
                secret_key=credential_map[SECRET_KEY],
                logger=mock_logger,
            )

            # Check the passed boto credentials are correctly set in the mocked os.environ dictionary
            self.assertNotIn(ACCESS_KEY, krux_boto.boto.os.environ)
            self.assertNotIn(SECRET_KEY, krux_boto.boto.os.environ)

        # Verify the warning is logged
        for key, val in iteritems(credential_map):
            mock_logger.debug.assert_any_call('Passed boto credentials is empty. Falling back to environment variable %s', key)
            self.assertTrue(('Setting boto credential %s to %s', key, '<empty>') not in mock_logger.debug.call_args_list)
            mock_logger.info.assert_any_call(
                'Boto environment credential %s NOT explicitly set -- boto will look for a .boto file somewhere',
                key,
            )

    def test_cli_arguments_check(self):
        """
        Boto warns users correctly when CLI arguments and passed in credentials don't match.
        """
        credential_map = {
            ACCESS_KEY: {
                'CLI': 'ZYXWVUTSR',
                'ENV': 'ABCDEFGHI',
                'msg': 'boto-access-key',
            },
            SECRET_KEY: {
                'CLI': '0Z9Y8X7W6V5U4T3S2R1',
                'ENV': '1A2B3C4D5E6F7G8H9I0',
                'msg': 'boto-secret-key',
            },
        }
        # Mocking the parser to trigger the warning
        parser = krux.cli.get_parser()
        add_boto_cli_arguments(parser)
        namespace = parser.parse_args([
            '--boto-access-key', credential_map[ACCESS_KEY]['CLI'],
            '--boto-secret-key', credential_map[SECRET_KEY]['CLI'],
        ])
        mock_parser = MagicMock(
            return_value=MagicMock(
                spec=ArgumentParser,
                autospec=True,
                _action_groups=[],
                parse_known_args=MagicMock(return_value=namespace)
            )
        )

        # Mocking the logger to check for calls later
        mock_logger = MagicMock(spec=Logger, autospec=True)

        mock_env = {
            ACCESS_KEY: credential_map[ACCESS_KEY]['ENV'],
            SECRET_KEY: credential_map[SECRET_KEY]['ENV'],
        }

        with patch.dict('krux_boto.boto.os.environ', mock_env, clear=True):
            with patch('krux_boto.boto.get_parser', mock_parser):
                self.boto = Boto(
                    logger=mock_logger
                )

        for key, value in iteritems(credential_map):
            msg = 'You set %s as {0} in CLI, but passed %s to the library. ' \
                'To avoid this error, consider using get_boto() function. ' \
                'For more information, please check README.' \
                .format(value['msg'])
            cli_key = value['CLI'][0:3] + '[...]' + value['CLI'][-3:]
            env_key = value['ENV'][0:3] + '[...]' + value['ENV'][-3:]
            mock_logger.warn.assert_any_call(msg, cli_key, env_key)

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
        mock_logger.debug.assert_called_once_with('Calling wrapped boto attribute: %s on %s', 'ec2', self.boto)
        self.assertTrue(("Boto attribute '%s' is callable", 'connect_ec2') not in mock_logger.debug.call_args_list)

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
        mock_logger.debug.assert_any_call('Calling wrapped boto attribute: %s on %s', 'connect_ec2', self.boto)
        mock_logger.debug.assert_any_call("Boto attribute '%s' is callable", boto.connect_ec2)

    def test_get_attr_function_boto3(self):
        """
        Boto3 properties are accessible directly via krux_boto
        """
        # Mocking the logger to check for calls later
        mock_logger = MagicMock(spec=Logger, autospec=True)

        self.boto = Boto3(
            logger=mock_logger,
        )

        # GOTCHA: Reset the logger to check only the property calling code, not the constructor
        mock_logger.debug.reset_mock()

        # We test the stringified version, because all the classes are autogenerated
        # and assertIsIntance is not finding the class of the client. However, we want
        # to still be sure the object returned is of the class we thing it is, hence
        # the workaround.
        self.assertIn('botocore.client.EC2', str(self.boto.client('ec2')))

        # Verify logging
        mock_logger.debug.assert_any_call('Calling wrapped boto attribute: %s on %s', 'client', self.boto)
