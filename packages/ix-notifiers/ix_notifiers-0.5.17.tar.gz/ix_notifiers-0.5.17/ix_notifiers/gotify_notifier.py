#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Gotify """

from urllib.parse import urljoin
import requests
from .notifier import Notifier, log

class GotifyNotifier(Notifier):
    """ The GotifyNotifier class """
    params = {
        'token': {
            'mandatory': True,
            'redact': True,
            'type': 'string',
        },
        'url': {
            'mandatory': True,
            'type': 'string',
        },
        'content_type': {
            'default': 'text/markdown',
            'type': 'string',
        },
        'default_priority': {
            'default': 0,
            'type': 'integer',
        },
    }

    def __init__(self, **kwargs):
        self.settings = {}
        super().__init__(**kwargs)
        self.settings['url'] = urljoin(self.settings['url'], '/message')
        log.debug(self.redact(f"Initialized with {self.settings}"))

    def send(self, **kwargs) -> bool:
        """
        sends the notification to gotify

        return: True on success otherwise False
        """

        success = True
        headers = {
            'X-Gotify-Key': self.settings['token'],
            'user-agent': f'{self.user_agent}',
        }
        # Allow per message override of content_type
        extras = {
            'client::display': {
                'contentType': kwargs.get('content_type', self.settings['content_type']),
            }
        }

        req_json = {
            'extras': extras,
        }
        try:
            req_json.update({'message': kwargs['message']})
        except KeyError:
            pass

        try:
            req_json.update({'title': kwargs['title']})
        except KeyError:
            pass

        priority = 0
        try:
            priority = self.settings['default_priority']  # First look if there's a default priority
            priority = kwargs['priority']  # Any default priority is overridden by a message priority
        except KeyError:
            pass

        try:
            req_json.update({'priority': int(priority)})  # priority needs to be integer
        except TypeError:
            log.warning(f'Priority not understood: {priority}')

        resp = None
        try:
            resp = requests.post(self.settings['url'], json=req_json, headers=headers, timeout=60)
        except requests.exceptions.RequestException as e:
            # Print exception if reqeuest fails
            log.warning(self.redact(f'Could not connect to the Gotify server. The error: {e}'))
            success = False
        except Exception as e:
            log.error(self.redact(f'Failed to send message! Exception: {e}'))
            success = False

        # Print request result if server returns http error code
        if resp is not None:
            if resp.status_code is not requests.codes.ok:  # pylint: disable=no-member
                log.warning(self.redact(f'Error sending message to Gotify: {bytes.decode(resp.content)}'))
                success = False
            else:
                log.info("Sent message to gotify")

        return success

start = GotifyNotifier.start
