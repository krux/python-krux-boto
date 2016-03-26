# -*- coding: utf-8 -*-
#
# © 2014-2016 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
from pprint import pprint

#
# Third party libraries
#

import boto

#
# Internal libraries
#

import krux.cli
from krux_boto.boto import add_boto_cli_arguments, get_boto, get_boto3, NAME


class Application(krux.cli.Application):

    def __init__(self, name=NAME):
        # Call to the superclass to bootstrap.
        super(Application, self).__init__(name=name)

        self.boto = get_boto(self.args, self.logger, self.stats)

        self.boto3 = get_boto3(self.args, self.logger, self.stats)

    def add_cli_arguments(self, parser):
        super(Application, self).add_cli_arguments(parser)

        # add the arguments for boto
        add_boto_cli_arguments(parser)

    def run(self):
        self._sample_boto2()
        self._sample_boto3()

    def _sample_boto2(self):
        region = self.boto.ec2.get_region(self.boto.cli_region)
        ec2 = self.boto.connect_ec2(region=region)

        self.logger.warn('Connected to region via boto2: %s', region.name)
        for r in ec2.get_all_regions():
            self.logger.warn('Region: %s', r.name)

    def _sample_boto3(self):
        ec2 = self.boto3.client('ec2')

        self.logger.warn('Connected to region via boto3: %s', self.boto3.cli_region)

        # See here for docs/return values:
        # http://boto3.readthedocs.org/en/latest/reference/services/ec2.html#EC2.Client.describe_regions
        for rv in ec2.describe_regions().get('Regions', []):
            self.logger.warn('Region: %s', rv.get('RegionName'))

def main():
    app = Application()
    with app.context():
        app.run()


# Run the application stand alone
if __name__ == '__main__':
    main()
