#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Authors    : Gtlions Lai <gtlions.l@qq.com>
"""
"""
import psycopg2.extras


class ActionBase(object):
    def __init__(self, *args, **kwargs):
        self.init_msg = ('init %s %s' % (self.__class__.__name__, '' if not self.__doc__ else self.__doc__))

    def makeinet(self, ip):
        return psycopg2.extras.Inet(ip)
