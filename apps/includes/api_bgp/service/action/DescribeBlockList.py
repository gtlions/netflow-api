#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Gtlions Lai

from tornado import gen, netutil

from apps.common.zx_firewall import Firewall
from apps.common.my_thread import MyThread
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class DescribeBlockList(ActionBase):
    '''查询防火墙屏蔽列表'''

    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        # self.application.logger.info(self.init_msg)

    def select_block(self, operator, ip):
        firewall = Firewall(operator)
        return firewall.select_block_list(ip)

    @gen.coroutine
    def run(self):
        source_ip = self.params['SourceIP']
        operator = self.params['Operator']
        if not netutil.is_valid_ip(source_ip):
            res = sc(code.ParamError)
            raise gen.Return(res)

        data_info = {}
        data_info['BlockListData'] = []
        data_status = {}
        thread_list = []

        fw_list = self.application.firewalllist if operator == 'bgp' else [self.application.ccfirewall, operator]
        for i in fw_list:
            t = MyThread(self.select_block, args=(i, source_ip))
            thread_list.append(t)
        for t in thread_list:
            t.start()
        for t in thread_list:
            t.join()
        for index, item in enumerate(thread_list):
            data_status[fw_list[index]] = item.get_result()

        for k, v in data_status.items():
            data_info['BlockListData'].append({k: v})
        res = sc(code.Success)
        res.redata = data_info
        raise gen.Return(res)
