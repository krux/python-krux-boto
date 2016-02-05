python-krux-boto
=====================

Krux Python class built on top of [Krux Stdlib](https://staticfiles.krxd.net/foss/docs/pypi/krux-stdlib/) for interacting with [Boto](http://boto.readthedocs.org/en/latest/)

Application quick start
-----------------------

The most common use case is to build a CLI script on top of boto.
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

    ### This gets you a region object based on the preference of
    ### the CLI parameters passed:
    region = app.boto.ec2.get_region(app.boto.cli_region)

    ### Sample program: connect to ec2 and list the regions:
    ec2 = app.boto.connect_ec2(region = region)

    ### Some simple diagnostics to show that it works
    app.logger.warn('Connected to region: %s', region.name)

    for r in ec2.get_all_regions():
        app.logger.warn('Region: %s', r.name)

### Run the application stand alone
if __name__ == '__main__':
    main()

```

Extending your application
--------------------------

Alternately, you want to add boto functionality to your larger script or application.
Here's how to do that:

```python

from krux_boto import Boto

class MyApplication( object ):

    BOTO_ACCCESS_KEY = 'fakeAccessKey'
    BOTO_SECRET_KEY = 'fakeSecretKey'
    BOTO_LOG_LEVEL = 'info'
    BOTO_REGION = 'us-east-1'

    def __init__(self, *args, **kwargs):
        self.boto = Boto(
            log_level=self.BOTO_LOG_LEVEL,
            access_key=self.BOTO_ACCESS_KEY,
            secret_key=self.BOTO_SECRET_KEY,
            region=self.BOTO_REGION,
            logger=self.logger,
            stats=self.stats,
        )

    def run(self):
        print self.boto.ec2.get_region(self.boto.cli_region).name

```

### Constructor Arguments
|Name|Value|Default|
|---|---|---|
|access_key|AWS Access Key to use|Environment variable `$AWS_ACCESS_KEY_ID`|
|secret_key|AWS Secret Key to use|Environment variable `$AWS_SECRET_ACCESS_KEY`|
|log_level|Verbosity of boto logging (Choose between `critical`, `error`, `warning`, `info`, `debug`)|`warning`|
|region|EC2 Region to connect to|`us-east-1`|
*NOTE:* This info can also be found in `krux_boto.Boto.add_boto_cli_arguments`.

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
                      [--boto-region {us-east-1,cn-north-1,ap-northeast-1,eu-west-1,ap-southeast-1,ap-southeast-2,us-west-2,us-gov-west-1,us-west-1,sa-east-1}]

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
  --boto-region {us-east-1,cn-north-1,ap-northeast-1,eu-west-1,ap-southeast-1,ap-southeast-2,us-west-2,us-gov-west-1,us-west-1,sa-east-1}
                        EC2 Region to connect to. (default: us-east-1)
```
