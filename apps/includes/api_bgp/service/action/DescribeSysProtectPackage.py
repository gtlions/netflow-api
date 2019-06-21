#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors    : Gtlions Lai <gtlions.l@qq.com>

from tornado import gen

from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class DescribeSysProtectPackage(ActionBase):
    '''查看系统高防服务包'''

    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        # self.application.logger.info(self.init_msg)

    @gen.coroutine
    def run(self):
        res = sc(code.Success)
        res.result = 'Success'

        sql = """select a.package_id as "PackageID",a.package_name as "Packagename",a.ipnums as "IPNums",
b.protect_name as "BaseProtectName",b.max_bps_in/1000/1000/1000 as "BaseProtectValue",
c.protect_name as "MaxProtectName",c.max_bps_in/1000/1000/1000 as "MaxProtectValue"
from t_package a,t_protect b,t_protect c
where a.protect_base=b.id and a.protect_max=c.id and a.status=True;"""
        data = self.application.dbcur.queryall_dict(sql)
        data_info = {}
        data_info['SysPackageInfo'] = data
        res.redata = data_info
        raise gen.Return(res)
