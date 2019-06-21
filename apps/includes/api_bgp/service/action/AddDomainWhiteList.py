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


class AddDomainWhiteList(ActionBase):
    '''添加防火墙域名白名单'''

    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        # self.application.logger.info(self.init_msg)

    def add_domain(self, operator, hostname, data_add, user_dict):
        firewall = ZhiFirewall(operator) if operator in self.application.zhifirewalllist else Firewall(operator)
        if data_add:
            if str(user_dict)[:-1] in str(data_add[0]):
                # 本人加的
                if firewall.add_domain_name(hostname):
                    return hostname + ':域名添加至白名单'
                else:
                    return sc(code.FirewallConnFail).result % hostname
            else:
                return sc(code.DomainError).result % hostname
        else:
            # 没有人有加
            if firewall.add_domain_name(hostname):
                return hostname + ':域名添加至白名单'
            else:
                return sc(code.FirewallConnFail).result % hostname

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

        if netutil.is_valid_ip(hostname):
            res = sc(code.ParamError)
            res.result = res.result % hostname
            raise gen.Return(res)
        if ip is None and package_id is None:
            res = sc(code.ParamError)
            res.result = res.result % 'IP与包ID至少择一提交'
            raise gen.Return(res)

        num_sql = "SELECT count(1) FROM t_firewall WHERE user_end=%s AND types=2 AND status>0"
        if ip is None:
            num_sql = num_sql + "AND package_protect_id=%s;"
            num_data = self.application.dbcur.queryall_dict(num_sql, (user_end, package_id,))
        elif package_id is None:
            num_sql = num_sql + "AND ip=%s;"
            num_data = self.application.dbcur.queryall_dict(num_sql, (user_end, ip,))
        else:
            num_sql = num_sql + "AND ip=%s AND package_protect_id=%s;"
            num_data = self.application.dbcur.queryall_dict(num_sql, (user_end, ip, package_id,))
        if num_data[0]['count'] > self.application.wlmaxvalue[1]:
            res = sc(code.MaxWhiteList)
            raise gen.Return(res)

        data_info = {}
        data_status = {}
        thread_list = []
        status_num = 0
        user_dict = {'user_org': user_org, 'user_end': user_end, 'ip': ip, 'package_protect_id': package_id}
        condition = 0

        fw_list = self.application.firewalllist if operator == 'bgp' else [self.application.ccfirewall, operator]
        for i in fw_list:
            firewall = ZhiFirewall(i) if i in self.application.zhifirewalllist else Firewall(i)
            condition += 2**firewall.number
        if len(data_add) != 0:
            if condition != data_add[0]['status']:
                res = sc(code.ParamError)
                res.result = res.result % operator
                raise gen.Return(res)
        for i in fw_list:
            t = MyThread(self.add_domain, args=(i, hostname, data_add, user_dict))
            thread_list.append(t)
        for t in thread_list:
            t.start()
        for t in thread_list:
            t.join()
        for index, item in enumerate(thread_list):
            data_status[fw_list[index]] = item.get_result()

        for k, v in data_status.items():
            if '添加至' in v:
                firewall = ZhiFirewall(k) if k in self.application.zhifirewalllist else Firewall(k)
                status_num = status_num ^ 2**firewall.number
                sql = "select user_org,user_end,ip,package_protect_id from t_firewall WHERE hostname=%s"
                data = self.application.dbcur.queryall_dict(sql, (hostname,))
                if user_dict in data:
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
                    white_info = {'user_org': user_org, 'user_end': user_end, 'ip': ip,
                                  'package_protect_id': package_id, 'hostname': hostname, 'types': 2,
                                  'status': status_num, 'createdt': ts}
                    self.application.dbcur.insert_dict('t_firewall', white_info)
            else:
                condition = ''

        if isinstance(condition, int):
            data_info['AddDomainWhiteList'] = operator + ':域名添加至白名单'
            res = sc(code.Success)
            res.redata = data_info
        else:
            res = sc(code.ChangeFail)
            res.result = res.result % {operator + ':此域名已被他人配置'}
        raise gen.Return(res)
