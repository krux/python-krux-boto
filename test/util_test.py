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
from mock import MagicMock, patch

#
# Internal libraries
#

from krux_boto import get_instance_region, Error


class UtilTest(unittest.TestCase):

    def test_get_instance_region_success(self):
        """
        get_instance_region successfully return the region
        """
        # Mocking the logger to check for calls later
        mock_logger = MagicMock(spec=Logger, autospec=True)
        # Mocking the metadata returned by boto
        mockock_metadata = {
            'placement': {
                'availability-zone': 'us-east-1a',
            },
        }

        # get_logger function returns the mocked logger
        with patch('krux_boto.util.get_logger', return_value=mock_logger):
            # get_instance_metadata returns a mock dictionary created above
            with patch('krux_boto.util.boto.utils.get_instance_metadata', return_value=mockock_metadata):
                self.assertEquals('us-east-1', get_instance_region())

        # Verify no warning is thrown
        mock_logger.warn.assert_not_called('get_instance_region failed to get the local instance region')

    def test_get_instance_region_failure(self):
        """
        get_instance_region fails when no region is returned
        """
        # Mocking the logger to check for calls later
        mock_logger = MagicMock(spec=Logger, autospec=True)
        # Mocking the metadata returned by boto
        mockock_metadata = {}

        # get_logger function returns the mocked logger
        with patch('krux_boto.util.get_logger', return_value=mock_logger):
            # get_instance_metadata returns a mock dictionary created above
            with patch('krux_boto.util.boto.utils.get_instance_metadata', return_value=mockock_metadata):
                # Verify an error is thrown
                with self.assertRaises(Error):
                    get_instance_region()

        # Verify a warning is thrown
        mock_logger.warn.assert_called_once_with('get_instance_region failed to get the local instance region')
