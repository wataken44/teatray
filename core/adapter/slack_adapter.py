#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" slack_adapter.py


"""

from datetime import datetime
from threading import Thread
import time
import re

try:
    from Queue import Queue, Empty # python 2 -> Queue.Queue
except:
    from queue import Queue, Empty # python 3 -> queue.Queue

import slacker

from core.adapter.adapter_base import AdapterBase
from core.message.message import Message

class SlackAdapter(AdapterBase):
    def __init__(self, adapter_id, api_token, channel_name):
        AdapterBase.__init__(self, adapter_id)
        self._slacker = slacker.Slacker(api_token)
        self._channel_name = channel_name
        self._channel_id = None
        self._latest_tsint = None
        self._user = None
        self._member = {}
        
        self._to_chat_queue = Queue()
        self._to_chat_thread = Thread(target=self._send_to_chat_loop) 
        self._from_chat_thread = Thread(target=self._recv_from_chat_loop) 

        self._send_to_other_function = None
        self._pattern_mention = re.compile('<@([^|>]*)>')
        self._pattern_unescape0 = re.compile('<([^|>]*)\|([^>]*)>')
        self._pattern_unescape1 = re.compile('<([^|>]*)>')

        self._setup()
        
    def get_recv_from_other_function(self):
        return self._recv_from_other

    def set_send_to_other_function(self, func):
        self._send_to_other_function = func

    def _recv_from_other(self, message):
        self._to_chat_queue.put(message)

    def _to_ts(self, tsint):
        return "%d.%d" % (tsint / 1000000, tsint % 1000000)

    def _to_tsint(self, ts):
        a = ts.split(".")
        return int(a[0]) * 1000000 + int(a[1])
        
    def _setup(self):
        raw_data = self._slacker.auth.test().body
        self._user = raw_data['user_id']

        raw_data = self._slacker.channels.list().body
        for data in raw_data['channels']:
            if data['name'] == self._channel_name:
                self._channel_id = data['id']

        raw_data = self._slacker.channels.info(self._channel_id).body
        self._latest_tsint = self._to_tsint(raw_data['channel']['latest']['ts'])

        raw_data = self._slacker.users.list().body
        for data in raw_data['members']:
            self._member[ data['id'] ] = data['name']
        
    def _send_to_chat_loop(self):
        while True:
            try:
                m = self._to_chat_queue.get(block=True, timeout=30)
                if m.adapter_id == self._adapter_id:
                    continue
                text = u'`%s`: %s' % (m.user, m.body)
                self._slacker.chat.post_message(self._channel_id, text)
                time.sleep(2)
            except Empty:
                time.sleep(2)

    def _recv_from_chat_loop(self):
        while True:
            oldest = self._to_ts(self._latest_tsint)
            raw_data = self._slacker.channels.history(
                channel=self._channel_id, oldest=oldest).body
            messages = raw_data['messages']
            new_latest_tsint = self._latest_tsint
            for rm in reversed(messages):
                # don't send other than message
                if ('type' not in rm) or ('user' not in rm) or  (rm['type'] != 'message'):
                    continue
                # don't send my message
                if rm['user'] == self._user:
                    continue
                username = 'unknown'
                if rm['user'] in self._member:
                    username = self._member[ rm['user'] ]
                
                sm = Message(self._adapter_id,
                             username,
                             self._unescape(rm['text']),
                             datetime.fromtimestamp(float(rm['ts'])))
                self._send_to_other_function(sm)

                if self._to_tsint(rm['ts']) > new_latest_tsint:
                    new_latest_tsint = self._to_tsint(rm['ts'])

            self._latest_tsint = new_latest_tsint
            time.sleep(60)

    def _unescape(self, text):
        while True:
            mo = self._pattern_mention.search(text)
            if mo is None:
                break
            name = self._member[ mo.group(1) ]
            text = text.replace(mo.group(0), '@' + name)
            
        text = self._pattern_unescape0.sub('\\2', text)
        text = self._pattern_unescape1.sub('\\1', text)
        return text.replace('&gt;','>').replace('&lt;','<').replace('&amp;','&')
                
    def start(self):
        self._to_chat_thread.start()
        self._from_chat_thread.start()

    def join(self):
        self._to_chat_thread.join()
        self._from_chat_thread.join()
