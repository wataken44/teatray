#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" message.py


"""

class Message(object):
    def __init__(self, adapter_id, user, body, datetime):
        self._adapter_id = adapter_id
        self._user = user
        self._body = body
        self._datetime = datetime

    def get_detail_text(self):
        return u"%s: %s" % (self._user, self._body)

    def get_adapter_id(self):
        return self._adapter_id

    adapter_id = property(get_adapter_id)
        
    def get_user(self):
        return self._user
    
    user = property(get_user)

    def get_body(self):
        return self._body

    body = property(get_body)
    
