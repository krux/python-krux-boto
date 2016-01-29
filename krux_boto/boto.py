# -*- coding: utf-8 -*-
#
# © 2015 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
from pprint import pprint
from functools import wraps

import os

#
# Third party libraries
#

import boto
import boto.ec2
import boto.utils

#
# Internal libraries
#

from krux.logging import get_logger, LEVELS, DEFAULT_LOG_LEVEL
from krux.stats import get_stats
from krux.cli import get_parser, get_group


# Constants
ACCESS_KEY = 'AWS_ACCESS_KEY_ID'
SECRET_KEY = 'AWS_SECRET_ACCESS_KEY'
NAME = 'krux-boto'

# Defaults
DEFAULT = {
    'log_level': lambda: DEFAULT_LOG_LEVEL,
    'access_key': lambda: os.environ.get(ACCESS_KEY),
    'secret_key': lambda: os.environ.get(SECRET_KEY),
    'region': lambda: 'us-east-1'
}


# Designed to be called from krux.cli, or programs inheriting from it
def add_boto_cli_arguments(parser):

    group = get_group(parser, 'boto')

    group.add_argument(
        '--boto-log-level',
        default=DEFAULT['log_level'](),
        choices=LEVELS.keys(),
        help='Verbosity of boto logging. (default: %(default)s)'
    )

    group.add_argument(
        '--boto-access-key',
        default=DEFAULT['access_key'](),
        help='AWS Access Key to use. Defaults to ENV[%s]' % ACCESS_KEY,
    )

    group.add_argument(
        '--boto-secret-key',
        default=DEFAULT['secret_key'](),
        help='AWS Secret Key to use. Defaults to ENV[%s]' % SECRET_KEY,
    )

    group.add_argument(
        '--boto-region',
        default=DEFAULT['region'](),
        choices=[r.name for r in boto.ec2.regions()],
        help='EC2 Region to connect to. (default: %(default)s)',
    )


class Boto(object):

    def __init__(
        self,
        log_level=None,
        access_key=None,
        secret_key=None,
        region=None,
        logger=None,
        stats=None,
    ):

        # Because we're wrapping boto directly, use ___ as a prefix for
        # all our variables, so we don't clash with anything public
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

        for env_var, val in credential_map.iteritems():
            if val is None or len(val) < 1:
                self._logger.debug('Passed boto credentials is empty. Falling back to environment variable %s', env_var)
            else:

                # this way we can tell what credentials are being used,
                # without dumping the whole secret into the logs
                pp_val = val[0:3] + '[...]' + val[-3:]
                self._logger.debug('Setting boto credential %s to %s', env_var, pp_val)

                os.environ[env_var] = val

            # If at this point the environment variable is NOT set,
            # you didn't set it, and we didn't set it. At which point
            # boto will go off spelunking for .boto files or other
            # settings. Best be clear about this. Using 'if not' because
            # if you set it like this:
            # $ FOO= ./myprog.py
            # It'll return an empty string, and we'd not catch it.
            if not os.environ.get(env_var, None):
                self._logger.info(
                    'Boto environment credential %s NOT explicitly set ' +
                    '-- boto will look for a .boto file somewhere', env_var
                )

        # This sets the log level for the underlying boto library
        get_logger('boto').setLevel(LEVELS[log_level])

        # access it via the object
        self._boto = boto

    def __getattr__(self, attr):
        """Proxies calls to ``boto.*`` methods."""

        # This way, we don't have to write: rv = Boto().boto.some_call
        # But can just write: rv = Boto().some_call
        # This also gives us hooks for future logging/timers/etc and
        # extended wrapping of things the attributes return if we so
        # choose.
        self._logger.debug('Calling wrapped boto attribute: %s', attr)

        attr = getattr(self._boto, attr)

        if callable(attr):
            self._logger.debug("Boto attribute '%s' is callable", attr)

            @wraps(attr)
            def wrapper(*args, **kwargs):
                return attr(*args, **kwargs)
            return wrapper

        return attr
