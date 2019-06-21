#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Gtlions Lai

from tornado import gen, netutil

from apps.common.zx_firewall import Firewall
from apps.common.my_thread import MyThread
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class ResetBlockIP(ActionBase):
    '''释放防火墙屏蔽IP'''

    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        # self.application.logger.info(self.init_msg)

    def reset_block(self, source_ip, remote_ip, operator,):
        firewall = Firewall(operator)
        if firewall.reset_block_list(source_ip, remote_ip):
            return 200
        else:
            return 408

    @gen.coroutine
    def run(self):
        source_ip = self.params['SourceIP']
        remote_ip = self.params['RemoteIP']
        operator = self.params['Operator']
        user_org = self.params['AccessKeyId']
        user_end = self.params['IPUserID'] if 'IPUserID' in self.params else None
        ts = self.application.ts_begin
        if not (netutil.is_valid_ip(source_ip) and netutil.is_valid_ip(remote_ip)):
            res = sc(code.ParamError)
            raise gen.Return(res)

        data_info = {}
        data_info['ResetBlockIPData'] = []
        data_status = {}
        thread_list = []
        condition = 0

        fw_list = self.application.firewalllist if operator == 'bgp' else [self.application.ccfirewall, operator]
        for i in fw_list:
            t = MyThread(self.reset_block, args=(i, source_ip))
            thread_list.append(t)
        for t in thread_list:
            t.start()
        for t in thread_list:
            t.join()
        for index, item in enumerate(thread_list):
            data_status[fw_list[index]] = item.get_result()

        for k, v in data_status.items():
            if v != 200:
                condition = ''

        if isinstance(condition, int):
            data_info['ResetBlockIPData'] = operator + ':屏蔽列表已重置'
            res = sc(code.Success)
            res.redata = data_info
        else:
            res = sc(code.ChangeFail)
            res.result = res.result % {operator + ':屏蔽列表重置失败'}
        raise gen.Return(res)
