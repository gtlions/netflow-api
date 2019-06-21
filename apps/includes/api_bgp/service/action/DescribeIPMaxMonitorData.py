#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: Gtlions Lai

import datetime
from tornado import gen

from apps.common import tools
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class DescribeIPMaxMonitorData(ActionBase):
    '''查看高防IP的带宽峰值'''

    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        # self.application.logger.info(self.init_msg)

    @gen.coroutine
    def run(self):
        res = sc(code.Success)
        res.result = 'Success'

        ip_l = self.params['IP'].split(',')
        user_org = self.params['AccessKeyId']
        user_end = self.params['IPUserID'] if 'IPUserID' in self.params else None
        packageid = self.params['PackageID'] if 'PackageID' in self.params else None
        starttime = self.params['StartTime']
        endtime = self.params['EndTime']

        starttime_str = starttime.replace('T', ' ').replace('Z', '')
        endtime_str = endtime.replace('T', ' ').replace('Z', '')
        starttime_dt = datetime.datetime.strptime(starttime_str, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)
        endtime_dt = datetime.datetime.strptime(endtime_str, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)
        band_m = self.application.dbcur.queryone("select bandmultiple from t_users where ackid=%s", (user_org, ))[0]
        package = self.application.dbcur.queryone("select id from t_package_protect where package_protect_id=%s", (packageid, ))[0] if packageid else None
        package_id_sql = "A.package='" + str(package) + "'" if packageid else 'A.package is NULL'
        user_end_sql = "A.user_end='" + user_end + "'" if user_end else '1=1'

        if starttime_dt > self.application.ts_begin or starttime_dt > endtime_dt:
            res = sc(code.TimeError)
            raise gen.Return(res)

        data_info = {}
        data_info['IPMaxMonitorData'] = []
        for ip in ip_l:
            ip_info = {}
            ip_info['ip'] = ip
            ip_info['Data'] = []
            sql = """
            SELECT count(ip), ip FROM (SELECT A.ts_open, CASE WHEN A.ts_shut IS NULL THEN now() ELSE A.ts_shut END
            ts_shut, b.* FROM ft_t_ip_protect A LEFT JOIN (SELECT * FROM t_blockhole_his WHERE ip=%s AND ts between %s
            and %s) b ON (b.ts BETWEEN A.ts_open AND CASE WHEN A.ts_shut IS NULL THEN now() ELSE A.ts_shut END ) AND
            A.ip = b.ip WHERE A.ip=%s AND user_org=%s AND {0} and {1}) T WHERE ts IS NOT NULL
            GROUP BY ip;""".format(package_id_sql, user_end_sql)
            black_hole = self.application.dbcurflow.queryone(sql, (ip, starttime, endtime, ip, user_org, ))

            if datetime.datetime.now() - datetime.timedelta(days=30) > starttime_dt:    # 30天之外去day表
                from_time_st = datetime.datetime.strptime(tools.front1day(str(starttime_dt)), "%Y-%m-%d %H:%M:%S")
                sql = """
                SELECT to_char(ts - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts,bps_max,pps_max FROM (SELECT
                A.ts_open, CASE WHEN A.ts_shut IS NULL THEN now() ELSE A.ts_shut END ts_shut, b.* FROM ft_t_ip_protect
                A LEFT JOIN (SELECT * FROM t_hosts_in_day WHERE ip=%s AND ts BETWEEN %s AND %s AND line=0 ) b ON (b.ts
                BETWEEN A.ts_open - INTERVAL '1day' AND CASE WHEN A.ts_shut IS NULL THEN now() ELSE A.ts_shut END )
                AND A.ip = b.ip WHERE A.ip=%s AND A.user_org=%s AND {0} AND {1}) T WHERE ts IS NOT NULL ORDER BY
                bps_max DESC;""".format(package_id_sql, user_end_sql)
                data = self.application.dbcurflow.queryone(sql, (ip, from_time_st, endtime_dt, ip, user_org,))
            elif starttime_dt + datetime.timedelta(seconds=300) > endtime_dt:   # 时间差300秒以内
                from_time = datetime.datetime.strptime(tools.front5min(str(starttime_dt)), "%Y-%m-%d %H:%M:%S")
                sql = """
                SELECT to_char(ts - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts,bps_max,pps_max FROM (SELECT
                A.ts_open, CASE WHEN A.ts_shut IS NULL THEN now() ELSE A.ts_shut END ts_shut, b.* FROM ft_t_ip_protect
                A LEFT JOIN (SELECT * FROM t_hosts_in_min5 WHERE ip=%s AND ts=%s AND line=0 ) b ON (b.ts
                BETWEEN A.ts_open - INTERVAL '1day' AND CASE WHEN A.ts_shut IS NULL THEN now() ELSE A.ts_shut END )
                AND A.ip = b.ip WHERE A.ip=%s AND A.user_org=%s AND {0} AND {1}) T WHERE ts IS NOT NULL ORDER BY
                bps_max DESC;""".format(package_id_sql, user_end_sql)
                data = self.application.dbcurflow.queryone(sql, (ip, from_time, ip, user_org,))
            else:       # 时间差300秒外，30天内5min表
                sql = """
                SELECT to_char(ts - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts,bps_max,pps_max FROM (SELECT
                A.ts_open, CASE WHEN A.ts_shut IS NULL THEN now() ELSE A.ts_shut END ts_shut, b.* FROM ft_t_ip_protect
                A LEFT JOIN (SELECT * FROM t_hosts_in_min5 WHERE ip=%s AND ts BETWEEN %s AND %s AND line=0 ) b ON (b.ts
                BETWEEN A.ts_open - INTERVAL '1day' AND CASE WHEN A.ts_shut IS NULL THEN now() ELSE A.ts_shut END )
                AND A.ip = b.ip WHERE A.ip=%s AND A.user_org=%s AND {0} AND {1}) T WHERE ts IS NOT NULL ORDER BY
                bps_max DESC;""".format(package_id_sql, user_end_sql)
                data = self.application.dbcurflow.queryone(sql, (ip, starttime_dt, endtime_dt, ip, user_org,))
            ts = data[0].replace('-T', 'T')if data else tools.front5min(starttime)
            max_value = data[1] if data else 0
            max_pps = data[2] if data else 0

            count_data = {}
            count_data['KBPS_MAX'] = int(int(max_value) * band_m / 1000)
            count_data['PPS_MAX'] = int(int(max_pps) * band_m)
            count_data['BlackHoleTimes'] = black_hole[0] if black_hole else 0
            count_data['IP'] = ip

            count_data['TimeStamp'] = ts
            data_info['IPMaxMonitorData'].append(count_data)

        res.redata = data_info
        raise gen.Return(res)
