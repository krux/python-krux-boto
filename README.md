# python-krux-boto

Krux Python class built on top of [Krux Stdlib](https://staticfiles.krxd.net/foss/docs/pypi/krux-stdlib/) for interacting with [Boto](http://boto.readthedocs.org/en/latest/) and [Boto3](http://boto3.readthedocs.org/en/latest/index.html)

## How to use

Refer to each individual module's README:
* [krux_boto](krux_boto/README.md)
* [krux_sqs](krux_sqs/README.md)

## Developing python-krux-boto

1. `user:~$ git clone git@github.com:krux/python-krux-boto.git`
2. `user:python-krux-boto$ pip install -r dev-requirements.pip`
3. `user:python-krux-boto$ nosetests`

The tests should all pass. Now you are ready to improve this library.

## Seeing it in action

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
