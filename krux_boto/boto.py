# -*- coding: utf-8 -*-
#
# © 2015-2016 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import, division, print_function, unicode_literals
from functools import wraps

# Declare the baseboto class a metaclass to avoid
# it being used directly
from abc import ABCMeta, abstractmethod

import os

#
# Third party libraries
#

# For differences between version2 & version3, please see here:
# http://boto3.readthedocs.org/en/latest/guide/migration.html

# Version2
import boto
import boto.ec2
import boto.utils

# Version3
import boto3

from six import iteritems

#
# Internal libraries
#

from krux.logging import get_logger, LEVELS, DEFAULT_LOG_LEVEL
from krux.stats import get_stats
from krux.cli import get_parser, get_group
from krux_boto.util import RegionCode


# Constants
ACCESS_KEY = 'AWS_ACCESS_KEY_ID'
SECRET_KEY = 'AWS_SECRET_ACCESS_KEY'
REGION = 'AWS_DEFAULT_REGION'
NAME = 'krux-boto'

# GOTCHA: This is not meant to be imported by another library. Thus, prefix with double underscore.
__DEFAULT_REGION = 'us-east-1'

# Defaults
# GOTCHA: If this is a simple string-to-string dictionary, values are evaluated on compilation.
#         This may cause some serious hair pulling if the developer decides to change the environment variable
#         and expect krux-boto to pick it up. Thus, make this a string-to-function dictionary
#         so the values are evaluated on method call and get up-to-date value.
DEFAULT = {
    'log_level': lambda: DEFAULT_LOG_LEVEL,
    'access_key': lambda: os.environ.get(ACCESS_KEY),
    'secret_key': lambda: os.environ.get(SECRET_KEY),
    # GOTCHA: Unlike credentials, this is defaulted to environment variable, but not required. Create a default
    #         fall-back value.
    'region': lambda: os.environ.get(REGION, __DEFAULT_REGION),
}


def __get_arguments(args=None, logger=None, stats=None):
    """
    A helper method that generates a dictionary of arguments needed to instantiate a BaseBoto object.
    The purpose of this method is to abstract out the code to handle optional CLI arguments
    and not duplicate the None handling code.

    :param args: Namespace of arguments parsed by argparse
    :type args: argparse.Namespace
    :param logger: Logger, recommended to be obtained using krux.cli.Application
    :type logger: logging.Logger
    :param stats: Stats, recommended to be obtained using krux.cli.Application
    :type stats: kruxstatsd.StatsClient
    :return: A dictionary of arguments needed for BaseBoto.__init__()
    :rtype: dict
    """

    if not args:
        parser = get_parser()
        add_boto_cli_arguments(parser)
        # Parse only the known arguments added by add_boto_cli_arguments().
        # We only need those arguments to create Boto object, nothing else.
        # parse_known_args() return (Namespace, list of unknown arguments),
        # we only care about the Namespace object here.
        args = parser.parse_known_args()[0]

    if not logger:
        logger = get_logger(name=NAME)

    if not stats:
        stats = get_stats(prefix=NAME)

    return {
        'log_level': getattr(args, 'boto_log_level', DEFAULT['log_level']()),
        'access_key': getattr(args, 'boto_access_key', DEFAULT['access_key']()),
        'secret_key': getattr(args, 'boto_secret_key', DEFAULT['secret_key']()),
        'region': getattr(args, 'boto_region', DEFAULT['region']()),
        'logger': logger,
        'stats': stats,
    }


def get_boto(args=None, logger=None, stats=None):
    """
    Return a usable Boto object without creating a class around it.

    In the context of a krux.cli (or similar) interface the 'args', 'logger'
    and 'stats' objects should already be present. If you don't have them,
    however, we'll attempt to provide usable ones for the boto setup.

    (If you omit the add_boto_cli_arguments() call during other cli setup,
    the Boto object will still work, but its cli options won't show up in
    --help output)

    :param args: Namespace of arguments parsed by argparse
    :type args: argparse.Namespace
    :param logger: Logger, recommended to be obtained using krux.cli.Application
    :type logger: logging.Logger
    :param stats: Stats, recommended to be obtained using krux.cli.Application
    :type stats: kruxstatsd.StatsClient
    :return: Boto object created with the arguments, logger, and stats created or deduced
    :rtype: krux_boto.boto.Boto
    """
    return Boto(**__get_arguments(args, logger, stats))


