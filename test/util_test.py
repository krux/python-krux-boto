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
from krux_boto.util import RegionCode


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
        RegionCode.Code.ASH: RegionCode.Region.us_east_1,
        RegionCode.Code.PDX: RegionCode.Region.us_west_2,
        RegionCode.Code.DUB: RegionCode.Region.eu_west_1,
        RegionCode.Code.SIN: RegionCode.Region.ap_southeast_1,
        RegionCode.Code.BOM: RegionCode.Region.ap_south_1,
        RegionCode.Code.SYN: RegionCode.Region.ap_southeast_2,
        RegionCode.Code.FRA: RegionCode.Region.eu_central_1,
        RegionCode.Code.NRT: RegionCode.Region.ap_northeast_1,
        RegionCode.Code.ICN: RegionCode.Region.ap_northeast_2,
        RegionCode.Code.GRU: RegionCode.Region.sa_east_1,
        RegionCode.Code.SJC: RegionCode.Region.us_west_1,
        RegionCode.Region.us_east_1: RegionCode.Code.ASH,
        RegionCode.Region.us_west_2: RegionCode.Code.PDX,
        RegionCode.Region.eu_west_1: RegionCode.Code.DUB,
        RegionCode.Region.ap_southeast_1: RegionCode.Code.SIN,
        RegionCode.Region.ap_south_1: RegionCode.Code.BOM,
        RegionCode.Region.ap_southeast_2: RegionCode.Code.SYN,
        RegionCode.Region.eu_central_1: RegionCode.Code.FRA,
        RegionCode.Region.ap_northeast_1: RegionCode.Code.NRT,
        RegionCode.Region.ap_northeast_2: RegionCode.Code.ICN,
        RegionCode.Region.sa_east_1: RegionCode.Code.GRU,
        RegionCode.Region.us_west_1: RegionCode.Code.SJC,
    }

    def test_iter(self):
        """
        RegionCode.__iter__() is correctly set up and iterates through the dictionary.
        """
        for key, value in RegionCode.iteritems():
            self.assertEquals(self.REGIONS[key], value)

    def test_len(self):
        """
        RegionCode.__len__() is correctly set up and returns the length the dictionary.
        """
        self.assertEquals(len(self.REGIONS), len(RegionCode))

    def test_get_by_code(self):
        """
        Region can be correctly retrieved from Code using RegionCode.
        """
        for code in list(RegionCode.Code):
            self.assertEquals(self.REGIONS[code], RegionCode[code])

    def test_get_by_region(self):
        """
        Code can be correctly retrieved from Region using RegionCode.
        """
        for reg in list(RegionCode.Region):
            self.assertEquals(self.REGIONS[reg], RegionCode[reg])

    def test_get_by_code_str(self):
        """
        Region can be correctly retrieved from Code string using RegionCode.
        """
        for code in list(RegionCode.Code):
            self.assertEquals(self.REGIONS[code], RegionCode[code.name])

    def test_get_by_code_str_lower(self):
        """
        Region can be correctly retrieved from Code string using RegionCode, regardless of the case
        """
        for code in list(RegionCode.Code):
            self.assertEquals(self.REGIONS[code], RegionCode[code.name.lower()])

    def test_get_by_region_str(self):
        """
        Code can be correctly retrieved from Region string using RegionCode.
        """
        for reg in list(RegionCode.Region):
            self.assertEquals(self.REGIONS[reg], RegionCode[reg.name])

    def test_get_by_region_str_uppder(self):
        """
        Code can be correctly retrieved from Region string using RegionCode, regardless of the case
        """
        for reg in list(RegionCode.Region):
            self.assertEquals(self.REGIONS[reg], RegionCode[reg.name.upper()])

    def test_get_by_region_name(self):
        """
        Code can be correctly retrieved from Region string with dashes using RegionCode.
        """
        for reg in list(RegionCode.Region):
            reg_str = reg.name.replace('_', '-')

            self.assertEquals(self.REGIONS[reg], RegionCode[reg_str])

    def test_get_error(self):
        """
        Given an invalid key, RegionCode throws error
        """
        fake_key = 'foobar'
        with self.assertRaises(KeyError) as e:
            RegionCode[fake_key]

        self.assertEquals("'{0}'".format(fake_key), str(e.exception))
