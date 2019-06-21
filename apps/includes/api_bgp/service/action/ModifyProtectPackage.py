#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors    : Gtlions Lai
from tornado import gen
import uuid,datetime
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase
from apps.common.apicom import get_ip_serialuuids

class ModifyProtectPackage(ActionBase):
    '''修改高防防护包'''

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
        ipnums = self.params['IPNums'] if 'IPNums' in self.params else None
        protect_base = self.params['GuaranteeProtectGroupID'] if 'GuaranteeProtectGroupID' in self.params else None
        protect_max = self.params['ElasticProtectGroupID'] if 'ElasticProtectGroupID' in self.params else None
        GuaranteeEnableTime = self.params['GuaranteeEnableTime'] if 'GuaranteeEnableTime' in self.params else None
        ElasticEnableTime = self.params['ElasticEnableTime'] if 'ElasticEnableTime' in self.params else None
        user_org = self.params['AccessKeyId']
        user_end = self.params['IPUserID'] if 'IPUserID' in self.params else None
        ts = self.application.ts_begin

        if ('GuaranteeProtectGroupID' in self.params and 'GuaranteeEnableTime' not in self.params) \
                or ('ElasticProtectGroupID' in self.params and 'ElasticEnableTime' not in self.params) \
                or ('GuaranteeProtectGroupID' not in self.params and 'GuaranteeEnableTime' in self.params) \
                or ('ElasticProtectGroupID' not in self.params and 'ElasticEnableTime' in self.params):
            res = sc(code.ParamAbsence)
            res.result = res.result % 'GuaranteeProtectGroupID-GuaranteeEnableTime|ElasticProtectGroupID-ElasticEnableTime'
            raise gen.Return(res)

        if not ipnums and not protect_base and not protect_max:
            res = sc(code.ParamError)
            res.result = res.result % '请传入要修改的参数'
            raise gen.Return(res)

        sql = 'select id,ipnums, protect_base, protect_max from t_package_protect where package_protect_id=%s AND user_org=%s and user_end=%s and status= TRUE and protect_state in (1,2)'
        data = self.application.dbcur.queryall_dict(sql, (packageid, user_org, user_end))
        if not data:
            res = sc(code.PackageStatusError)
            res.result = res.result % '请检查服务包状态'
            raise gen.Return(res)

        old_ipnums = data[0]['ipnums']
        old_protect_base = data[0]['protect_base']
        old_protect_max = data[0]['protect_max']

        if protect_base:
            protect_base = self.application.dbcur.queryall('select id from t_protect WHERE protect_id=%s', (protect_base, ))[0][0]
            sql = 'select bandtype from t_protect WHERE id=%s'
            data_band = self.application.dbcur.queryone(sql, (protect_base,))
            if data_band[0] != 70:
                res = sc(code.ParamError)
                res.result = res.result % '线路类型需为AntiBGP'
                raise gen.Return(res)
        if protect_max:
            protect_max = self.application.dbcur.queryall('select id from t_protect WHERE protect_id=%s', (protect_max, ))[0][0]
            sql = 'select bandtype from t_protect WHERE id=%s'
            data_band = self.application.dbcur.queryone(sql, (protect_max,))

            if not data_band[0] == 70:
                res = sc(code.ParamError)
                res.result = res.result % '线路类型需为AntiBGP'
                raise gen.Return(res)
        if protect_max and protect_base:
            if protect_max < protect_base:
                res = sc(code.ParamError)
                res.result = res.result % '保底防护组需小于弹性防护组'
                raise gen.Return(res)

        info = []
        a = 0
        s = 0
        if ipnums:
            s += 1
            sql = 'select count(ip) from t_ip_protect q LEFT JOIN t_package_protect w ON q.package=w.id where w.package_protect_id=%s and w.user_org=%s and w.user_end=%s and w.status=True;'
            self.application.dbcur.execute(sql, (packageid, user_org, user_end))
            ip_in_use = self.application.dbcur.fetchall()
            if int(ip_in_use[0][0]) > int(ipnums):
                res = sc(code.IPNumsError)
                res.result = res.result % '现使用ip数量已超过传入数量'
                raise gen.Return(res)
            if int(ipnums) == int(old_ipnums):
                info.append('ipnums与原先相同')
                a += 1
        if protect_base:
            s += 1
            if int(protect_base) == int(old_protect_base):
                info.append('保底防护组与原先相同')
                a += 1
        if protect_max:
            s += 1
            if int(protect_max) == int(old_protect_max):
                info.append('弹性防护组与原先相同')
                a += 1
        if a == s:
            res = sc(code.DuplicateRequest)
            res.result = res.result % info
            raise gen.Return(res)

        if protect_base:
            sql = "delete from t_job where p5=%s and p1='guaranteeprotect';"
            self.application.dbcur.execute(sql, (packageid, ))
            sql = 'insert into t_job (serialnum,ts,actions,ts_actions,p1,p3,p4,p5) values(%s,%s,%s,%s,%s,%s,%s,%s)'
            self.application.dbcur.execute(sql, (packageid, ts, 'ModifyProtectPackage', datetime.datetime.strptime(
                    GuaranteeEnableTime.replace('T', ' ').replace('Z', ''),
                    '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8), 'guaranteeprotect', old_protect_max, protect_base, packageid, ))

        if protect_max:
            sql = "delete from t_job where p5=%s and p1='elasticprotect';"
            self.application.dbcur.execute(sql, (packageid, ))
            sql = 'insert into t_job (serialnum,ts,actions,ts_actions,p1,p3,p4,p5) values(%s,%s,%s,%s,%s,%s,%s,%s)'
            self.application.dbcur.execute(sql, (packageid, ts, 'ModifyProtectPackage',datetime.datetime.strptime(
                ElasticEnableTime.replace('T', ' ').replace('Z', ''),
                    '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8), 'elasticprotect', old_protect_max, protect_max, packageid ,))

            # sql = 'update t_package_protect set protect_max=%s WHERE package_protect_id = %s AND status=TRUE ;'
            # self.application.dbcur.execute(sql, (protect_max, packageid))

        if ipnums:
            sql = 'update t_package_protect set ipnums=%s WHERE package_protect_id = %s AND status=TRUE ;'
            self.application.dbcur.execute(sql, (ipnums, packageid))

        # sql = 'INSERT INTO t_ip_protect_his (ip,package,user_org,user_end,protect_base,protect_max,protect_previous,ts_open,ts_shut,metric_pct_pps,metric_pct_bps,region,zone,serialnum,status,cts,actions,protect_state,iptype,bandtype) SELECT ip,package,user_org,user_end,protect_base,protect_max,protect_previous,ts_open,ts_shut,metric_pct_pps,metric_pct_bps,region,zone,serialnum,status,%s,%s,protect_state,iptype,bandtype FROM t_ip_protect WHERE package = %s'
        # self.application.dbcur.execute(sql, (ts, action, data[0]['id'],))
        self.application.history_backup_t_ip_protect(
            column_extra_value=",'{cts}','{action}'".format(cts=ts, action=action),
            filter="package='{package}'".format(package=data[0]['id']))

        # sql = 'insert into t_package_protect_his(ts_due,protect_base,protect_max,package,ipnums,package_protect_id,package_protect_name,user_org,user_end,protect_state,ts_open,ts_shut,serialnum,status,cts,actions) select ts_due,protect_base,protect_max,package,ipnums,package_protect_id,package_protect_name,user_org,user_end,protect_state,ts_open,ts_shut,serialnum,status,%s,%s from t_package_protect where package_protect_id=%s;'
        # self.application.dbcur.execute(sql, (ts, action, packageid))
        self.application.history_backup_t_package_protect(
            column_extra_value=",'{cts}','{action}'".format(cts=ts, action=action),
            filter="package_protect_id='{packageid}'".format(packageid=packageid))
        raise gen.Return(res)
