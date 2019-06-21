#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Gtlions Lai

from tornado import gen, netutil
from apps.common.zx_firewall import Firewall
from apps.common.zhi_firewall import ZhiFirewall
from apps.common.my_thread import MyThread
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class DescribeIPFirewallList(ActionBase):
    '''查询防火墙IP白名单'''

    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        # self.application.logger.info(self.init_msg)

    def select_ip(self, operator, hostname):
        firewall = ZhiFirewall(operator) if operator in self.application.zhifirewalllist else Firewall(operator)
        result = firewall.select_white_list(hostname)
        if result == 'white':
            return hostname + ':IP在白名单'
        elif result == 'black':
            return hostname + ':IP在黑名单'
        else:
            return hostname + ':IP不在名单'

    @gen.coroutine
    def run(self):
        operator = self.params['Operator']
        hostname = self.params['Hostname']
        data_info = {}

        if not netutil.is_valid_ip(hostname):
            res = sc(code.ParamError)
            res.result = res.result % hostname
            raise gen.Return(res)

        thread_list = []
        data_status = {}
        fw_list = self.application.firewalllist if operator == 'bgp' else [self.application.ccfirewall, operator]
        for i in fw_list:
            t = MyThread(self.select_ip, args=(i, hostname))
            thread_list.append(t)
        for t in thread_list:
            t.start()
        for t in thread_list:
            t.join()
        for index, item in enumerate(thread_list):
            data_status[fw_list[index]] = item.get_result()
        print(data_status)

        for k, v in data_status.items():
            if '白' not in v:
                data_info['DescribeIPFirewallList'] = operator + ':IP不在白名单'
                break
            else:
                data_info['DescribeIPFirewallList'] = operator + ':IP在白名单'
        res = sc(code.Success)
        res.redata = data_info
        raise gen.Return(res)
