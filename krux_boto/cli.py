# -*- coding: utf-8 -*-
#
# © 2015-2016 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
from os import path
import json

#
# Third party libraries
#

#
# Internal libraries
#

import krux.cli
from krux_boto.boto import add_boto_cli_arguments, get_boto, get_boto3, NAME
from krux_boto.util import RegionCode


class Application(krux.cli.Application):
    # XXX: Usually, a VERSION constant should be set in __init__.py and be imported.
    #      However, krux-boto adds some basic classes to __init__.py and importing VERSION constant here
    #      causes a dependency circle. Thus, set VERSION constant in version.json and import it

    def __init__(self, name=NAME, *args, **kwargs):
        _VERSION_PATH = path.join(path.dirname(path.dirname(__file__)), 'version.json')
        with open(_VERSION_PATH, 'r') as f:
            self._VERSION = json.load(f).get('VERSION')

        self._VERSIONS[NAME] = self._VERSION

        # Call to the superclass to bootstrap.
        super(Application, self).__init__(name=name)

        self.boto = get_boto(self.args, self.logger, self.stats)

        self.boto3 = get_boto3(self.args, self.logger, self.stats)

    def add_cli_arguments(self, parser):
        super(Application, self).add_cli_arguments(parser)

        # add the arguments for boto
        add_boto_cli_arguments(parser)

    def run(self):
        self.logger.debug('Parsed arguments: %s', self.args)

        self._sample_boto2()
        self._sample_boto3()

    def _sample_boto2(self):
        self.logger.warn('Getting regions via boto2')
        for r in self.boto.get_valid_regions():
            if isinstance(r, RegionCode.Region):
                self.logger.warn('Region: %s - %s', RegionCode[r].name, str(r))
            else:
                self.logger.warn('Region: %s', r)

    def _sample_boto3(self):
        self.logger.warn('Getting regions via boto3')
        for r in self.boto3.get_valid_regions():
            if isinstance(r, RegionCode.Region):
                self.logger.warn('Region: %s - %s', RegionCode[r].name, str(r))
            else:
                self.logger.warn('Region: %s', r)


def main():
    app = Application()
    with app.context():
        app.run()


# Run the application stand alone
if __name__ == '__main__':
    main()
