#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Gtlions Lai

from tornado import gen

from apps.common.apicom import get_ip_serialuuids
from apps.common.zx_firewall import Firewall
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class DeleteProtectGroupIP(ActionBase):
    '''从指定防护组删除IP'''

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
        ts = self.application.ts_begin
        ip = self.params['IP']
        ip_l = self.params['IP'].split(',')
        user_org = self.params['AccessKeyId']
        user_end = self.params['IPUserID'] if 'IPUserID' in self.params else None

        uuids_list, uuids_str, ips_list, ips_str = get_ip_serialuuids(user_org=user_org, user_end=user_end, ips=ip,
                                                                      status='open')
        if len(ip_l) != len(ips_list):
            ip_r = list(set(ip_l).difference(set(ips_list)))
            res = sc(code.IPNotUsed)
            res.result = res.result % str(','.join(ip_r))
            raise gen.Return(res)

        # status = False  ts_shut
        if uuids_str:
            sql = "SELECT host(ii.ip) ip,ii.serialnum,ii.status, ii.protect_base, ii.protect_max FROM t_ip_protect ii, t_protect pp, t_bandtype bb WHERE ii.serialnum IN (%s) AND ii.protect_base = pp.id AND pp.bandtype = bb.id"
            data = self.application.dbcur.queryall_dict(sql, (uuids_str.replace('"', ''),))

        if data:
            for i in data:
                del_fw_dict = self.delete_firewall_configs(ip)
                if len(del_fw_dict) != 0:
                    res = sc(code.CommitFail)
                    res.result = res.result % str(del_fw_dict)
                    raise gen.Return(res)
                white_info = dict()
                white_info['serialnum'] = i['serialnum']
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
                ip, serialnum,protect_base, protect_max, status = i['ip'], i['serialnum'], i['protect_base'], i['protect_max'], i['status']
                ip_info = dict()
                ip_info['ip'] = ip
                ip_info['status'] = False
                ip_info['ts_shut'] = ts
                self.application.dbcur.update_dict('t_ip_protect', ip_info, 'serialnum', serialnum)
                # sql = "INSERT INTO t_ip_protect_his (serialnum, ip, user_org, user_end, protect_base, protect_max, protect_state, protect_previous, ts_open, ts_shut, metric_pct_bps, metric_pct_pps, region, zone, status, cts, actions,iptype,bandtype ) SELECT serialnum, ip, user_org, user_end, protect_base, protect_max, protect_state, protect_previous, ts_open, ts_shut, metric_pct_bps, metric_pct_pps, region, zone, status, %s, %s,iptype,bandtype FROM t_ip_protect WHERE serialnum IN (%s)"
                # self.application.dbcur.execute(sql, (str(ts).replace('"', ''), action, uuids_str.replace('"', ''),))
                self.application.history_backup_t_ip_protect(
                    column_extra_value=",'{cts}','{action}'".format(cts=ts, action=action),
                    filter="serialnum='{serialnum}'".format(serialnum=uuids_str.replace('"', "")))
                sql = "delete from t_job where ip=%s and serialnum in (%s) AND actions<>'DeleteWhiteList'"
                self.application.dbcur.execute(sql, (str(ip), uuids_str.replace('"', ''),))
                self.application.dbcurflow.execute('delete from t_ip_credit where ip=%s;', (ip_info['ip'],))
        else:
            res = sc(code.IPNotUsed)
            res.result = res.result % ip
        raise gen.Return(res)