def get_boto3(args=None, logger=None, stats=None):
    """
    Return a usable Boto3 object without creating a class around it.

    In the context of a krux.cli (or similar) interface the 'args', 'logger'
    and 'stats' objects should already be present. If you don't have them,
    however, we'll attempt to provide usable ones for the boto setup.

    (If you omit the add_boto_cli_arguments() call during other cli setup,
    the Boto object will still work, but its cli options won't show up in
    --help output)

    :param args: Namespace of arguments parsed by argparse
    :type args: argparse.Namespace
    :param logger: Logger, recommended to be obtained using krux.cli.Application
    :type logger: logging.Logger
    :param stats: Stats, recommended to be obtained using krux.cli.Application
    :type stats: kruxstatsd.StatsClient
    :return: Boto3 object created with the arguments, logger, and stats created or deduced
    :rtype: krux_boto.boto.Boto3
    """
    return Boto3(**__get_arguments(args, logger, stats))


# Designed to be called from krux.cli, or programs inheriting from it
def add_boto_cli_arguments(parser, include_log_level=True, include_credentials=True, include_region=True):

    group = get_group(parser, 'boto')

    if include_log_level:
        group.add_argument(
            '--boto-log-level',
            default=DEFAULT['log_level'](),
            choices=LEVELS.keys(),
            help="Verbosity of boto logging. (default: %(default)s)",
        )

    if include_credentials:
        group.add_argument(
            '--boto-access-key',
            default=DEFAULT['access_key'](),
            help="AWS Access Key to use. Defaults to ENV[{0}]".format(ACCESS_KEY),
        )

        group.add_argument(
            '--boto-secret-key',
            default=DEFAULT['secret_key'](),
            help="AWS Secret Key to use. Defaults to ENV[{0}]".format(SECRET_KEY),
        )

    if include_region:
        group.add_argument(
            '--boto-region',
            default=DEFAULT['region'](),
            choices=[r.name for r in boto.ec2.regions()],
            help=(
                "EC2 Region to connect to. Defaults to ENV[{0}]. If not ENV set, defaults to us-east-1.".format(REGION)
            ),
        )


class BaseBoto(object):
    # This is an abstract class, which prevents direct instantiation. See here
    # for details: https://docs.python.org/2/library/abc.html
    __metaclass__ = ABCMeta

    def __init__(
        self,
        log_level=None,
        access_key=None,
        secret_key=None,
        region=None,
        logger=None,
        stats=None,
    ):
        # Private variables, not to be used outside this module
        self._name = NAME
        self._logger = logger or get_logger(self._name)
        self._stats = stats or get_stats(prefix=self._name)

        if log_level is None:
            log_level = DEFAULT['log_level']()

        if access_key is None:
            access_key = DEFAULT['access_key']()

        if secret_key is None:
            secret_key = DEFAULT['secret_key']()

        if region is None:
            region = DEFAULT['region']()

        if REGION not in os.environ:
            self._logger.debug(
                "There is not a default region set in your environment variables. Defaulted to '%s'", region
            )

        # GOTCHA: Due to backward incompatible version change in v1.0.0, the users of krux_boto may
        # pass wrong credential. Make sure the passed credential via CLI is the same as one passed into this instance.
        parser = get_parser()
        add_boto_cli_arguments(parser)
        # GOTCHA: We only care about the credential arguments and nothing else.
        # Don't validate the arguments or parse other things. Let krux.cli do that.
        args = parser.parse_known_args()
        _access_key = getattr(args, 'boto_access_key', None)
        _secret_key = getattr(args, 'boto_secret_key', None)
        if _access_key is not None and _access_key != access_key:
            self._logger.warn(
                'You set %s as boto-access-key in CLI, but passed %s to the library. '
                'To avoid this error, consider using get_boto() function. '
                'For more information, please check README.',
                BaseBoto._hide_value(_access_key), BaseBoto._hide_value(access_key),
            )
        if _secret_key is not None and _secret_key != secret_key:
            self._logger.warn(
                'You set %s as boto-secret-key in CLI, but passed %s to the library. '
                'To avoid this error, consider using get_boto() function. '
                'For more information, please check README.',
                BaseBoto._hide_value(_secret_key), BaseBoto._hide_value(secret_key),
            )

        # Infer the loglevel, but set it as a property so the subclasses can
        # use it to set the loglevels on the loghandlers for their implementation
        self._boto_log_level = LEVELS[log_level]

        # this has to be 'public', so callers can use it. It's unfortunately
        # near impossible to transparently wrap this, because the boto.config
        # is initialized before we get here, and all the classes do a look up
        # at compile time. So overriding doesn't help.
        # Wrapping doesn't work cleanly, because we 1) would have to wrap
        # everything, including future features we can't know about yet, as
        # well as 2) poke into the guts of the implementation classes to figure
        # out connection strings etc. It's quite cumbersome.
        # So for now, we just store the region that was asked for, and let the
        # caller use it. See the sample app for a howto.
        self.cli_region = region
        # if these are set, make sure we set the environment again
        # as well; that way the underlying boto calls will just DTRT
        # without the need to wrap all the functions.
        credential_map = {
            ACCESS_KEY: access_key,
            SECRET_KEY: secret_key,
        }
        for env_var, val in iteritems(credential_map):
            if val is None or len(val) < 1:
                self._logger.debug('Passed boto credentials is empty. Falling back to environment variable %s', env_var)
            else:

                # this way we can tell what credentials are being used,
                # without dumping the whole secret into the logs
                self._logger.debug('Setting boto credential %s to %s', env_var, BaseBoto._hide_value(val))

                os.environ[env_var] = val

            # If at this point the environment variable is NOT set,
            # you didn't set it, and we didn't set it. At which point
            # boto will go off spelunking for .boto files or other
            # settings. Best be clear about this. Using 'if not' because
            # if you set it like this:
            # $ FOO= ./myprog.py
            # It'll return an empty string, and we'd not catch it.
            if not os.environ.get(env_var, None):
                self._logger.debug(
                    'Boto environment credential %s NOT explicitly set ' +
                    '-- boto will look for a .boto file somewhere', env_var
                )

    @staticmethod
    def _hide_value(value):
        return value[0:3] + '[...]' + value[-3:]

    def __getattr__(self, attr):
        """Proxies calls to ``boto.*`` methods."""

        # This way, we don't have to write: rv = Boto().boto.some_call
        # But can just write: rv = Boto().some_call
        # This also gives us hooks for future logging/timers/etc and
        # extended wrapping of things the attributes return if we so
        # choose.

        self._logger.debug('Calling wrapped boto attribute: %s on %s', attr, self)

        attr = getattr(self._boto, attr)

        if callable(attr):
            self._logger.debug("Boto attribute '%s' is callable", attr)

            @wraps(attr)
            def wrapper(*args, **kwargs):
                return attr(*args, **kwargs)
            return wrapper

        return attr

    @abstractmethod
    def get_valid_regions(self):
        """
        Gets all AWS regions that Krux can access

        :return: A list of :py:class:`RegionCode.Region` for the known regions. For any new regions
                 for which the enum does not exist, just returns the name of the region as a string.
        :rtype: list[RegionCode.Region]
        """
        pass


