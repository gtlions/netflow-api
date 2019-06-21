#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Gtlions Lai

from tornado import gen

from apps.includes.api_bgp.service.actionbase.action_base import ActionBase
from apps.common.statusconfig import code
from apps.common.statusconfig import statusconfig as sc
from apps.common.apicom import get_ip_serialuuids


class DescribeIPInfo(ActionBase):
    '''高防IP的防护组信息'''
    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        # self.application.logger.info(self.init_msg)

    @gen.coroutine
    def run(self):
        res = sc(code.Success)
        res.result = 'Success'

        ips = self.params['IP'] if 'IP' in self.params else None
        user_org = self.params['AccessKeyId']
        user_end = self.params['IPUserID'] if 'IPUserID' in self.params else None

        data_info = {}
        data_info['ProtectGroupInfo'] = []
        if ips:
            ip_l = ips.split(',')
        else:
            ip_l = []
            if 'IPUserID' in self.params:
                sql = "SELECT HOST (ip) AS ip FROM t_ip_protect WHERE user_org=%s AND user_end=%s AND status=TRUE"
                ip_data = self.application.dbcur.queryall_dict(sql, (user_org, user_end,))
            else:
                sql = "SELECT HOST (ip) AS ip FROM t_ip_protect WHERE user_org=%s AND status=TRUE"
                ip_data = self.application.dbcur.queryall_dict(sql, (user_org,))
            for i in ip_data:
                ip_l.append(i['ip'])
            ip_l = list(set(ip_l))

        for ip in ip_l:
            uuids_list, uuids_str, _, _ = get_ip_serialuuids(user_org=user_org, user_end=user_end, ips=ip)
            if uuids_list:
                sql = """SELECT host(ip) as ip,CASE WHEN ip.package is null then ''else package_protect_id end as "Package", CASE WHEN ip.user_end IS NULL THEN ''ELSE ip.user_end END AS user_end,CASE WHEN ip.status = True THEN 'open' ELSE 'close' END AS "Status",to_char(ip.ts_open - INTERVAL'8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS "OpenTimeStamp",
CASE WHEN ip.ts_shut IS NULL THEN '' ELSE to_char(ip.ts_shut-INTERVAL'8hour', 'YYYY-MM-DD-THH24:MI:SSZ') END AS"CloseTimeStamp",b.bandtype_name AS "BandwithType",case when ip.zone is null then ''ELSE zone_name end AS "Zone",
CASE when ip.region is null then ''else region_name end AS "Region",p.max_bps_in as"guaranteeprotectBlackHoleValue" ,p.protect_id AS "guaranteeprotectProtectGroupID",p.protect_name AS "guaranteeprotectProtectGroupName",e.protect_id AS "elasticprotectProtectGroupID",
e.protect_name AS "elasticprotectProtectGroupName",e.max_bps_in AS "elasticprotectBlackHoleValue"
from t_ip_protect ip LEFT JOIN t_bandtype b on b.id=ip.bandtype LEFT JOIN t_protect p on p.id=ip.protect_base LEFT JOIN t_protect e on e.id=ip.protect_max
LEFT JOIN t_zone on t_zone.id=ip.zone LEFT JOIN t_region on t_region.id=ip.region LEFT JOIN t_package_protect ppp on ppp.id=ip.package
WHERE ip.serialnum =%s"""

                data = self.application.dbcur.queryall_dict(sql, (uuids_str.replace('"', ""),))
                for ipinfo in data:
                    sinfo = {}
                    sinfo['ip'] = ipinfo['ip']
                    sinfo['IPUserID'] = ipinfo['user_end']
                    sinfo['Package'] = ipinfo['Package']
                    sinfo['Status'] = ipinfo['Status']
                    sinfo['OpenTimeStamp'] = ipinfo['OpenTimeStamp'].replace('-T', 'T')
                    sinfo['CloseTimeStamp'] = ipinfo['CloseTimeStamp'].replace('-T', 'T')
                    sinfo['BandwithType'] = ipinfo['BandwithType']
                    sinfo['Region'] = ipinfo['Region']
                    sinfo['Zone'] = ipinfo['Zone']
                    sinfo['GAURATEE'] = {'ProtectGroupID': ipinfo['guaranteeprotectProtectGroupID'],
                                         'ProtectGroupName': ipinfo['guaranteeprotectProtectGroupName'],
                                         'BlackHoleValue': int(ipinfo['guaranteeprotectBlackHoleValue']/1000000000)
                                         }
                    sinfo['ELASTIC'] = {'ProtectGroupID': ipinfo['elasticprotectProtectGroupID'],
                                        'ProtectGroupName': ipinfo['elasticprotectProtectGroupName'],
                                        'BlackHoleValue': int(ipinfo['elasticprotectBlackHoleValue']/1000000000)
                                        }
                    data_info['ProtectGroupInfo'].append(sinfo)
            else:
                res = sc(code.IPNotUsed)
                res.result = res.result % str(ip)
                raise gen.Return(res)

        res.redata = data_info
        raise gen.Return(res)
