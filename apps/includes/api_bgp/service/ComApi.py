#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import logging
import os

from tornado import gen
# from apps.API_BGP.config.config import logger_name_std
from apps.includes.api_bgp.service import action

scenepath = action.__path__[0]


class ComApiService():
    scenelist = {}

    def __init__(self):
        '''
        Constructor
        '''
        pass
        # self.logger = logging.getLogger(logger_name_std)

    @gen.coroutine
    def run(self, params, application):
        #         print params
        action = params["Action"]
        C_class = self.initscene(action)
        # res = yield C_class().getMonitorDataByIP(params['IP'],params['StartTime'],params['EndTime'])
        res = yield C_class(params, application).run()
        # res = yield  C_class().getMoniterDatarFromHuawei(params['IP'],params['StartTime'],params['EndTime'])
        raise gen.Return(res)

    def initscene(self, action):
        files = os.path.join(scenepath, action + ".py")
        #         print files
        if os.path.isfile(files):
            C_module = __import__('apps.includes.api_bgp.service.action.' + action).includes.api_bgp.service.action
            #             print C_module
            C_class = getattr(getattr(C_module, action), action)
            return C_class
