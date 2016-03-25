# krux_boto

## CRITICAL NOTE about versions!

Version 0.0.7 went through a major refactoring work and thus is not compatible with applications written with `krux-boto` version 0.0.6. The mechanism to fetch AWS credential is changed and may cause your application to use a different credentials than intended. Therefore, version 0.0.7 **should not be used**. Please use either 0.0.6 or 1.0.0 version. For update instructions, refer to the [section below](#version-update).

## Application quick start

The most common use case is to build a CLI script on top of boto.
Here's how to do that:

```python

from krux_boto import Application

def main():
    ### The name must be unique to the organization. The object
    ### returned inherits from krux.cli.Application, so it provides
    ### all that functionality as well.
    app = Application( name = 'krux-my-boto-script' )

    ### krux-boto supports both boto2 and boto3. See below for samples
    ### using either interface
    sample_boto2(app)
    sample_boto3(app)

def sample_boto2(app):
    ### This is the boto2 object, which behaves exactly like a standard
    ### boto object, but with the right logging/stats settings added.
    boto = app.boto

    ### This gets you a region object based on the preference of
    ### the CLI parameters passed:
    region = app.boto.ec2.get_region(app.boto.cli_region)

    ### Sample program: connect to ec2 and list the regions:
    ec2 = app.boto.connect_ec2(region = region)

    ### Some simple diagnostics to show that it works
    app.logger.warn('Boto2 - Connected to region: %s', region.name)

    for r in ec2.get_all_regions():
        app.logger.warn('Region: %s', r.name)

def sample_boto3(app):
    ### This is the boto3 object, which behaves exactly like a standard
    ### boto object, but with the right logging/stats settings added.
    boto = app.boto3

    ### This gets you an ec2 object, connected to the right region as
    ### passed in via the cli or app directly
    ec2 = boto.client('ec2')

    ### Some simple diagnostics to show that it works
    app.logger.warn('Boto3 - Connected to region: %s', boto.cli_region)

    ### See here for docs/return values:
    ### http://boto3.readthedocs.org/en/latest/reference/services/ec2.html#EC2.Client.describe_regions
    for rv in ec2.describe_regions().get('Regions', []):
        app.logger.warn('Region: %s', rv.get('RegionName'))

### Run the application stand alone
if __name__ == '__main__':
    main()

```

## Extending your application

From other CLI applications, you can make the use of `krux_boto.boto.get_boto()` function.

```python

from krux_boto.boto import get_boto, add_boto_cli_arguments
import krux.cli

class Application(krux.cli.Application):

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)

        self.boto = get_boto(self.args, self.logger, self.stats)

    def add_cli_arguments(self, parser):
        super(Application, self).add_cli_arguments(parser)

        add_boto_cli_arguments(parser)

```

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
*NOTE:*
* This info can also be found in [krux_boto.Boto.add_boto_cli_arguments](boto.py#L131)
* All arguments are string

### <a name="version-update"></a>Updating from 0.0.6 to 1.0.0

In version 0.0.6, `krux_boto.Boto` object took an `argparse.ArgumentParser` object as an optional parameter for the constructor. This approach has been abandoned. `krux_boto.Boto` object now expects 4 parameters listed below. Therefore, following change is required to get your application working with version 1.0.0.

```python

# Version 0.0.6

import krux.cli
from krux_boto import Boto, add_boto_cli_arguments

class Application(krux.cli.Application):

    def __init__(self, name='krux-my-boto-script'):
        super(Application, self).__init__(name=name)

        self.boto = Boto()

    def add_cli_arguments(self, parser):
        super(Application, self).add_cli_arguments(parser)

        add_boto_cli_arguments(parser)

```
```python

# Version 1.0.0

import krux.cli
from krux_boto import add_boto_cli_arguments, get_boto

class Application(krux.cli.Application):

    def __init__(self, name='krux-my-boto-script'):
        super(Application, self).__init__(name=name)

        # Notice the change in constructor parameters
        self.boto = get_boto()

    def add_cli_arguments(self, parser):
        super(Application, self).add_cli_arguments(parser)

        add_boto_cli_arguments(parser)

```
