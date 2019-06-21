#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors    : Gtlions Lai

from tornado import gen

from apps.common.apicom import get_ip_serialuuids
from apps.common.statusconfig import code, statusconfig as sc
from apps.common.zx_firewall import Firewall
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class DeleteProtectPackageIP(ActionBase):
    '''删除高防防护包IP'''

    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        # self.application.logger.info(self.init_msg)

    def delete_firewall_configs(self, ip):
        fw_condition = {}
        firewall = Firewall(self.application.ccfirewall)
        if len(firewall.query_protect_serial_number(ip)) > 1:
            if firewall.set_protect_serial_number(ip, param_set='0', set_tcp='0'):
                pass
            else:
                fw_condition['cc防护'] = '删除CC防护配置失败'
        return fw_condition

    @gen.coroutine
    def run(self):
        res = sc(code.Success)
        res.result = 'Success'
        action = self.params['Action']
        packageid = self.params['PackageID']
        ips = self.params['IP']
        ip_l = self.params['IP'].split(',')
        user_org = self.params['AccessKeyId']
        user_end = self.params['IPUserID']

        uuids_list, uuids_str, ips_list, ips_str = get_ip_serialuuids(user_org=user_org, user_end=user_end, ips=ips,
                                                                      status='open')
        if len(ip_l) != len(ips_list):
            ip_r = list(set(ip_l).difference(set(ips_list)))
            res = sc(code.IPNotUsed)
            res.result = res.result % str(','.join(ip_r))
            raise gen.Return(res)

        ts = self.application.ts_begin
        for ip in ip_l:
            del_fw_dict = self.delete_firewall_configs(ip)
            if len(del_fw_dict) != 0:
                res = sc(code.CommitFail)
                res.result = res.result % str(del_fw_dict)
                raise gen.Return(res)
            white_info = dict()
            white_info['serialnum'] = packageid
            white_info['ts'] = white_info['ts_actions'] = ts
            white_info['p5'] = ip
            white_info['actions'] = 'DeleteWhiteList'
            sql = "select hostname,status from t_firewall where ip=%s and status>0"
            w_data = self.application.dbcur.queryall_dict(sql, (ip,))
            if w_data:
                for w in w_data:
                    white_info['p1'] = w['hostname']
                    white_info['p2'] = w['status']
                    self.application.dbcur.insert_dict('t_job', white_info)
            proxy_sql = "UPDATE t_slb_four_layer SET configtype = 'Del' WHERE ip=%s;UPDATE t_slb_seven_layer SET configtype = 'Del' WHERE ip=%s"
            self.application.dbcur.execute(proxy_sql, (ip, ip,))
            self.application.dbcurflow.execute('delete from t_ip_credit where ip=%s;', (ip,))

        for uuid in uuids_list:
            ts = self.application.ts_begin
            sql = 'update t_ip_protect set (ts_shut,status)=(%s,False) where serialnum=%s and status=TRUE;'
            self.application.dbcur.execute(sql, (ts, uuid,))
            self.application.history_backup_t_ip_protect(column_extra_value=",'{cts}','{action}'".format(cts=ts, action=action),
                                                         filter="serialnum='{serialnum}'".format(serialnum=uuid))

        raise gen.Return(res)
