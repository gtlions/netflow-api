#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2015-6-18

@author: grenb
'''

from .control.bgp import MainHandler, HeartBeat,UNBan

apibgpUrlpatterns = [
    (r"/ip", MainHandler),
    (r"/heartbeat", HeartBeat),
    (r"/unban",UNBan),
]
