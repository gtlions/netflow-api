#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors    : Gtlions Lai <gtlions.l@qq.com>
import uuid
from tornado import gen, netutil
from apps.common.zx_firewall import Firewall
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class AddProtectPackageIP(ActionBase):
    '''添加高防防护包IP'''

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
        packageid = self.params['PackageID']
        ip_l = self.params['IP'].split(',')
        ts = self.application.ts_begin
        user_org = self.params['AccessKeyId']
        user_end = self.params['IPUserID'] if 'IPUserID' in self.params else None

        sql = 'select id from t_package_protect where package_protect_id=%s and user_org=%s and user_end=%s and protect_state in (1,2) and status=True; '
        package = self.application.dbcur.queryall(sql, (packageid, user_org, user_end))
        if not package:
            res = sc(code.PackageStatusError)
            res.result = res.result % '请先改变高防包服务状态'
            raise gen.Return(res)

        sql = 'select (select ipnums from t_package_protect where package_protect_id=%s and status=True)-count(ip)-%s from t_ip_protect where package=%s and user_org=%s and user_end=%s and status=True;'
        self.application.dbcur.execute(sql, (packageid, len(ip_l), package[0][0], user_org, user_end))
        ip_left = self.application.dbcur.fetchall()
        if ip_left[0][0] < 0:
            res = sc(code.IPNumsError)
            res.result = res.result % '添加ip数量超过上限'
            raise gen.Return(res)

        sql = 'SELECT host(ip) AS ip FROM t_ip_protect WHERE ip in %s and status=True;'
        data = self.application.dbcur.queryall_dict(sql, (tuple(self.makeinet(x) for x in ip_l),))
        if data:
            ip_r = [x['ip'] for x in data]
            if ip_r:
                res = sc(code.NotCorrectStatus)
                res.result = res.result % ip_r
                raise gen.Return(res)

        for ip in ip_l:
            t_ip_protect_data = {}
            t_ip_protect_data['ip'] = self.makeinet(ip)
            t_ip_protect_data['user_org'] = user_org
            t_ip_protect_data['user_end'] = user_end if user_end else None
            t_ip_protect_data['protect_base'] = \
                self.application.dbcur.queryone(
                    "select protect_base from t_package_protect where package_protect_id=%s;",
                    (packageid,))[0]
            t_ip_protect_data['protect_max'] = \
                self.application.dbcur.queryone(
                    "select protect_max from t_package_protect where package_protect_id=%s;",
                    (packageid,))[0]
            t_ip_protect_data['protect_state'] = 2
            t_ip_protect_data['ts_open'] = ts
            serialnum = str(uuid.uuid1())
            t_ip_protect_data['serialnum'] = serialnum
            t_ip_protect_data['iptype'] = 0
            t_ip_protect_data['status'] = True
            band_type = self.application.dbcur.queryone(
                "select bandtype from t_protect where id=%s;",
                (t_ip_protect_data['protect_base'],))[0]
            t_ip_protect_data['bandtype'] = band_type
            t_ip_protect_data['package'] = package[0][0]

            self.application.dbcur.insert_dict('t_ip_protect', t_ip_protect_data)
            self.application.history_backup_t_ip_protect(column_extra_value=",'{cts}','{action}'".format(cts=ts, action=action),
                                                         filter="serialnum='{serialnum}'".format(serialnum=serialnum))
            # sql = 'insert into t_ip_protect_his(ip,package,user_org,user_end,protect_base,protect_max,protect_state,ts_open,ts_shut,metric_pct_bps,metric_pct_pps,region,zone,serialnum,cts,actions,iptype,bandtype) select ip,package,user_org,user_end,protect_base,protect_max,protect_state,ts_open,ts_shut,metric_pct_bps,metric_pct_pps,region,zone,serialnum,%s,%s,iptype,bandtype from t_ip_protect where serialnum=%s;'
            # self.application.dbcur.execute(sql, (ts, action, serialnum))
            self.application.dbcurflow.execute('delete from t_ip_credit where ip=%s;', (t_ip_protect_data['ip'],))
            self.application.dbcurflow.execute('insert into t_ip_credit(uts,ip,points) values(%s,%s,%s)', (
            ts, t_ip_protect_data['ip'],
            self.application.dbcur.queryone('select max_bps_in/1000/1000/1000 from t_protect where id=%s;',
                                            (t_ip_protect_data['protect_base'],))[0]))
            firewall = Firewall(self.application.ccfirewall)
            firewall.set_protect_serial_number(ip, param_set='0')
        raise gen.Return(res)
