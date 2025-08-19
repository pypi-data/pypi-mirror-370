#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" notification core """

import logging
import importlib
from os import listdir
from os.path import dirname, realpath
from typing import Dict, List, Any
from .constants import NAME

log = logging.getLogger(NAME)

class IxNotifiers:
    """ the IxNotifiers class """

    notifiers: List[str] = []
    registered: Dict[str, Any] = {}

    def __init__(self):
        """
        Records the existing notifiers

        It looks in the current library directory for all files called `*_notifier.py`
        """
        for notifier in listdir(dirname(realpath(__file__))):

            if notifier.endswith('_notifier.py'):
                self.notifiers.append(notifier.replace('_notifier.py', ''))
                log.debug(f"Notifier available: {notifier}")

    def register(self, notifier: str, **kwargs) -> None:
        """
        registers the notifiers

        Each notifier will expect `notifier_key: value`. The `notifier_` part will
        be stripped and the notifier will get `key` set as part of `kwargs`.

        For example, if the `register` `kwargs` is set to:

            kwargs = {
                'gotify_port': 1234,
                'gotify_token': 'abc'
            }

        Then the Gotify notifier will be called with:

        `gotify_notifier.start(port=1234, token='abc')`

        :param notifier: The notifier to be registered
        :type notifier: str
        """
        log.debug(f'Registering {notifier}')
        for n in self.notifiers:
            if n == notifier:
                instance = importlib.import_module(f'ix_notifiers.{notifier}_notifier')
                # Strips the prefix from kwargs, if set
                settings = {}
                for k, v in kwargs.items():
                    settings.update({k.replace(f'{notifier}_', ''): v})
                self.registered.update({notifier: instance.start(**settings)})
                log.debug(f'Registered {notifier}')

    def notify(self, **kwargs) -> bool:
        """
        dispatches a notification to all the registered notifiers

        :param **kwargs: get passed to the `send()` method of the notifier
        :return: True if at least one notification channel was successful, False otherwise
        :rtype: bool
        """
        success = False
        for notifier in self.registered.items():
            log.debug(f'Sending notification to {notifier}')
            if self.registered[notifier].send(**kwargs) is True:
                success = True
        return success

register = IxNotifiers.register
