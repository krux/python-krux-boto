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

#
# Third party libraries
#

import boto
from mock import MagicMock, patch

#
# Internal libraries
#

from krux_boto import get_instance_region, Error
from krux_boto.util import RegionCode, Region, RegionToCode


class UtilTest(unittest.TestCase):

    def test_get_instance_region_success(self):
        """
        get_instance_region successfully return the region
        """
        # Mocking the logger to check for calls later
        mock_logger = MagicMock(spec=Logger, autospec=True)
        # Mocking the metadata returned by boto
        mock_metadata = {
            'placement': {
                'availability-zone': 'us-east-1a',
            },
        }

        # get_logger function returns the mocked logger
        with patch('krux_boto.util.get_logger', return_value=mock_logger):
            # get_instance_metadata returns a mock dictionary created above
            with patch('krux_boto.util.boto.utils.get_instance_metadata', return_value=mock_metadata):
                self.assertEquals('us-east-1', get_instance_region())

        # Verify no warning is thrown
        self.assertTrue(('get_instance_region failed to get the local instance region') not in mock_logger.warn.call_args_list)

    def test_get_instance_region_failure(self):
        """
        get_instance_region fails when no region is returned
        """
        # Mocking the logger to check for calls later
        mock_logger = MagicMock(spec=Logger, autospec=True)
        # Mocking the metadata returned by boto
        mock_metadata = {}

        # get_logger function returns the mocked logger
        with patch('krux_boto.util.get_logger', return_value=mock_logger):
            # get_instance_metadata returns a mock dictionary created above
            with patch('krux_boto.util.boto.utils.get_instance_metadata', return_value=mock_metadata):
                # Verify an error is thrown
                with self.assertRaises(Error):
                    get_instance_region()

        # Verify a warning is thrown
        mock_logger.warn.assert_called_once_with('get_instance_region failed to get the local instance region')


class RegionCodeTest(unittest.TestCase):
    REGIONS = {
        RegionCode.ASH: Region.us_east_1,
        RegionCode.PDX: Region.us_west_2,
        RegionCode.DUB: Region.eu_west_1,
        RegionCode.SIN: Region.ap_southeast_1,
        Region.us_east_1: RegionCode.ASH,
        Region.us_west_2: RegionCode.PDX,
        Region.eu_west_1: RegionCode.DUB,
        Region.ap_southeast_1: RegionCode.SIN,
    }

    def test_iter(self):
        """
        RegionToCode.__iter__() is correctly set up and iterates through the dictionary.
        """
        for key, value in RegionToCode.iteritems():
            self.assertEquals(self.REGIONS[key], value)

    def test_len(self):
        """
        RegionToCode.__len__() is correctly set up and returns the length the dictionary.
        """
        self.assertEquals(len(self.REGIONS), len(RegionToCode))

    def test_get_by_code(self):
        """
        Region can be correctly retrieved from Code using RegionToCode.
        """
        for code in list(RegionCode):
            self.assertEquals(self.REGIONS[code], RegionToCode[code])

    def test_get_by_region(self):
        """
        Code can be correctly retrieved from Region using RegionToCode.
        """
        for reg in list(Region):
            self.assertEquals(self.REGIONS[reg], RegionToCode[reg])

    def test_get_by_code_str(self):
        """
        Region can be correctly retrieved from Code string using RegionToCode.
        """
        for code in list(RegionCode):
            self.assertEquals(self.REGIONS[code], RegionToCode[code.name])

    def test_get_by_code_str_lower(self):
        """
        Region can be correctly retrieved from Code string using RegionToCode, regardless of the case
        """
        for code in list(RegionCode):
            self.assertEquals(self.REGIONS[code], RegionToCode[code.name.lower()])

    def test_get_by_region_str(self):
        """
        Code can be correctly retrieved from Region string using RegionToCode.
        """
        for reg in list(Region):
            self.assertEquals(self.REGIONS[reg], RegionToCode[reg.name])

    def test_get_by_region_str_uppder(self):
        """
        Code can be correctly retrieved from Region string using RegionToCode, regardless of the case
        """
        for reg in list(Region):
            self.assertEquals(self.REGIONS[reg], RegionToCode[reg.name.upper()])

    def test_get_by_region_name(self):
        """
        Code can be correctly retrieved from Region string with dashes using RegionToCode.
        """
        for reg in list(Region):
            reg_str = reg.name.replace('_', '-')

            self.assertEquals(self.REGIONS[reg], RegionToCode[reg_str])

    def test_get_error(self):
        """
        Given an invalid key, RegionToCode throws error
        """
        fake_key = 'foobar'
        with self.assertRaises(KeyError) as e:
            RegionToCode[fake_key]

        self.assertEquals("'{0}'".format(fake_key), str(e.exception))
