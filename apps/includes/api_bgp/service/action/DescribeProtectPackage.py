#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors    : Gtlions Lai <gtlions.l@qq.com>

from tornado import gen
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class DescribeProtectPackage(ActionBase):
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
        user_org = self.params['AccessKeyId']
        user_end = self.params['IPUserID'] if 'IPUserID' in self.params else None
        user_end_sql = " a.user_end='" + user_end + "' " if user_end else " 1=1 "
        package_id = self.params['PackageID'] if 'PackageID' in self.params else None
        package_id_sql = "a.package_protect_id='" + package_id + "'" if package_id else '1=1'

        sql = """select case when wm_concat(host(ip)) is not null then wm_concat(host(ip)) else ''end as "IPs",
                count(ip) as "IPNumsUsed",a.package_protect_name as "PackageName",a.package_protect_id as "PackageID",
                a.ipnums as "IPNums",replace(to_char(a.ts_due-INTERVAL '8 HOURS','YYYY-MM-DD HH24:MI:SSZ'),' ','T') as "DueTime",
                case when a.protect_state=2 then 'Elastic' when a.protect_state=1 then 'Guarantee' else 'Free' 
                end as "ProtectStatus",c.protect_id as "GuaranteeProtect",d.protect_id as "ElasticProtect",
                case when a.status=True then 'open' else 'close' end as "Status",
                replace(to_char(a.ts_open-INTERVAL '8 HOURS','YYYY-MM-DD HH24:MI:SSZ'),' ','T') as "OpenTimeStamp",
                case when a.ts_shut is not null then replace(to_char(a.ts_shut-INTERVAL '8 HOURS','YYYY-MM-DD HH24:MI:SSZ'),' ','T') else '' END as "CloseTimeStamp"
                from t_package_protect a left JOIN t_ip_protect w on w.package=a.id and w.status=TRUE LEFT JOIN t_protect c on a.protect_base=c.id LEFT JOIN t_protect d on a.protect_max=d.id
                where a.user_org=%s and {0} and {1} 
                GROUP BY w.package,a.package_protect_name,a.ipnums,a.protect_state,c.protect_id,a.status,a.ts_due,
                a.package_protect_id,d.protect_id,a.ts_open,a.ts_shut,w.package;""".format(package_id_sql,user_end_sql)

        data = self.application.dbcur.queryall_dict(sql, (user_org,))
        data_info = dict()
        data_info['ProtectPackageInfo'] = data
        res.redata = data_info
        raise gen.Return(res)
