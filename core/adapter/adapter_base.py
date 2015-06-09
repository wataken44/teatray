#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" adapter_base.py


"""

class AdapterBase(object):
    def __init__(self, adapter_id):
        self._adapter_id = adapter_id
        self._send_to_other_function = None
    
    def set_send_to_other_function(self, func):
        self._send_to_other_function = func
    
    def get_recv_from_other_function(self):
        return self._dummy_recv

    def _dummy_recv(self, message):
        return None

    def start(self):
        pass

    def join(self):
        pass

    def stop(self):
        pass
    
