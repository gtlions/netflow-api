#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Gtlions Lai


from tornado import gen
from apps.common.zx_firewall import Firewall
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class DescribeIPFirewallProtect(ActionBase):
    '''查询防火墙防护策略'''

    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        # self.application.logger.info(self.init_msg)

    @gen.coroutine
    def run(self):
        ip = self.params['IP']

        data_info = dict()
        data_info['DescribeIPFirewallProtectData'] = dict()
        firewall = Firewall(self.application.ccfirewall)
        protect_dict = firewall.query_protect_serial_number(ip)
        try:
            param_set = self.application.param_set_dict[protect_dict['param_set']]
            port_tcp = self.application.port_tcp_dict[protect_dict['PortTCP']]
        except KeyError:
            res = sc(code.IPNotExist)
            res.result = res.result % ip
            raise gen.Return(res)
        # if param_set == '0':
        #     result = 'loose'
        # elif param_set == '1':
        #     result = 'medium'
        # elif param_set == '2':
        #     result = 'tight'
        if int(param_set) > 2:
            param_set = 'Not in correct global protect level'
        if int(port_tcp) > 2:
            port_tcp = 'Not in correct web protect level'
        data_info['DescribeIPFirewallProtectData']['GlobalProtectLevel'] = param_set
        data_info['DescribeIPFirewallProtectData']['WebProtectLevel'] = port_tcp

        res = sc(code.Success)
        res.redata = data_info
        raise gen.Return(res)
