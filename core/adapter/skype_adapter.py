#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" skype_adapter.py


"""

from datetime import datetime
from threading import Thread
import time

try:
    from Queue import Queue, Empty # python 2 -> Queue.Queue
except:
    from queue import Queue, Empty # python 3 -> queue.Queue
    
import Skype4Py

from core.adapter.adapter_base import AdapterBase
from core.message.message import Message

skype = None
def get_skype():
    global skype
    if skype is None:
        skype = Skype4Py.Skype()
        skype.Attach()
    return skype

def get_chat_by_topic(topic):
    skype = get_skype()
    for chat in skype.BookmarkedChats:
        if chat.Topic == topic:
            return chat
    return None

class SkypeAdapter(AdapterBase):
    def __init__(self, adapter_id, topic):
        AdapterBase.__init__(self, adapter_id)
        self._handle = get_skype().CurrentUserHandle
        self._chat = get_chat_by_topic(topic)

        self._to_chat_queue = Queue()

        self._to_chat_thread = Thread(target=self._send_to_chat_loop) 
        self._from_chat_thread = Thread(target=self._recv_from_chat_loop) 

        self._send_to_other_function = None
        
    def get_recv_from_other_function(self):
        return self._recv_from_other

    def set_send_to_other_function(self, func):
        self._send_to_other_function = func

    def _recv_from_other(self, message):
        self._to_chat_queue.put(message)

    def _send_to_chat_loop(self):
        while True:
            try:
                m = self._to_chat_queue.get(block=True, timeout=30)
                if m.adapter_id == self._adapter_id:
                    continue
                self._chat.SendMessage(m.get_detail_text())
            except Empty:
                time.sleep(30)

    def _recv_from_chat_loop(self):
        cursor = datetime.now()
        while True:
            messages = self._chat.RecentMessages
            new_cursor = cursor
            for rm in messages:
                # don't send old message
                if rm.Datetime <= cursor:
                    continue
                # don't send my message
                if rm.Sender.Handle == self._handle:
                    continue
                sm = Message(self._adapter_id,
                             rm.Sender.Handle,
                             rm.Body,
                             rm.Datetime)
                self._send_to_other_function(sm)

                if rm.Datetime > new_cursor:
                    new_cursor = rm.Datetime

            cursor = new_cursor
            time.sleep(30)
            
            
    def start(self):
        self._to_chat_thread.start()
        self._from_chat_thread.start()

    def join(self):
        self._to_chat_thread.join()
        self._from_chat_thread.join()
