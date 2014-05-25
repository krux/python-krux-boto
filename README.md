python-krux-scheduler
=====================

Krux Python class built on top of [Krux Stdlib](https://staticfiles.krxd.net/foss/docs/pypi/krux-stdlib/) for interacting with [Boto](http://boto.readthedocs.org/en/latest/)

Application quick start
-----------------------

The most common use case is to build a script on top of boto.
Here's how to do that:

```python

from krux_boto import Application

def main():
    ### The name must be unique to the organization. The object
    ### returned inherits from krux.cli.Application, so it provides
    ### all that functionality as well.
    app = Application( name = 'krux-my-boto-script' )

    ### This is the boto object, which behaves exactly like a standard
    ### boto object, but with the right logging/stats settings added.
    boto = app.boto

    ### Sample program: connect to ec2 and list the regions:
    ec2 = boto.connect_ec2()

    for r in ec2.get_all_regions():
        app.logger.warn('Region: %s', r.name)


### Run the application stand alone
if __name__ == '__main__':
    main()

```

Extending your application
--------------------------

Alternately, you want to add boto functionality to your larger script
or application that might be built on krux.cli.Application as well.
Here's how to do that:

```python


import krux.cli
from krux_boto import add_boto_cli_arguments

class MyApplication( krux.cli.Application ):

    def __init__(self, *args, **kwargs):
        ### Call to the superclass to bootstrap.
        super(MyApplication, self).__init__(name = 'my-application')

        self.boto = Boto(
            parser = self.parser,
            logger = self.logger,
            stats  = self.stats,
        )

    def add_cli_arguments(self, parser):

        ### add the arguments for boto
        add_boto_cli_arguments(parser)

```


Seeing it in action
-------------------

This library comes with a CLI tool bundled that shows you how the code works.

These are the options and how you can invoke it:

```
$ krux-boto-test -h
usage: krux-boto-test [-h] [--log-level {info,debug,critical,warning,error}]
                      [--stats] [--stats-host STATS_HOST]
                      [--stats-port STATS_PORT]
                      [--stats-environment STATS_ENVIRONMENT]
                      [--boto-log-level {info,debug,critical,warning,error}]
                      [--boto-access-key BOTO_ACCESS_KEY]
                      [--boto-secret-key BOTO_SECRET_KEY]

krux-boto

optional arguments:
  -h, --help            show this help message and exit

logging:
  --log-level {info,debug,critical,warning,error}
                        Verbosity of logging. (default: warning)

stats:
  --stats               Enable sending statistics to statsd. (default: False)
  --stats-host STATS_HOST
                        Statsd host to send statistics to. (default:
                        localhost)
  --stats-port STATS_PORT
                        Statsd port to send statistics to. (default: 8125)
  --stats-environment STATS_ENVIRONMENT
                        Statsd environment. (default: dev)

boto:
  --boto-log-level {info,debug,critical,warning,error}
                        Verbosity of boto logging. (default: warning)
  --boto-access-key BOTO_ACCESS_KEY
                        AWS Access Key to use. Defaults to
                        ENV[AWS_ACCESS_KEY_ID]
  --boto-secret-key BOTO_SECRET_KEY
                        AWS Secret Key to use. Defaults to
                        ENV[AWS_SECRET_ACCESS_KEY]
```
