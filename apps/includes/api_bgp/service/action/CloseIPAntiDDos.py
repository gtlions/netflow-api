#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @Author: Gtlions Lai

import logging

from tornado import gen
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase
from apps.common.apicom import get_ip_serialuuids
import json

class CloseIPAntiDDos(ActionBase):
    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        #self.application.logger.info(self.init_msg)



    @gen.coroutine
    def run(self):
        res = sc(code.Success)
        res.result = 'Success'

        action = self.params['Action']
        ts = self.application.ts_begin
        ip = self.params['IP']
        ip_s = self.params['IP']
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

        sql = 'SELECT host(ip) AS ip FROM t_ip_protect WHERE serialnum IN (%s) AND protect_state=0'
        data = self.application.dbcur.queryall_dict(sql, (uuids_str.replace('"', ""),))

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
            ip_info['protect_state'] = 0
            # sql_1 = "SELECT protect_base, protect_max FROM t_ip_protect WHERE serialnum in (%s)"
            # data = self.application.dbcur.queryall_dict(sql_1, (uuids_str.replace('"', ''),))[0]
            # ip_info['protect_previous'] = json.dumps(data)
            # sql_2 = "SELECT bandtype_id FROM t_ip_protect INNER JOIN t_bandtype ON t_bandtype.id = t_ip_protect.bandtype WHERE serialnum in (%s)"
            # bandtype = self.application.dbcur.queryall(sql_2, (uuids_str.replace('"', ''),))[0]
            # band_free = bandtype[0].lower()+'free'
            # sql_3 = "SELECT id FROM t_protect WHERE protect_id=%s"
            # ip_info['protect_base'] = ip_info['protect_max'] = self.application.dbcur.queryall(sql_3, (band_free,))[0][0]
            self.application.dbcur.update_dict('t_ip_protect', ip_info, 'serialnum', uuids_str.replace('"', ''))
            # sql = 'INSERT INTO t_ip_protect_his (ip,user_org,user_end,protect_base,protect_max,protect_previous,ts_open,ts_shut,metric_pct_pps,metric_pct_bps,region,zone,serialnum,status,cts,actions,protect_state,iptype,bandtype) SELECT ip,user_org,user_end,protect_base,protect_max,protect_previous,ts_open,ts_shut,metric_pct_pps,metric_pct_bps,region,zone,serialnum,status,%s,%s,protect_state,iptype,bandtype FROM t_ip_protect WHERE serialnum = %s'
            # self.application.dbcur.execute(sql, (ts, action, uuids_str.replace('"', ""),))
            self.application.history_backup_t_ip_protect(column_extra_value=",'{cts}','{action}'".format(cts=ts, action=action),
                                                         filter="serialnum='{serialnum}'".format(serialnum=uuids_str.replace('"', "")))
        else:
            res = sc(code.IPNotUsed)
            res.result = res.result % ip_s
        raise gen.Return(res)
