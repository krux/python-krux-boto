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
    class Code(Enum):
        ASH = 1
        PDX = 2
        DUB = 3
        SIN = 4

    class Region(Enum):
        us_east_1 = 1
        us_west_2 = 2
        eu_west_1 = 3
        ap_southeast_1 = 4

    def __init__(self):
        self._wrapped = {}

        for code in list(self.Code):
            self._wrapped[code] = self.Region(code.value)

        for reg in list(self.Region):
            self._wrapped[reg] = self.Code(reg.value)

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
