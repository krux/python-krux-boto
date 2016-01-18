# -*- coding: utf-8 -*-
#
# © 2015 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import

#
# Third party libraries
#

import boto

#
# Internal libraries
#

import krux.cli
from krux_boto.boto import Boto, add_boto_cli_arguments, NAME

class Application(krux.cli.Application):

    def __init__(self, name = NAME):
        ### Call to the superclass to bootstrap.
        super(Application, self).__init__(name = name)

        self.boto = Boto(
            parser = self.parser,
            logger = self.logger,
            stats  = self.stats,
        )

    def add_cli_arguments(self, parser):

        ### add the arguments for boto
        add_boto_cli_arguments(parser)


def main():
    app    = Application()
    region = boto.ec2.get_region(app.boto.cli_region)
    ec2    = app.boto.connect_ec2(region = region)

    app.logger.warn('Connected to region: %s', region.name)
    for r in ec2.get_all_regions():
        app.logger.warn('Region: %s', r.name)


### Run the application stand alone
if __name__ == '__main__':
    main()
