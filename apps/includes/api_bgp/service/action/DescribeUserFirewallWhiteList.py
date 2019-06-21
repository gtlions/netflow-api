#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Gtlions Lai

from tornado import gen
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class DescribeUserFirewallWhiteList(ActionBase):
    '''查询用户防火墙白名单'''

    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        # self.application.logger.info(self.init_msg)

    @gen.coroutine
    def run(self):
        user_end = self.params['IPUserID']
        ip = self.params['IP'] if 'IP' in self.params else None
        packageid = self.params['PackageID'] if 'PackageID' in self.params else None
        domain = self.params['Domain'] if 'Domain' in self.params else None

        sqls = []
        sql = "SELECT ip,package_protect_id,hostname FROM t_firewall WHERE user_end=%s AND status>0"
        sqls.append(sql)
        sql = " and ip in ('" + ip + "')" if ip else ''
        sqls.append(sql)
        sql = " and package_protect_id in ('" + packageid + "')" if packageid else ''
        sqls.append(sql)
        if domain is None:
            sql = ''
        else:
            sql = " and types=2" if domain == 'True' else " and types=1"
        sqls.append(sql)
        sql_all = ''.join(sqls)
        data = self.application.dbcur.queryall_dict(sql_all, (user_end,))
        data_info = dict()
        data_info['UserWhiteListData'] = []
        hostname_dict = dict()
        hostname_list = []
        if data:
            if self.params['AccessKeyId'] == 'hsefbawrfg':
            # if self.params['AccessKeyId'] == 'dev1':
                for i in data:
                    hostname_dict[i['ip']] = []
                for i in data:
                    hostname_dict[i['ip']].append(i['hostname'])
            else:
                for i in data:
                    hostname_list.append(i['hostname'])
        if self.params['AccessKeyId'] == 'hsefbawrfg':
        # if self.params['AccessKeyId'] == 'dev1':
            data_info['UserWhiteListData'].append(hostname_dict)
        else:
            data_info['UserWhiteListData'].append(hostname_list)

        res = sc(code.Success)
        res.redata = data_info
        raise gen.Return(res)
