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
from six import iteritems

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

def setup_hosts(hosts, accepted_domains=['krxd.net'], default='krxd.net'):
    """
    Loop through hosts to check if the domain matches any in accepted_domains. If not, append default.
    This function will return a new list.

    :param hosts: A list of hostname strings
    :param accepted_domains: A list of accepted domain strings
    :param default: A default domain name string to be appended to the hostnames

    :return: A list of modified host name strings
    """
    new_hostnames = []
    for i in range(len(hosts)):
        # Python 2.6 support
        if hosts[i][-8:len(hosts[i])] not in accepted_domains:
            new_hostnames.append(hosts[i] + '.' + default)
        else:
            new_hostnames.append(hosts[i])
    return new_hostnames

# Region codes
class __RegionCode(Mapping):

    # GOTCHA: The dictionary is created by matching the values.
    #         Therefore, when adding a region, make sure the values of the enums match.
    #         i.e. If we add LA as one of the regions, then Region.LA.value == Code.LAX.value.
    class Code(Enum):
        """
        Krux uses the largest airport in the region for the codename of AWS region.
        This enum is the representation of that.
        """
        # Use IATA codes since they sound closer to the colloquial airport names
        ASH = 1   # Ashburn, Virginia
        PDX = 2   # Portland, Oregon
        DUB = 3   # Dublin, Ireland
        SIN = 4   # Singapore
        BOM = 5   # Mumbai (Bombay), India
        SYD = 6   # Sydney, Australia
        FRA = 7   # Frankfurt, Germany
        NRT = 8   # Tokyo (Narita), Japan
        ICN = 9   # Seoul (Incheon), South Korea
        GRU = 10  # Sao Paulo (Guarulhos), Brazil
        SJC = 11  # San Jose, California
        CMH = 12  # Columbus, Ohio

    class Region(Enum):
        """
        Names of AWS regions as an enum.
        """
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
        us_east_2 = 12

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
        dash_dict = {}
        for name, region in iteritems(self.Region._member_map_):
            dash_dict[name.lower().replace('_', '-')] = region
        self.Region._member_map_.update(dash_dict)

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
