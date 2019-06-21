#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors    : Gtlions Lai
from tornado import gen
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase
import datetime,re


class ExtendProtectPackageDueTime(ActionBase):
    '''延长高防防护包期限'''

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
        LifeDay = self.params['LifeDay']
        value = re.compile(r'^[1-9]?[0-9]+$')
        result = value.match(LifeDay)
        if not result:
            res = sc(code.ParamError)
            res.result = res.result % '请检查LifeDay参数'
            raise gen.Return(res)

        sql = 'select ts_due,id from t_package_protect WHERE package_protect_id=%s'
        due_time_package = self.application.dbcur.queryone_dict(sql, (packageid, ))[0]
        ts = self.application.ts_begin
        if due_time_package['ts_due'] > ts:
            due_time = due_time_package['ts_due'] + datetime.timedelta(days=int(LifeDay))
            sql = 'update t_package_protect set (protect_state, ts_due)=(2, %s) where package_protect_id=%s and status=TRUE;'
            self.application.dbcur.execute(sql, (due_time, packageid,))
            sql = 'update t_ip_protect set protect_state=2 where package=(SELECT id from t_package_protect WHERE package_protect_id=%s) and status=TRUE;'
            self.application.dbcur.execute(sql, ( packageid,))
        else:
            due_time = ts + datetime.timedelta(days=int(LifeDay))
            sql = 'update t_package_protect set (ts_open, ts_due, protect_state)=(%s, %s, 2) where package_protect_id=%s and status=TRUE;'
            self.application.dbcur.execute(sql, (ts, due_time, packageid, ))
            sql = 'update t_ip_protect set (ts_open, protect_state)=(%s, 2) where package=(SELECT id from t_package_protect WHERE package_protect_id=%s) and status=TRUE;'
            self.application.dbcur.execute(sql, (ts, packageid,))

        self.application.history_backup_t_ip_protect(
            column_extra_value=",'{cts}','{action}'".format(cts=ts, action=action),
            filter="package='{package}'".format(package=due_time_package['id']))
        self.application.history_backup_t_package_protect(
            column_extra_value=",'{cts}','{action}'".format(cts=ts, action=action),
            filter="package_protect_id='{packageid}'".format(packageid=packageid))
        due_time_utc = str(due_time - datetime.timedelta(hours=8)).split('.')[0].replace(' ', 'T') + 'Z'

        data_info = {}
        data_info['ProtectPackageInfo'] = {'PackageID': str(packageid), 'Due_Time': str(due_time_utc)}
        res.redata = data_info
        raise gen.Return(res)
