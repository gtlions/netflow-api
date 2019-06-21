#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors    : Gtlions Lai

from tornado import gen

from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class DeleteProtectPackage(ActionBase):
    '''删除高防防护包'''

    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        # self.application.logger.info(self.init_msg)

    @gen.coroutine
    def run(self):
        res = sc(code.Success)
        res.result = 'Success'
        actions = self.params['Action']
        packageid = self.params['PackageID']
        user_org = self.params['AccessKeyId']
        user_end = self.params['IPUserID'] if 'IPUserID' in self.params else None

        sql = 'select id from t_package_protect where package_protect_id=%s and user_org=%s and user_end=%s and status=True;'
        self.application.dbcur.execute(sql, (packageid, user_org, user_end))
        package = self.application.dbcur.fetchall()
        if not package:
            res = sc(code.PackageStatusError)
            res.result = res.result % '请检查服务包状态'
            raise gen.Return(res)

        sql = 'select host(ip) as ip from t_ip_protect where package=%s and status=True;'
        self.application.dbcur.execute(sql, (package[0][0],))
        data = self.application.dbcur.fetchall()
        if data:
            res = sc(code.PackageIPError)
            res.result = res.result % data
            raise gen.Return(res)

        ts = self.application.ts_begin

        white_info = dict()
        white_info['serialnum'] = packageid
        white_info['ts'] = white_info['ts_actions'] = ts
        white_info['p5'] = packageid
        white_info['actions'] = 'DeleteWhiteList'
        sql = "select hostname,status from t_firewall where package_protect_id=%s and status>0"
        w_data = self.application.dbcur.queryall_dict(sql, (packageid,))
        if w_data:
            for w in w_data:
                white_info['p1'] = w['hostname']
                white_info['p2'] = w['status']
                self.application.dbcur.insert_dict('t_job', white_info)

        sql = 'update t_package_protect set (ts_shut,status)=(%s,False) where package_protect_id=%s and status=TRUE;'
        self.application.dbcur.execute(sql, (ts, packageid,))
        self.application.history_backup_t_package_protect(
            column_extra_value=",'{cts}','{action}'".format(cts=ts, action=actions),
            filter="package_protect_id='{packageid}'".format(packageid=packageid))

        sql = "delete from t_job where serialnum=%s AND actions<>'DeleteWhiteList'"
        self.application.dbcur.execute(sql, (packageid,))
        raise gen.Return(res)
