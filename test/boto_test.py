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

import krux.cli
import krux_boto.boto
from krux.logging import get_logger
from krux_boto.boto import Boto, add_boto_cli_arguments, ACCESS_KEY, SECRET_KEY


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

    def test_cli_region(self):
        region = 'us-west-2'
        self.boto = Boto(parser=self._get_parser(['--boto-region', region]))

        self.assertEqual(region, self.boto.cli_region)

    def test_credential_logging_success(self):
        mock_logger = MagicMock(spec=Logger, autospec=True)

        credential_map = {
            ACCESS_KEY: os.environ.get(ACCESS_KEY),
            SECRET_KEY: os.environ.get(SECRET_KEY),
        }

        with patch.dict('krux_boto.boto.os.environ', {}):
            self.boto = Boto(
                logger=mock_logger,
                parser=self._get_parser([
                    '--boto-access-key', credential_map[ACCESS_KEY],
                    '--boto-secret-key', credential_map[SECRET_KEY],
                ]),
            )

            self.assertIn(ACCESS_KEY, krux_boto.boto.os.environ)
            self.assertEqual(credential_map[ACCESS_KEY], krux_boto.boto.os.environ[ACCESS_KEY])
            self.assertIn(SECRET_KEY, krux_boto.boto.os.environ)
            self.assertEqual(credential_map[SECRET_KEY], krux_boto.boto.os.environ[SECRET_KEY])

        for key, val in credential_map.iteritems():
            obsc = val[0:3] + '[...]' + val[-3:]
            mock_logger.debug.assert_any_call('Setting boto credential %s to %s', key, obsc)
            mock_logger.info.assert_not_called(
                'Boto environment credential %s NOT explicitly set -- boto will look for a .boto file somewhere',
                key,
            )

    def test_credential_logging_empty(self):
        mock_logger = MagicMock(spec=Logger, autospec=True)

        credential_map = {
            ACCESS_KEY: '',
            SECRET_KEY: '',
        }

        with patch.dict('krux_boto.boto.os.environ', {}):
            self.boto = Boto(
                logger=mock_logger,
                parser=self._get_parser([
                    '--boto-access-key', credential_map[ACCESS_KEY],
                    '--boto-secret-key', credential_map[SECRET_KEY],
                ]),
            )

            self.assertIn(ACCESS_KEY, krux_boto.boto.os.environ)
            self.assertEqual(credential_map[ACCESS_KEY], krux_boto.boto.os.environ[ACCESS_KEY])
            self.assertIn(SECRET_KEY, krux_boto.boto.os.environ)
            self.assertEqual(credential_map[SECRET_KEY], krux_boto.boto.os.environ[SECRET_KEY])

        for key, val in credential_map.iteritems():
            mock_logger.debug.assert_any_call('Setting boto credential %s to %s', key, '<empty>')
            mock_logger.info.assert_any_call(
                'Boto environment credential %s NOT explicitly set -- boto will look for a .boto file somewhere',
                key,
            )

    def test_logging_level(self):
        self.boto = Boto(
            parser=self._get_parser(['--boto-log-level', 'info'])
        )

        self.assertEqual(INFO, get_logger('boto').getEffectiveLevel())
