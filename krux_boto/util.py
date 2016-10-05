# -*- coding: utf-8 -*-
#
# © 2015-2016 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
import string
from collections import Mapping

#
# Third party libraries
#

import boto.utils
from enum import Enum

#
# Internal libraries
#

from krux.logging import get_logger


class Error(Exception):
    pass


def get_instance_region():
    """
    Query the instance metadata service and return the region this instance is
    placed in. If the metadata service can't be contacted, return a generic
    default instead.
    """
    # TODO: XXX This shouldn't get called if we're not on EC2.
    zone = boto.utils.get_instance_metadata().get('placement', {}).get('availability-zone', None)
    if zone is None:
        get_logger('krux_boto').warn('get_instance_region failed to get the local instance region')
        raise Error('get_instance_region failed to get the local instance region')
    return zone.rstrip(string.lowercase)


# Region codes
class __RegionCode(Mapping):

    # GOTCHA: The dictionary is created by matching the values.
    # Therefore, when adding a region, make sure the values of the enums match.
    # i.e. If we add LA as one of the regions, then Region.LA.value == Code.LAX.value
    class Code(Enum):
        ASH = 1
        PDX = 2
        DUB = 3
        SIN = 4
        BOM = 5
        SYN = 6
        FRA = 7
        NRT = 8
        ICN = 9
        GRU = 10
        SFO = 11

    class Region(Enum):
        us_east_1 = 1
        us_west_2 = 2
        eu_west_1 = 3
        ap_southeast_1 = 4
        ap_south_1 = 5
        ap_southeast_2 = 6
        eu_central_1 = 7
        ap_northeast_1 = 8
        ap_northeast_2 = 9
        sa_east_1 = 10
        us_west_1 = 11

        def __str__(self):
            return self.name.lower().replace('_', '-')

    def __init__(self):
        self._wrapped = {}

        for code in list(self.Code):
            self._wrapped[code] = self.Region(code.value)

        for reg in list(self.Region):
            self._wrapped[reg] = self.Code(reg.value)

        # HACK: Enum does not allow us to override its __getitem__() method.
        #       Thus, we cannot handle the difference of underscore and dash gracefully.
        #       However, since __getitem__() is merely a lookup of _member_map_ dictionary, duplicate the elements
        #       in the private dictionary so that we can handle AWS region <-> RegionCode.Region conversion smoothly.
        for name, region in self.Region._member_map_.iteritems():
            self.Region._member_map_[name.lower().replace('_', '-')] = region

    def __iter__(self):
        return iter(self._wrapped)

    def __len__(self):
        return len(self._wrapped)

    def __getitem__(self, key):
        if isinstance(key, self.Region) or isinstance(key, self.Code):
            return self._wrapped[key]
        elif isinstance(key, str):
            key = key.replace('-', '_')

            code = getattr(self.Code, key.upper(), None)
            if code is not None:
                return self._wrapped[code]

            reg = getattr(self.Region, key.lower(), None)
            if reg is not None:
                return self._wrapped[reg]

        raise KeyError(key)

RegionCode = __RegionCode()
