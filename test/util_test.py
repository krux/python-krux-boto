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
        mock_logger = MagicMock(spec=Logger, autospec=True)
        mockock_metadata = {
            'placement': {
                'availability-zone': 'us-east-1a',
            },
        }

        with patch('krux_boto.util.get_logger', return_value=mock_logger):
            with patch('krux_boto.util.boto.utils.get_instance_metadata', return_value=mockock_metadata):
                self.assertEquals('us-east-1', get_instance_region())

        mock_logger.warn.assert_not_called('get_instance_region failed to get the local instance region')

    def test_get_instance_region_failure(self):
        mock_logger = MagicMock(spec=Logger, autospec=True)
        mockock_metadata = {}

        with patch('krux_boto.util.get_logger', return_value=mock_logger):
            with patch('krux_boto.util.boto.utils.get_instance_metadata', return_value=mockock_metadata):
                with self.assertRaises(Error):
                    get_instance_region()

        mock_logger.warn.assert_called_once_with('get_instance_region failed to get the local instance region')
