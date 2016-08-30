# -*- coding: utf-8 -*-
#
# © 2016 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
import unittest

#
# Third party libraries
#


#
# Internal libraries
#

from krux_boto.enum import RegionCode


class RegionCodeTest(unittest.TestCase):
    REGIONS = {
        'ASH': ('us-east-1', RegionCode.ASH),
        'PDX': ('us-west-2', RegionCode.PDX),
        'DUB': ('eu-west-1', RegionCode.DUB),
        'SIN': ('ap-southeast-1', RegionCode.SIN),
    }

    def test_names(self):
        """
        ASH, PDX, DUB, and SIN are all defined
        """
        region_codes = [rc.name for rc in list(RegionCode)]
        for code in self.REGIONS.keys():
            self.assertIn(code, region_codes)

    def test_codes(self):
        """
        Enums have the correct code property defined
        """
        region_codes = [rc.code for rc in list(RegionCode)]
        for code in self.REGIONS.keys():
            self.assertIn(code, region_codes)

    def test_regions(self):
        """
        Enums have the correct region property defined
        """
        region_codes = [rc.region for rc in list(RegionCode)]
        for region in [r for r, e in self.REGIONS.values()]:
            self.assertIn(region, region_codes)

    def test_get_by_code(self):
        """
        Enums can be retrieved by region code (ASH, PDX, DUB, SIN)
        """
        for code in self.REGIONS.keys():
            self.assertEqual(self.REGIONS[code][1], RegionCode[code])
