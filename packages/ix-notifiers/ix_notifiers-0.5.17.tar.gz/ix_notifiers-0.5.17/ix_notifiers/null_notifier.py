#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Null """

from .notifier import Notifier, log

class NullNotifier(Notifier):
    """ The NullNotifier class """

    def __init__(self, **kwargs):
        self.settings = {}
        super().__init__(**kwargs)
        log.debug("Initialized")

start = NullNotifier.start
