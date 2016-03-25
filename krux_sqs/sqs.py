# -*- coding: utf-8 -*-
#
# © 2014-2016 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
from abc import ABCMeta, abstractmethod


NAME = 'krux-sqs'


def get_sqs(args=None, logger=None, stats=None):
    pass


def add_sqs_cli_arguments(parser):
    pass


class Sqs(object):
    __metaclass__ = ABCMeta

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

        self._boto = boto

    @abstractmethod
    def get_messages(self):
        raise NotImplementedError()

    @abstractmethod
    def delete_messages(self, messages):
        raise NotImplementedError()


class Sqs_Boto2(Sqs):
    pass


class Sqs_Boto3(Sqs):
    pass
