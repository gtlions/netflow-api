#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Gtlions Lai

import uuid
from tornado import gen
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase
from apps.common.apicom import get_ip_serialuuids
import datetime


class ModifyIPProtectGroup(ActionBase):
    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        #self.application.logger.info(self.init_msg)


    @gen.coroutine
    def run(self):
        res = sc(code.Success)
        res.result = 'Success'
        actions = self.params['Action']
        ts = self.application.ts_begin
        user_org = self.params['AccessKeyId']
        ip = self.params['IP']
        ip_s = self.params['IP']
        ip_l = self.params['IP'].split(',')
        ipuserid = self.params['IPUserID'] if 'IPUserID' in self.params else None
        guaranteeprotect = self.params['GuaranteeProtectGroupID'] if 'GuaranteeProtectGroupID' in self.params else None
        guaranteeEnableTime = self.params['GuaranteeEnableTime'] if 'GuaranteeEnableTime' in self.params else None
        elasticprotect = self.params['ElasticProtectGroupID'] if 'ElasticProtectGroupID' in self.params else None
        elasticenabletime = self.params['ElasticEnableTime'] if 'ElasticEnableTime' in self.params else None
        region = self.params['Region']
        zone = self.params['Zone']
        bandtype = self.params['BandwithType']

        if ('GuaranteeProtectGroupID' not in self.params and 'ElasticProtectGroupID' not in self.params) \
                or ('GuaranteeProtectGroupID' in self.params and 'GuaranteeEnableTime' not in self.params) \
                or ('ElasticProtectGroupID' in self.params and 'ElasticEnableTime' not in self.params) \
                or ('GuaranteeProtectGroupID' not in self.params and 'GuaranteeEnableTime' in self.params) \
                or ('ElasticProtectGroupID' not in self.params and 'ElasticEnableTime' in self.params):
            res = sc(code.ParamAbsence)
            res.result = res.result % 'GuaranteeProtectGroupID-GuaranteeEnableTime|ElasticProtectGroupID-ElasticEnableTime'
            raise gen.Return(res)
        uuids_list, uuids_str, ips_list, ips_str = get_ip_serialuuids(user_org=user_org, user_end=ipuserid, ips=ip,
                                                                      status='open')

        job_serialuuid = str(uuid.uuid1())
        if not uuids_list:
            res = sc(code.IPNotUsed)
            res.result = res.result % str(ip_s)
            raise gen.Return(res)
        if len(ip_l) != len(ips_list):
            ip_r = list(set(ip_l).difference(set(ips_list)))
            res = sc(code.IPNotUsed)
            res.result = res.result % str(','.join(ip_r))
            raise gen.Return(res)
        if 'GuaranteeProtectGroupID' in self.params and 'ElasticProtectGroupID' in self.params:
            gua_sql = "SELECT id FROM t_protect WHERE protect_id=%s"
            ela_sql = "SELECT id FROM t_protect WHERE protect_id=%s"
            gua_id = self.application.dbcur.queryone(gua_sql, (guaranteeprotect,))
            ela_id = self.application.dbcur.queryone(ela_sql, (elasticprotect,))
            if gua_id[0] > ela_id[0]:
                res = sc(code.ParamError)
                res.result = res.result % '保底需小于弹性'
                raise gen.Return(res)
        sql = 'select bandtype_id from t_ip_protect JOIN t_bandtype ON t_ip_protect.bandtype=t_bandtype.id WHERE ip= %s and t_ip_protect.status=TRUE '
        data_band = self.application.dbcur.queryone(sql, (ip,))
        if data_band[0] != bandtype:
            res = sc(code.ParamError)
            res.result = res.result % '线路类型需要一致'
            raise gen.Return(res)


        sql = 'SELECT host(a.ip) AS ip FROM t_ip_protect a WHERE NOT EXISTS (SELECT 1 FROM t_job b WHERE a.ip=b.ip AND a.serialnum=b.p5) AND a.serialnum IN (%s)'
        if guaranteeprotect and elasticprotect:
            sql += ' and a.protect_base=(select id from t_protect where protect_id= %s and a.region=region and a.zone=zone) and a.protect_max=(select id from t_protect where protect_id=%s and a.region=region and a.zone=zone)'
            data = self.application.dbcur.queryall(sql, (uuids_str.replace('"', "'"), guaranteeprotect, elasticprotect,))

        if guaranteeprotect and not elasticprotect:
            sql += ' and a.protect_base=(select id from t_protect where protect_id= %s and a.region=region and a.zone=zone)'
            data = self.application.dbcur.queryall_dict(sql, (uuids_str.replace('"', ""),guaranteeprotect,))

        if not guaranteeprotect and elasticprotect:
            sql += ' and a.protect_max=(select id from t_protectgroup where groupid="' + elasticprotect + '" and a.region=region and a.zone=zone)'
            data = self.application.dbcur.queryall_dict(sql, (uuids_str.replace('"', ""), elasticprotect,))


        ip_r = [x['ip'] for x in data] if data else None
        if ip_r:
            ip_r = [x for x in ip_r if x in ips_list]
            res = sc(code.DuplicateRequest)
            res.result = res.result % ip
            raise gen.Return(res)
        sql = 'SELECT host(ip) AS ip ,serialnum as ip_serialuuid,q.protect_id guaranteeprotect,' \
              'e.protect_id elasticprotect FROM t_ip_protect w,t_protect q,t_protect e where w.protect_base=q.id ' \
              'AND w.protect_max=e.id AND serialnum in (%s)'
        data1 = self.application.dbcur.queryall_dict(sql, (uuids_str.replace('"', ""),))

        if data1:
            for i1 in data1:
                ip, ip_serialuuid, old_guaranteeprotect, old_elasticprotect = i1['ip'], i1['ip_serialuuid'], i1[
                    'guaranteeprotect'], i1['elasticprotect']

                sql = "select id,actions,ts_actions,p1,p2,p3,p4 from t_job where actions= 'ModifyIPProtectGroup' and p5=%s"
                data2 = self.application.dbcur.queryall_dict(sql, (ip_serialuuid,))

                if data2:
                    sql = 'delete from t_job where p5=%s'
                    self.application.dbcur.queryall_dict(sql, (ip_serialuuid,))
                    if guaranteeprotect:
                        job_info = {}
                        job_info['serialnum'] = job_serialuuid
                        job_info['ts'] = ts
                        job_info['ts_actions'] = datetime.datetime.strptime(
                            guaranteeEnableTime.replace('T', ' ').replace('Z', ''),
                            '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)
                        job_info['ip'] = ip
                        job_info['actions'] = 'ModifyIPProtectGroup'
                        job_info['p1'] = 'guaranteeprotect'
                        job_info['p2'] = self.application.dbcur.queryone('select id from t_bandtype where bandtype_id=%s', (bandtype,))[0]
                        job_info['p3'] = self.application.dbcur.queryone(
                            'select id from t_protect where protect_id=%s', (old_guaranteeprotect,))[0]
                        job_info['p4'] = self.application.dbcur.queryone(
                            'select id from t_protect where protect_id=%s', (guaranteeprotect,))[0]
                        job_info['p5'] = ip_serialuuid
                        self.application.dbcur.insert_dict('t_job', job_info)

                    if elasticprotect:
                        job_info = {}
                        job_info['serialnum'] = job_serialuuid
                        job_info['ts'] = ts
                        job_info['ts_actions'] = datetime.datetime.strptime(
                            elasticenabletime.replace('T', ' ').replace('Z', ''),
                            '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)
                        job_info['ip'] = ip
                        job_info['actions'] = 'ModifyIPProtectGroup'
                        job_info['p1'] = 'elasticprotect'
                        job_info['p2'] = self.application.dbcur.queryone('select id from t_bandtype where bandtype_id=%s', (bandtype,))[0]
                        job_info['p3'] = self.application.dbcur.queryone(
                            'select id from t_protect where protect_id=%s', (old_elasticprotect,))[0]
                        job_info['p4'] = self.application.dbcur.queryone(
                            'select id from t_protect where protect_id=%s', (elasticprotect,))[0]
                        job_info['p5'] = ip_serialuuid
                        self.application.dbcur.insert_dict('t_job', job_info)

                else:
                    if guaranteeprotect and old_guaranteeprotect != guaranteeprotect:
                        job_info = {}
                        job_info['serialnum'] = job_serialuuid
                        job_info['ts'] = ts
                        job_info['ts_actions'] = datetime.datetime.strptime(
                            guaranteeEnableTime.replace('T', ' ').replace('Z', ''),
                            '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)
                        job_info['ip'] = ip
                        job_info['actions'] = 'ModifyIPProtectGroup'
                        job_info['p1'] = 'guaranteeprotect'
                        job_info['p2'] = self.application.dbcur.queryone('select id from t_bandtype where bandtype_id=%s', (bandtype,))[0]
                        job_info['p3'] = self.application.dbcur.queryone(
                            'select id from t_protect where protect_id=%s', (old_guaranteeprotect,))[0]
                        job_info['p4'] = self.application.dbcur.queryone(
                            'select id from t_protect where protect_id=%s', (guaranteeprotect,))[0]
                        job_info['p5'] = ip_serialuuid
                        self.application.dbcur.insert_dict('t_job', job_info)

                    if elasticprotect and old_elasticprotect != elasticprotect:
                        job_info = {}
                        job_info['serialnum'] = job_serialuuid
                        job_info['ts'] = ts
                        job_info['ts_actions'] = datetime.datetime.strptime(
                            elasticenabletime.replace('T', ' ').replace('Z', ''),
                            '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)
                        job_info['ip'] = ip
                        job_info['actions'] = 'ModifyIPProtectGroup'
                        job_info['p1'] = 'elasticprotect'
                        job_info['p2'] = \
                        self.application.dbcur.queryone('select id from t_bandtype where bandtype_id=%s', (bandtype,))[0]
                        job_info['p3'] = self.application.dbcur.queryone('select id from t_protect where protect_id=%s', (old_elasticprotect, ))[0]
                        job_info['p4'] = \
                        self.application.dbcur.queryone('select id from t_protect where protect_id=%s', (elasticprotect,))[0]
                        job_info['p5'] = ip_serialuuid
                        self.application.dbcur.insert_dict('t_job', job_info)

        raise gen.Return(res)
