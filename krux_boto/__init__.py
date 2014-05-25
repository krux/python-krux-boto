######################
# Standard Libraries #
######################
from __future__ import absolute_import
from pprint     import pprint
from functools  import wraps

import os

#########################
# Third Party Libraries #
#########################

### The boto library
import boto

### for the application class
import krux.cli

from krux.constants     import DEFAULT_LOG_LEVEL
from krux.logging       import get_logger, LEVELS
from krux.stats         import get_stats
from krux.cli           import get_parser, get_group


### Constants

ACCESS_KEY  = 'AWS_ACCESS_KEY_ID'
SECRET_KEY  = 'AWS_SECRET_ACCESS_KEY'
NAME        = 'krux-boto'

### Designed to be called from krux.cli, or programs inheriting from it
def add_boto_cli_arguments(parser):

    group = get_group(parser, 'boto')

    ### All our jobs only use minute & hour at this point
    ### so don't bother exposing more than that
    group.add_argument(
        '--boto-log-level',
        default = DEFAULT_LOG_LEVEL,
        choices = LEVELS.keys(),
        help    = 'Verbosity of boto logging. (default: %(default)s)'
    )

    group.add_argument(
        '--boto-access-key',
        default = os.environ.get(ACCESS_KEY),
        help    = 'AWS Access Key to use. Defaults to ENV[%s]' % ACCESS_KEY,
    )

    group.add_argument(
        '--boto-secret-key',
        default = os.environ.get(SECRET_KEY),
        help    = 'AWS Secret Key to use. Defaults to ENV[%s]' % SECRET_KEY,
    )

class Boto(object):

    def __init__(self, logger = None, stats = None, parser = None):

        self.name   = NAME
        self.logger = logger or get_logger(self.name)
        self.stats  = stats  or get_stats( prefix      = self.name)
        self.parser = parser or get_parser(description = self.name)

        ### in case we got some of the information via the CLI
        self.args       = self.parser.parse_args()

        ### if these are set, make sure we set the environment again
        ### as well; that way the underlying boto calls will just DTRT
        ### without the need to wrap all the functions.
        map = {
            'boto_access_key': ACCESS_KEY,
            'boto_secret_key': SECRET_KEY,
        }

        for name, env_var in map.iteritems():
            val = getattr( self.args, name, None )

            if val is not None:

                ### this way we can tell what credentials are being used,
                ### without dumping the whole secret into the logs
                pp_val = val[0:3] + '[...]' + val[-3:] if len(val) else '<empty>'
                self.logger.debug(
                    'Setting boto credential %s to %s', env_var, pp_val
                )

                os.environ[ env_var ] = val

            ### If at this point the environment variable is NOT set,
            ### you didn't set it, and we didn't set it. At which point
            ### boto will go off spelunking for .boto files or other
            ### settings. Best be clear about this. Using 'if not' because
            ### if you set it like this:
            ### $ FOO= ./myprog.py
            ### It'll return an empty string, and we'd not catch it.
            if not os.environ.get( env_var, None ):
                self.logger.info(
                    'Boto environment credential %s NOT explicitly set ' +
                    '-- boto will look for a .boto file somewhere', env_var
                )

        ### This sets the log level for the underlying boto library
        get_logger('boto').setLevel( LEVELS[ self.args.boto_log_level ] )

        ### access it via the object
        self.___boto = boto

    def __getattr__(self, attr):
        """Proxies calls to ``boto.*`` methods."""

        ### This way, we don't have to write: rv = Boto().boto.some_call
        ### But can just write: rv = Boto().some_call
        ### This also gives us hooks for future logging/timers/etc and
        ### extended wrapping of things the attributes return if we so
        ### choose.
        self.logger.debug('Calling wrapped boto attribute: %s', attr)

        attr = getattr(self.___boto, attr)

        if callable(attr):
            self.logger.debug("Boto attribute '%s' is callable", attr)

            @wraps(attr)
            def wrapper(*args, **kwargs):
                return attr(*args, **kwargs)
            return wrapper

        return attr


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
    app = Application()

    ec2 = app.boto.connect_ec2()

    for r in ec2.get_all_regions():
        app.logger.warn('Region: %s', r.name)


### Run the application stand alone
if __name__ == '__main__':
    main()
