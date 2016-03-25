# -*- coding: utf-8 -*-
#
# © 2014-2016 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
from abc import ABCMeta, abstractmethod

#
# Third party libraries
#

import simplejson

#
# Internal libraries
#

from krux.logging import get_logger
from krux.stats import get_stats
from krux_boto.boto import Boto3


NAME = 'krux-sqs'


def get_sqs(args=None, logger=None, stats=None):
    pass


def add_sqs_cli_arguments(parser):
    pass


class Sqs(object):
    """
    A manager to handle all SQS related functions.
    Each instance is locked to a connection to a designated region (self.boto.cli_region).
    """
    MAX_RECEIVE_MESSAGES_NUM = 10
    MAX_RECEIVE_MESSAGES_WAIT = 10

    def __init__(
        self,
        boto,
        logger=None,
        stats=None,
    ):
        # Private variables, not to be used outside this module
        self._name = NAME
        self._logger = logger or get_logger(self._name)
        self._stats = stats or get_stats(prefix=self._name)

        if not isinstance(boto, Boto3):
            raise NotImplementedError('Currently krux_boto.sqs.Sqs only supports krux_boto.boto.Boto3')

        self._resource = boto.resource('sqs')
        self._queues = {}

    def _get_queue(self, queue_name):
        """
        Returns a queue with the given name.
        The queue is fetched on the first call (lazy) and cached.

        :param queue_name: :py:class:`str` Name of the queue to get.
        """
        if queue_name not in self._queues or self._queues[queue_name] is None:
            self._queues[queue_name] = self._resource.get_queue_by_name(QueueName=queue_name)

        return self._queues[queue_name]

    def get_messages(self, queue_name):
        """
        Returns a list of messages in the given queue.

        :param queue_name: :py:class:`str` Name of the queue to get.
        """
        # GOTCHA: Note that not all messages may be returned
        # http://boto3.readthedocs.org/en/latest/reference/services/sqs.html#SQS.Queue.receive_messages
        raw_messages = self._get_queue(queue_name).receive_messages(
            MaxNumberOfMessages=self.MAX_RECEIVE_MESSAGES_NUM,
            WaitTimeSeconds=self.MAX_RECEIVE_MESSAGES_WAIT
        )

        result = []
        for msg in raw_messages:
            # Parse the strings as JSON so that we can deal with them easier
            body_dict = simplejson.loads(msg.body)
            body_dict['Message'] = simplejson.loads(body_dict['Message'])

            msg_dict = {
                'ReceiptHandle': msg.receipt_handle,
                'MessageId': msg.message_id,
                'Body': body_dict,
                'MessageAttributes': msg.message_attributes,
                'QueueUrl': msg.queue_url,
                'Attributes': msg.attributes,
            }
            result.append(msg_dict)

        return result

    def delete_messages(self, messages):
        raise NotImplementedError()
