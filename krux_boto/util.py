# -*- coding: utf-8 -*-
#
# © 2015 Krux Digital, Inc.
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
    ### TODO: XXX This shouldn't get called if we're not on EC2.
    zone = boto.utils.get_instance_metadata().get('placement', {}).get('availability-zone', None)
    if zone is None:
        get_logger('krux_boto').warn('get_instance_region failed to get the local instance region')
        raise Error('get_instance_region failed to get the local instance region')
    return zone.rstrip(string.lowercase)
