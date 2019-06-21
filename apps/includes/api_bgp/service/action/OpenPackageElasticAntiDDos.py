#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors    : Gtlions Lai
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase
from tornado import gen


class OpenPackageElasticAntiDDos(ActionBase):
    '''开启高防防护包弹性防护'''

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
        user_org = self.params['AccessKeyId']
        user_end = self.params['IPUserID']

        sql = 'select id from t_package_protect where package_protect_id=%s and user_org=%s and user_end=%s and status=True;'
        self.application.dbcur.execute(sql, (packageid, user_org, user_end))
        package = self.application.dbcur.fetchall()
        if not package:
            res = sc(code.PackageNotExist)
            res.result = res.result % '请检查PackageID或IPUserID'
            raise gen.Return(res)

        sql = "select package_protect_id from t_package_protect where package_protect_id=%s and protect_state =2"
        data = self.application.dbcur.queryall_dict(sql, (packageid,))
        if data:
            res = sc(code.NotInCorrectStatus)
            res.result = res.result % packageid
            raise gen.Return(res)

        ts = self.application.ts_begin

        sql = 'update t_package_protect set protect_state=2 where package_protect_id=%s and status=TRUE;'
        self.application.dbcur.execute(sql, (packageid, ))
        sql = 'update t_ip_protect set protect_state=2 where package=%s and status=TRUE;'
        self.application.dbcur.execute(sql, (package[0][0], ))
        # sql = 'INSERT INTO t_ip_protect_his (ip,package,user_org,user_end,protect_base,protect_max,protect_previous,' \
        #       'ts_open,ts_shut,metric_pct_pps,metric_pct_bps,region,zone,serialnum,status,cts,actions,protect_state,' \
        #       'iptype,bandtype) ' \
        #       'SELECT ip,package,user_org,user_end,protect_base,protect_max,protect_previous,ts_open,ts_shut,' \
        #       'metric_pct_pps,metric_pct_bps,region,zone,serialnum,status,%s,%s,protect_state,iptype,bandtype ' \
        #       'FROM t_ip_protect WHERE package =%s;'
        # self.application.dbcur.execute(sql, (ts, action, package[0][0], ))
        self.application.history_backup_t_ip_protect(
            column_extra_value=",'{cts}','{action}'".format(cts=ts, action=action),
            filter="package='{package}'".format(package=package[0][0]))

        # sql = 'INSERT INTO t_package_protect_his ' \
        #       '(package,ipnums,package_protect_id,package_protect_name,user_org,user_end,protect_state,ts_open,' \
        #       'ts_shut,serialnum,status,cts,actions) SELECT package,ipnums,package_protect_id,package_protect_name,' \
        #       'user_org,user_end,protect_state,ts_open,ts_shut,serialnum,status,%s,%s' \
        #       'FROM t_package_protect WHERE package =%s;'
        # self.application.dbcur.execute(sql, (ts, action,  package[0][0],))
        self.application.history_backup_t_package_protect(
            column_extra_value=",'{cts}','{action}'".format(cts=ts, action=action),
            filter="package_protect_id='{packageid}'".format(packageid=packageid))

        raise gen.Return(res)
