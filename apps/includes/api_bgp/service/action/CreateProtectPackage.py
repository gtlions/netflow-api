#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors    : Gtlions Lai <gtlions.l@qq.com>
import re
import uuid
from tornado import gen
import datetime
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class CreateProtectPackage(ActionBase):
    '''创建高防防护包'''

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
        packagename = self.params['PackageName']
        protect_base = self.params['GuaranteeProtectGroupID']
        protect_max = self.params['ElasticProtectGroupID']
        bandtype = self.params['BandwithType']
        LifeDay = self.params['LifeDay']
        ipnums = self.params['IPNums']
        user_org = self.params['AccessKeyId']
        user_end = self.params['IPUserID'] if 'IPUserID' in self.params else None

        value = re.compile(r'^[1-9]?[0-9]+$')
        result = value.match(LifeDay)
        if not result:
            res = sc(code.ParamError)
            res.result = res.result % '请检查LifeDay参数'
            raise gen.Return(res)

        value = re.compile(r'^[1-9]?[0-9]+$')
        result = value.match(ipnums)
        if not result:
            res = sc(code.ParamError)
            res.result = res.result % '请检查ipnums参数'
            raise gen.Return(res)

        if not str(bandtype) == 'AntiBGP':
            res = sc(code.ParamError)
            res.result = res.result % 'bandtype必须是AntiBGP'
            raise gen.Return(res)

        if int(ipnums) > 256:
            res = sc(code.IPNumsError)
            res.result = res.result % ipnums
            raise gen.Return(res)
        serialnum = str(uuid.uuid1())
        ts = self.application.ts_begin
        t_package_protect_info = {}
        t_package_protect_info['ipnums'] = ipnums
        t_package_protect_info['package_protect_id'] = serialnum
        t_package_protect_info['package_protect_name'] = packagename
        t_package_protect_info['user_org'] = user_org
        t_package_protect_info['user_end'] = user_end
        t_package_protect_info['protect_base'] = \
            self.application.dbcur.queryone(
                "select id from t_protect where protect_id=%s;",
                (protect_base,))[0]
        t_package_protect_info['protect_max'] = \
            self.application.dbcur.queryone(
                "select id from t_protect where protect_id=%s;",
                (protect_max,))[0]

        t_package_protect_info['protect_state'] = 2
        t_package_protect_info['ts_open'] = ts
        t_package_protect_info['ts_due'] = due_time = ts + datetime.timedelta(days=int(LifeDay))
        t_package_protect_info['serialnum'] = serialnum
        t_package_protect_info['status'] = True
        self.application.dbcur.insert_dict('t_package_protect', t_package_protect_info)
        # sql = 'insert into t_package_protect_his(ts_due,protect_base,protect_max,package,ipnums,package_protect_id,package_protect_name,user_org,user_end,protect_state,ts_open,ts_shut,serialnum,status,cts,actions) select ts_due,protect_base,protect_max,package,ipnums,package_protect_id,package_protect_name,user_org,user_end,protect_state,ts_open,ts_shut,serialnum,status,%s,%s from t_package_protect where serialnum=%s;'
        # self.application.dbcur.execute(sql, (ts, action, serialnum))
        self.application.history_backup_t_package_protect(
            column_extra_value=",'{cts}','{action}'".format(cts=ts, action=action),
            filter="serialnum='{serialnum}'".format(serialnum=serialnum))
        data_info = {}
        due_time_utc = str(due_time - datetime.timedelta(hours=8)).split('.')[0].replace(' ', 'T') + 'Z'

        data_info['ProtectPackageInfo'] = {'PackageID': str(serialnum), 'Due_Time': str(due_time_utc)}
        res.redata = data_info

        raise gen.Return(res)
