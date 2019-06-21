#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @Author: Gtlions Lai

from tornado import gen

from apps.common.apicom import get_ip_serialuuids
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class CloseIPElasticAntiDDos(ActionBase):
    '''关闭IP的弹性流量服务'''

    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        #self.application.logger.info(self.init_msg)

    @gen.coroutine
    def run(self):
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

        sql = "select host(ip) ip from t_ip_protect where serialnum in (%s) and protect_state in (0,1)"
        data = self.application.dbcur.queryall_dict(sql, (uuids_str.replace('"', ''),))
        if data:
            ip_r = [x['ip'] for x in data]
            if ip_r:
                res = sc(code.NotInCorrectStatus)
                res.result = res.result % ip
                raise gen.Return(res)

        if uuids_str:
            sql = "SELECT protect_state FROM t_ip_protect WHERE serialnum in (%s)"
            data = self.application.dbcur.queryall_dict(sql, (uuids_str.replace('"', ''),))

        if data:
            ip_info = {}
            ip_info['protect_state'] = 1
            self.application.dbcur.update_dict('t_ip_protect', ip_info, 'serialnum', uuids_str.replace('"', ''))
            # sql = "insert into (serialnum, ip, user_org, user_end, protect_base, protect_max, protect_state, protect_previous, ts_open, ts_shut, metric_pct_bps, metric_pct_pps, region, zone, status, cts, actions,iptype,bandtype) SELECT serialnum, ip, user_org, user_end, protect_base, protect_max, protect_state, protect_previous, ts_open, ts_shut, metric_pct_bps, metric_pct_pps, region, zone, status, %s, %s,iptype,bandtype FROM t_ip_protect WHERE serialnum IN (%s)"
            # self.application.dbcur.execute(sql, (str(ts).replace('"', ''), action, uuids_str.replace('"', ''),))
            self.application.history_backup_t_ip_protect(column_extra_value=",'{cts}','{action}'".format(cts=ts, action=action),
                                                         filter="serialnum='{serialnum}'".format(serialnum=uuids_str.replace('"', "")))

            res = sc(code.Success)
            res.result = 'Success'
        else:
            res = sc(code.DataNotConform)
            res.result = res.result % ip
        raise gen.Return(res)
