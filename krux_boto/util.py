# -*- coding: utf-8 -*-
#
# © 2015-2016 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
import string

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
