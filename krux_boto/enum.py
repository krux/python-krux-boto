# -*- coding: utf-8 -*-
#
# © 2016 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import

#
# Third party libraries
#

from enum import Enum, EnumMeta

#
# Internal libraries
#


# Region codes
class RegionCode(Enum):
    ASH = ('ASH', 'us-east-1')
    PDX = ('PDX', 'us-west-2')
    DUB = ('DUB', 'eu-west-1')
    SIN = ('SIN', 'ap-southeast-1')

    def __init__(self, code, region):
        self.code = code
        self.region = region

    # GOTCHA: It would be so nice if I can override __getitem__ function
    # for this. However that is not possible with the current implementation.
    # Thus, creating a class method for this.
    @classmethod
    def from_region(cls, region):
        # Lower the
        region = region.lower()

        for enum in list(cls):
            if enum.region == region:
                return enum

        raise KeyError(region)