class Boto(BaseBoto):

    # All the hard work is done in the superclass. We just need to use the
    # resulting object to initialize a session properly.
    def __init__(self, *args, **kwargs):
        # Call to the superclass to resolve.
        super(Boto, self).__init__(*args, **kwargs)

        # access the boto classes via the object. Note these are just the
        # classes for internal use, NOT the object as exposed via the CLI
        # or the objects returned via the get_boto* calls
        self._boto = boto

        # This sets the log level for the underlying boto library
        get_logger('boto').setLevel(self._boto_log_level)

    def get_valid_regions(self):
        """
        Gets all AWS regions that Krux can access

        :return: A list of :py:class:`RegionCode.Region` for the known regions. For any new regions
                 for which the enum does not exist, just returns the name of the region as a string.
        :rtype: list[RegionCode.Region]
        """
        conn = self._boto.ec2.connect_to_region(self.cli_region)

        regions = []
        for region in conn.get_all_regions():
            if getattr(RegionCode.Region, region.name, None) is not None:
                regions.append(RegionCode.Region[region.name])
            else:
                regions.append(region.name)

        return regions


class Boto3(BaseBoto):

    # All the hard work is done in the superclass. We just need to use the
    # resulting object to initialize a session properly.
    def __init__(self, *args, **kwargs):
        # Call to the superclass to resolve.
        super(Boto3, self).__init__(*args, **kwargs)

        # In boto3, the custom settings like region and connection params are
        # stored in what's called a 'session'. This object behaves just like
        # the boto3 class invocation, but it uses your custom settings instead.
        # Read here for details: http://boto3.readthedocs.org/en/latest/guide/session.html

        # Creating your own session, based on the region that was passed in
        session = boto3.session.Session(region_name=self.cli_region)

        # access the boto classes via the session. Note these are just the
        # classes for internal use, NOT the object as exposed via the CLI
        # or the objects returned via the get_boto* calls
        self._boto = session

        # This sets the log level for the underlying boto library
        # http://boto3.readthedocs.org/en/latest/reference/core/boto3.html?highlight=logging
        # XXX note that the name of the default boto3 logger is NOT boto3, it's
        # called 'botocore'
        get_logger('botocore').setLevel(self._boto_log_level)

    def get_valid_regions(self):
        """
        Gets all AWS regions that Krux can access

        :return: A list of :py:class:`RegionCode.Region` for the known regions. For any new regions
                 for which the enum does not exist, just returns the name of the region as a string.
        :rtype: list[RegionCode.Region]
        """
        client = self._boto.client('ec2')

        regions = []
        for region in client.describe_regions().get('Regions', []):
            if getattr(RegionCode.Region, region.get('RegionName'), None) is not None:
                regions.append(RegionCode.Region[region.get('RegionName')])
            else:
                regions.append(region.get('RegionName'))

        return regions
