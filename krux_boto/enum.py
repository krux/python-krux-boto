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

    # def __call__(cls, value, *args, **kw):
    #     if isinstance(value, str):
    #         # map strings to enum values, defaults to Unknown
    #         value = {'nl': 2, 'src': 1}.get(value, 0)
    #     return super().__call__(value, *args, **kw)
