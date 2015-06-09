#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" teatray.py

chat hub utility

"""

import json
import os
import sys
rootdir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(rootdir + "/core/lib/")

from core.adapter.slack_adapter import SlackAdapter
from core.adapter.hipchat_adapter import HipchatAdapter
from core.adapter.skype_adapter import SkypeAdapter
from core.hub.hub import Hub

def create_hub(hub_param):
    hub = Hub()
    for ap in hub_param['adapter']:
        t = ap['type']
        adapter = None
        if t == 'core.adapter.slack_adapter.SlackAdapter':
            adapter = SlackAdapter(ap['id'], ap['api_token'], ap['channel'])
        elif t == 'core.adapter.hipchat_adapter.HipchatAdapter':
            adapter = HipchatAdapter(ap['id'], ap['api_token'], ap['room_id_or_name'], ap['handle'])
        elif t == 'core.adapter.skype_adapter.SkypeAdapter':
            adapter = SkypeAdapter(ap['id'], ap['topic'])
        hub.add_adapter(adapter)
        
    return hub

def main():
    fp = open('config.json')
    conf = json.load(fp)
    fp.close()

    hub = []
    for hp in conf['hub']:
        hub.append(create_hub(hp))

    for h in hub:
        h.start()

    for h in hub:
        h.join()
    


if __name__ == "__main__":
    main()
