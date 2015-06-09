#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" hipchat_adapter.py


"""


from datetime import datetime
from threading import Thread
import time

try:
    from Queue import Queue, Empty # python 2 -> Queue.Queue
except:
    from queue import Queue, Empty # python 3 -> queue.Queue
    
import hypchat

from core.adapter.adapter_base import AdapterBase
from core.message.message import Message

class HipchatAdapter(AdapterBase):
    def __init__(self, adapter_id, api_token, room_id_or_name, handle):
        AdapterBase.__init__(self, adapter_id)
        self._hipchat = hypchat.HypChat(api_token)
        self._room = self._hipchat.get_room(room_id_or_name)
        self._handle = handle

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
                for i in range(3):
                    try:
                        self._room.notification(m.get_detail_text())
                        break
                    except:
                        time.sleep(5**i)
            except Empty:
                time.sleep(30)

    def _recv_from_chat_loop(self):
        cursor = datetime.utcnow()
        while True:
            try:
                messages = list(self._room.history(maxResults=90).contents())
            except:
                time.sleep(60)
                continue
            new_cursor = cursor
            for rm in messages:
                # remove timezone
                d = rm['date']
                rmd = datetime(d.year, d.month, d.day,
                               d.hour, d.minute, d.second, d.microsecond,
                               None)
                # don't send old message
                if rmd <= cursor:
                    continue
                # don't send my message
                user = self._get_user(rm)
                if user == self._handle:
                    continue
                sm = Message(self._adapter_id,
                             user,
                             rm['message'],
                             rmd)
                self._send_to_other_function(sm)

                if rmd > new_cursor:
                    new_cursor = rmd

            cursor = new_cursor
            time.sleep(60)

    def _get_user(self, rm):
        f = rm['from']
        if type(f) == hypchat.restobject.User:
            return f['name']
        elif type(f) == unicode:
            return f
        elif type(f) == str:
            return unicode(f)
        # never reach
        print(type(f))
        print(f)
            
    def start(self):
        self._to_chat_thread.start()
        self._from_chat_thread.start()

    def join(self):
        self._to_chat_thread.join()
        self._from_chat_thread.join()
