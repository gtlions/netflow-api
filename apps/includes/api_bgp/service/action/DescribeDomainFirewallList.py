#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Gtlions Lai

from tornado import gen
from apps.common.zx_firewall import Firewall
from apps.common.zhi_firewall import ZhiFirewall
from apps.common.my_thread import MyThread
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class DescribeDomainFirewallList(ActionBase):
    '''查询防火墙域名白名单'''

    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        # self.application.logger.info(self.init_msg)

    def select_domain(self, operator, hostname):
        firewall = ZhiFirewall(operator) if operator in self.application.zhifirewalllist else Firewall(operator)
        # firewall = Firewall(operator)
        if firewall.query_domain_name(hostname):
            return hostname + ':域名在白名单'
        else:
            return hostname + ':域名不在名单'

    @gen.coroutine
    def run(self):
        operator = self.params['Operator']
        hostname = self.params['Hostname']
        data_info = {}

        thread_list = []
        data_status = {}
        fw_list = self.application.firewalllist if operator == 'bgp' else [self.application.ccfirewall, operator]
        for i in fw_list:
            t = MyThread(self.select_domain, args=(i, hostname))
            thread_list.append(t)
        for t in thread_list:
            t.start()
        for t in thread_list:
            t.join()
        for index, item in enumerate(thread_list):
            data_status[fw_list[index]] = item.get_result()

        for k, v in data_status.items():
            if '白' not in v:
                data_info['DescribeDomainFirewallList'] = operator + ':域名不在白名单'
                break
            else:
                data_info['DescribeDomainFirewallList'] = operator + ':域名在白名单'
        res = sc(code.Success)
        res.redata = data_info
        raise gen.Return(res)
