#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from tornado import gen
from apps.common.zx_firewall import Firewall
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class AddProtectGroupIP(ActionBase):
    '''添加IP到指定的防护组'''

    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        # self.application.logger.info(self.init_msg)

    @gen.coroutine
    def run(self):
        res = sc(code.Success)
        res.result = 'Success'

        action = self.params['Action']
        ts = self.application.ts_begin
        ip_s = self.params['IP']
        ip_l = self.params['IP'].split(',')
        user_org = self.params['AccessKeyId']
        user_end = self.params['IPUserID'] if 'IPUserID' in self.params else None
        protect_base = self.params['guaranteeProtectGroupID']
        protect_max = self.params['elasticProtectGroupID']
        bandtype = self.params['BandwithType']
        region = self.params['Region']
        zone = self.params['Zone']

        sql = 'SELECT ip FROM t_ip_protect where ip in %s and status=True'
        data = self.application.dbcur.queryall_dict(sql, (tuple(self.makeinet(x) for x in ip_l),))
        ip_check = [x['ip'].addr for x in data]
        if ip_check:
            res = sc(code.IPConflict)
            res.result = res.result % ','.join(ip_check)
            raise gen.Return(res)
        gua_sql = "SELECT id FROM t_protect WHERE protect_id=%s"
        ela_sql = "SELECT id FROM t_protect WHERE protect_id=%s"
        gua_id = self.application.dbcur.queryone(gua_sql, (protect_base,))
        ela_id = self.application.dbcur.queryone(ela_sql, (protect_max,))
        if gua_id[0] > ela_id[0]:
            res = sc(code.ParamError)
            res.result = res.result % '保底需小于弹性'
            raise gen.Return(res)
        for ip in ip_l:
            t_ip_protect_data = {}
            t_ip_protect_data['ip'] = self.makeinet(ip)
            t_ip_protect_data['user_org'] = user_org
            t_ip_protect_data['user_end'] = user_end if user_end else None
            t_ip_protect_data['protect_base'] = \
                self.application.dbcur.queryone(
                    "select protect from v_protect where protect_id=%s and bandtype_id=%s;",
                    (protect_base, bandtype))[0]
            t_ip_protect_data['protect_max'] = \
                self.application.dbcur.queryone(
                    "select protect from v_protect where protect_id=%s and bandtype_id=%s;",
                    (protect_max, bandtype))[0]
            t_ip_protect_data['protect_state'] = 2
            t_ip_protect_data['ts_open'] = ts
            t_ip_protect_data['region'] = \
                self.application.dbcur.queryone("select id from t_region where region_id=%s;", (region,))[0]
            t_ip_protect_data['zone'] = \
                self.application.dbcur.queryone("select id from t_zone where zone_id=%s;", (zone,))[0]
            serialnum = str(uuid.uuid1())
            t_ip_protect_data['serialnum'] = serialnum
            t_ip_protect_data['iptype'] = 0
            t_ip_protect_data['status'] = True
            t_ip_protect_data['bandtype'] = self.application.dbcur.queryone(
                    "select id from t_bandtype where bandtype_id=%s;",
                    (bandtype,))[0]

            self.application.dbcur.insert_dict('t_ip_protect', t_ip_protect_data)
            self.application.dbcurflow.execute('delete from t_ip_credit where ip=%s;',(t_ip_protect_data['ip'],))
            self.application.dbcurflow.execute('insert into t_ip_credit(uts,ip,points) values(%s,%s,%s)',(ts,t_ip_protect_data['ip'],self.application.dbcur.queryone('select max_bps_in/1000/1000/1000 from t_protect where id=%s;',(t_ip_protect_data['protect_base'],))[0]))
            firewall = Firewall(self.application.ccfirewall)
            firewall.set_protect_serial_number(ip, param_set='0')
            # sql = 'insert into t_ip_protect_his(ip,user_org,user_end,protect_base,protect_max,protect_state,ts_open,ts_shut,metric_pct_bps,metric_pct_pps,region,zone,serialnum,cts,actions,iptype,bandtype) select ip,user_org,user_end,protect_base,protect_max,protect_state,ts_open,ts_shut,metric_pct_bps,metric_pct_pps,region,zone,serialnum,%s,%s,iptype,bandtype from t_ip_protect where serialnum=%s;'
            # self.application.dbcur.execute(sql, (ts, action, serialnum))

            self.application.history_backup_t_ip_protect(column_extra_value=",'{cts}','{action}'".format(cts=ts, action=action),
                                                         filter="serialnum='{serialnum}'".format(serialnum=serialnum))
        raise gen.Return(res)