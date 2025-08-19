#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" The Notifier Class """

from typing import Dict
from egos_helpers import redact
from .constants import NAME, BUILD, VERSION
from .core import log

class Notifier:
    """
    The base class, extended by notifiers

    This class not meant to be used directly!
    """

    settings: Dict = {}
    params: Dict = {}

    version: str
    user_agent: str

    def __init__(self, **kwargs):

        self.version = VERSION
        if BUILD:
            self.version += f'.{BUILD}'

        self.user_agent = f'{NAME} {self.version}'

        # go through self.params and check against kwargs
        for param, setting in self.params.items():
            if setting.get('mandatory') and not kwargs.get(f'{param}'):
                raise ValueError(f'{param} is mandatory')
            self.settings[param] = kwargs.get(f'{param}', self.params[param].get('default'))

            if (setting['type'] == 'boolean') and not isinstance(self.settings[param], bool):
                raise ValueError(f'`{param}` is not bool but {type(self.settings[param])}')
            if (setting['type'] == 'integer') and not isinstance(self.settings[param], int):
                raise ValueError(f'`{param}` is not int but {type(self.settings[param])}')
            if (setting['type'] == 'string') and not isinstance(self.settings[param], str):
                raise ValueError(f'`{param}` is not str but {type(self.settings[param])}')

    @classmethod
    def start(cls, **kwargs):
        """ Returns an instance of the Notifier """
        return cls(**kwargs)

    def send(self, **kwargs) -> bool:
        """
        logs the notification to info

        This method must be overwritten by the notifiers

        return: True
        """
        log.info(f"{self.redact(str(kwargs))}")
        return True

    def redact(self, message: str) -> str:
        """ based on self.params, it replaces sensitive information in message with a redacted string """
        for param, setting in self.params.items():
            message = redact(message, self.settings[param], setting.get('redact', False))
        return message
