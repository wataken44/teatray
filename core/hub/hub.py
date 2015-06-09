#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" hub.py


"""

class Hub(object):
    def __init__(self):
        self._port = []

    def start(self):
        for port in self._port:
            port.get_adapter().start()

    def join(self):
        for port in self._port:
            port.get_adapter().join()

    def add_adapter(self, adapter):
        port = Port(len(self._port), self, adapter)
        self._port.append(port)
        adapter.set_send_to_other_function(port.bridge)

    def bridge(self, from_index, message):
        for i in range(1, len(self._port)):
            to_index = (from_index + i) % len(self._port)
            adapter = self._port[to_index].get_adapter()
            adapter.get_recv_from_other_function()(message)
        
class Port(object):
    def __init__(self, index, hub, adapter):
        self._index = index
        self._hub = hub
        self._adapter = adapter

    def bridge(self, message):
        self._hub.bridge(self._index, message)

    def get_adapter(self):
        return self._adapter

    
