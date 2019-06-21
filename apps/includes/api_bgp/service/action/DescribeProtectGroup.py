#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Gtlions Lai

from tornado import gen

from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class DescribeProtectGroup(ActionBase):
    '''查看可用的防护组列表'''

    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        #self.application.logger.info(self.init_msg)

    @gen.coroutine
    def run(self):
        res = sc(code.Success)
        res.result = 'Success'

        sql = """SELECT protect_id AS "ProtectGroupID",protect_name AS "ProtectGroupName",max_bps_in/1000/1000/1000 AS "BlackHoleValue",
        b.bandtype_id as "BandwithType",rz.region_id as "Region",rz.zone_id AS "Zone"
        FROM t_protect p,t_bandtype b, (select r.region_id,z.zone_id from t_region r,t_zone z where r.id=z.region) rz
        where p.issys=False and p.status=True and p.bandtype=b.id"""
        if 'Region' in self.params:
            sql += " and rz.region_id='" + self.params['Region'] + "'"
        if 'Zone' in self.params:
            sql += " and rz.zone_id='" + self.params['Zone'] + "'"
        if 'BandwithType' in self.params:
            sql += " and b.bandtype_id='" + self.params['BandwithType'] + "'"

        sql = sql + ' order by "BandwithType","BlackHoleValue","ProtectGroupID"'
        data = self.application.dbcur.queryall_dict(sql)
        data_info = {}
        data_info['ProtectGroupInfo'] = data

        res.redata = data_info
        raise gen.Return(res)
