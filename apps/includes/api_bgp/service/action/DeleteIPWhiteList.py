#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Gtlions Lai

from tornado import gen, netutil
from apps.common.zx_firewall import Firewall
from apps.common.zhi_firewall import ZhiFirewall
from apps.common.my_thread import MyThread
from apps.common.statusconfig import code
from apps.common.statusconfig import statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class DeleteIPWhiteList(ActionBase):
    '''删除防火墙IP白名单'''

    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        # self.application.logger.info(self.init_msg)

    def del_ip(self, operator, hostname, data_add, user_dict):
        firewall = ZhiFirewall(operator) if operator in self.application.zhifirewalllist else Firewall(operator)
        if str(user_dict)[:-1] in str(data_add[0]):
            if firewall.del_white_list(hostname):
                return hostname + ':IP从白名单删除'
            else:
                return sc(code.FirewallConnFail).result % hostname
        else:
            return sc(code.IPError).result % hostname

    @gen.coroutine
    def run(self):
        operator = self.params['Operator']
        hostname = self.params['Hostname']
        user_org = self.params['AccessKeyId']
        user_end = self.params['IPUserID']
        ip = self.params['IP'] if 'IP' in self.params else None
        package_id = self.params['PackageID'] if 'PackageID' in self.params else None
        ts = self.application.ts_begin
        sql = "select user_org,user_end,ip,package_protect_id,status from t_firewall WHERE hostname=%s and status>0"
        data_add = self.application.dbcur.queryall_dict(sql, (hostname,))

        if not netutil.is_valid_ip(hostname):
            res = sc(code.ParamError)
            res.result = res.result % hostname
            raise gen.Return(res)
        if len(data_add) == 0:
            res = sc(code.PermissionDenied)
            res.result = res.result % hostname
            raise gen.Return(res)
        if ip is None and package_id is None:
            res = sc(code.ParamError)
            res.result = res.result % 'IP与包ID至少择一提交'
            raise gen.Return(res)

        data_info = {}
        data_status = {}
        thread_list = []
        status_num = data_add[0]['status']
        user_dict = {'user_org': user_org, 'user_end': user_end, 'ip': ip, 'package_protect_id': package_id}
        condition = 0

        fw_list = self.application.firewalllist if operator == 'bgp' else [self.application.ccfirewall, operator]
        for i in fw_list:
            fw_num = ZhiFirewall(i) if i in self.application.zhifirewalllist else Firewall(i)
            condition += 2 ** fw_num.number
        if condition != status_num:
            res = sc(code.ParamError)
            res.result = res.result % operator
            raise gen.Return(res)
        for i in fw_list:
            t = MyThread(self.del_ip, args=(i, hostname, data_add, user_dict))
            thread_list.append(t)
        for t in thread_list:
            t.start()
        for t in thread_list:
            t.join()
        for index, item in enumerate(thread_list):
            data_status[fw_list[index]] = item.get_result()

        for k, v in data_status.items():
            if '删除' in v:
                firewall = ZhiFirewall(k) if k in self.application.zhifirewalllist else Firewall(k)
                status_num = status_num ^ 2**firewall.number
                if ip is None:
                    update_sql = 'UPDATE t_firewall SET status=%s, updatedt=%s WHERE user_org=%s AND user_end=%s AND hostname=%s AND ip IS NULL AND package_protect_id=%s'
                    self.application.dbcur.execute(update_sql,
                                                   (status_num, ts, user_org, user_end, hostname, package_id,))
                elif package_id is None:
                    update_sql = 'UPDATE t_firewall SET status=%s, updatedt=%s WHERE user_org=%s AND user_end=%s AND hostname=%s AND ip=%s AND package_protect_id IS NULL'
                    self.application.dbcur.execute(update_sql, (status_num, ts, user_org, user_end, hostname, ip,))
                else:
                    update_sql = 'UPDATE t_firewall SET status=%s, updatedt=%s WHERE user_org=%s AND user_end=%s AND hostname=%s AND ip=%s AND package_protect_id=%s'
                    self.application.dbcur.execute(update_sql,
                                                   (status_num, ts, user_org, user_end, hostname, ip, package_id,))
            else:
                condition = ''

        if isinstance(condition, int):
            data_info['DeleteIPWhiteList'] = operator + ':IP从白名单删除'
            res = sc(code.Success)
            res.redata = data_info
        else:
            data_info['DeleteIPWhiteList'] = operator + ':此IP已被他人配置'
            res = sc(code.ChangeFail)
            res.result = res.result % data_info
        raise gen.Return(res)
