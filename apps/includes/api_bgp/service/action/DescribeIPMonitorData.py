#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Gtlions Lai

import datetime

from tornado import gen
from apps.common import tools
from apps.common.statusconfig import code
from apps.common.statusconfig import statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class DescribeIPMonitorData(ActionBase):
    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        # self.application.logger.info(self.init_msg)

    @gen.coroutine
    def run(self):
        ip_s = self.params['IP']
        ip_l = self.params['IP'].split(',')
        user_org = self.params['AccessKeyId']
        user_end = self.params['IPUserID'] if 'IPUserID' in self.params else None
        packageid = self.params['PackageID'] if 'PackageID' in self.params else None
        starttime = self.params['StartTime']
        endtime = self.params['EndTime']
        dt = self.application.ts_begin

        starttime_str = starttime.replace('T', ' ').replace('Z', '')
        endtime_str = endtime.replace('T', ' ').replace('Z', '')
        starttime_dt = datetime.datetime.strptime(starttime_str, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)
        endtime_dt = datetime.datetime.strptime(endtime_str, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)

        if starttime_dt > self.application.ts_begin or starttime_dt > endtime_dt:
            res = sc(code.TimeError)
            raise gen.Return(res)

        total_times = (endtime_dt - starttime_dt).total_seconds()
        band_m = self.application.dbcur.queryone("select bandmultiple from t_users where ackid=%s", (user_org, ))[0]
        package = self.application.dbcur.queryone("select id from t_package_protect where package_protect_id=%s", (packageid, ))[0] if packageid else None
        package_id_sql = "A.package='" + str(package) + "'" if packageid else 'A.package is NULL'
        user_end_sql = "A.user_end='" + user_end + "'" if user_end else "A.user_end is NULL"
        data_info = {}
        data_info['IPMonitorData'] = []

        for ip in ip_l:
            ip_info = {}
            ip_info['ip'] = ip
            ip_info['Data'] = []
            if dt - datetime.timedelta(days=30) > starttime_dt:    # 30天外，day表
                from_time_st = datetime.datetime.strptime(tools.front1day(str(starttime_dt)), "%Y-%m-%d %H:%M:%S")
                from_time_ed = datetime.datetime.strptime(tools.front1day(str(endtime_dt)), "%Y-%m-%d %H:%M:%S")
                sql = """
                SELECT to_char(ts - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts, bps_max, bps_avg, pps_max,
                pps_avg FROM (SELECT A.ts_open, CASE WHEN A.ts_shut IS NULL THEN now() ELSE A.ts_shut END ts_shut,
                b.* FROM ft_t_ip_protect A LEFT JOIN (SELECT * FROM t_hosts_in_day WHERE ip=%s AND ts BETWEEN %s AND %s
                AND line=0 ) b ON (b.ts BETWEEN A.ts_open - INTERVAL '1day'AND CASE WHEN A.ts_shut IS NULL THEN now()
                ELSE A.ts_shut END) AND A.ip = b.ip WHERE A.ip=%s AND A.user_org=%s AND {0} AND {1}) T WHERE
                ts IS NOT NULL ORDER BY ts;""".format(package_id_sql, user_end_sql)
                data = self.application.dbcurflow.queryall_dict(sql, (ip, from_time_st, from_time_ed, ip, user_org,))
            elif total_times <= 86400:
                if starttime_dt + datetime.timedelta(seconds=300) > endtime_dt:
                    from_time = datetime.datetime.strptime(tools.front5min(str(starttime_dt)), "%Y-%m-%d %H:%M:%S")
                    sql = """
                    SELECT to_char(ts - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts, bps_avg, bps_max, pps_avg,
                    pps_max FROM (SELECT A.ts_open, CASE WHEN A.ts_shut IS NULL THEN now() ELSE A.ts_shut END ts_shut,
                    b.* FROM ft_t_ip_protect A LEFT JOIN (SELECT * FROM t_hosts_in_min5 WHERE ip=%s AND ts=%s AND
                    line=0 ) b ON (b.ts BETWEEN A.ts_open - INTERVAL '1day' AND CASE WHEN A.ts_shut IS NULL
                    THEN now() ELSE A.ts_shut END) AND A.ip = b.ip WHERE A.ip=%s AND A.user_org=%s AND {0} AND {1}) T
                    WHERE ts IS NOT NULL ORDER BY ts;""".format(package_id_sql, user_end_sql)
                    data = self.application.dbcurflow.queryall_dict(sql, (ip, from_time, ip, user_org,))
                else:
                    sql = """
                    SELECT to_char(ts - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts, bps_avg, bps_max, pps_avg,
                    pps_max FROM (SELECT A.ts_open, CASE WHEN A.ts_shut IS NULL THEN now() ELSE A.ts_shut END ts_shut,
                    b.* FROM ft_t_ip_protect A LEFT JOIN (SELECT * FROM t_hosts_in_min5 WHERE ip=%s AND ts BETWEEN %s
                    AND %s AND line=0 ) b ON (b.ts BETWEEN A.ts_open - INTERVAL '1day' AND CASE WHEN A.ts_shut IS NULL
                    THEN now() ELSE A.ts_shut END) AND A.ip = b.ip WHERE A.ip=%s AND A.user_org=%s AND {0} AND {1}) T
                    WHERE ts IS NOT NULL ORDER BY ts;""".format(package_id_sql, user_end_sql)
                    data = self.application.dbcurflow.queryall_dict(sql, (ip, starttime_dt, endtime_dt, ip, user_org,))
            elif total_times <= 259200:
                # 3天内
                sql = """
                SELECT to_char(date_trunc('hour', ts) + CAST (FLOOR (EXTRACT(minutes FROM ts) / 15) * 15 || ' minutes'
                AS INTERVAL ) - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts, AVG (bps_avg) AS bps_avg,
                MAX(bps_max) AS bps_max,AVG(pps_avg) AS pps_avg,MAX(pps_max) AS pps_max FROM (SELECT A.ts_open, CASE
                WHEN A.ts_shut IS NULL THEN now() ELSE A.ts_shut END ts_shut, b.* FROM ft_t_ip_protect A LEFT JOIN
                (SELECT * FROM t_hosts_in_min5 WHERE ip=%s AND ts BETWEEN %s AND %s AND line=0 ) b ON (b.ts BETWEEN
                A.ts_open AND CASE WHEN A.ts_shut IS NULL THEN now() ELSE A.ts_shut END ) AND A.ip = b.ip WHERE A.ip=%s
                AND A .user_org=%s AND {0} AND {1}) T WHERE ts IS NOT NULL GROUP BY date_trunc('hour', ts) + CAST
                (FLOOR (EXTRACT(minutes FROM ts) / 15) * 15 || ' minutes' AS INTERVAL ) ORDER BY ts;""".format(package_id_sql, user_end_sql)
                data = self.application.dbcurflow.queryall_dict(sql, (ip, starttime_dt, endtime_dt, ip, user_org,))
            elif total_times <= 518400:
                # 6天内
                sql = """
                SELECT to_char(date_trunc('hour', ts) + CAST (FLOOR (EXTRACT(minutes FROM ts) / 30) * 30 || ' minutes'
                AS INTERVAL ) - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts, AVG (bps_avg) AS bps_avg,
                MAX(bps_max) AS bps_max,AVG(pps_avg) AS pps_avg,MAX(pps_max) AS pps_max FROM (SELECT A.ts_open, CASE
                WHEN A.ts_shut IS NULL THEN now() ELSE A.ts_shut END ts_shut, b.* FROM ft_t_ip_protect A LEFT JOIN
                (SELECT * FROM t_hosts_in_min5 WHERE ip=%s AND ts BETWEEN %s AND %s AND line=0 ) b ON (b.ts BETWEEN
                A.ts_open AND CASE WHEN A.ts_shut IS NULL THEN now() ELSE A.ts_shut END ) AND A.ip = b.ip WHERE A.ip=%s
                AND A .user_org=%s AND {0} AND {1}) T WHERE ts IS NOT NULL GROUP BY date_trunc('hour', ts) + CAST
                (FLOOR (EXTRACT(minutes FROM ts) / 30) * 30 || ' minutes' AS INTERVAL ) ORDER BY ts;""".format(package_id_sql, user_end_sql)
                data = self.application.dbcurflow.queryall_dict(sql, (ip, starttime_dt, endtime_dt, ip, user_org,))
            elif total_times <= 1036800:
                sql = """
                SELECT to_char(date_trunc('day', ts) + CAST (FLOOR (EXTRACT(hour FROM ts) / 1) * 1 || ' hour'
                AS INTERVAL ) - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts, AVG (bps_avg) AS bps_avg,
                MAX(bps_max) AS bps_max,AVG(pps_avg) AS pps_avg,MAX(pps_max) AS pps_max FROM (SELECT A.ts_open, CASE
                WHEN A.ts_shut IS NULL THEN now() ELSE A.ts_shut END ts_shut, b.* FROM ft_t_ip_protect A LEFT JOIN
                (SELECT * FROM t_hosts_in_min5 WHERE ip=%s AND ts BETWEEN %s AND %s AND line=0 ) b ON (b.ts BETWEEN
                A.ts_open AND CASE WHEN A.ts_shut IS NULL THEN now() ELSE A.ts_shut END ) AND A.ip = b.ip WHERE A.ip=%s
                AND A .user_org=%s AND {0} AND {1}) T WHERE ts IS NOT NULL GROUP BY date_trunc('day', ts) + CAST
                (FLOOR (EXTRACT(hour FROM ts) / 1) * 1 || ' hour' AS INTERVAL ) ORDER BY ts;""".format(package_id_sql, user_end_sql)
                data = self.application.dbcurflow.queryall_dict(sql, (ip, starttime_dt, endtime_dt, ip, user_org,))
            else:
                sql = """
                SELECT to_char(date_trunc('day', ts) + CAST (FLOOR (EXTRACT(hour FROM ts) / 3) * 3 || ' hour'
                AS INTERVAL ) - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts, AVG (bps_avg) AS bps_avg,
                MAX(bps_max) AS bps_max,AVG(pps_avg) AS pps_avg,MAX(pps_max) AS pps_max FROM (SELECT A.ts_open, CASE
                WHEN A.ts_shut IS NULL THEN now() ELSE A.ts_shut END ts_shut, b.* FROM ft_t_ip_protect A LEFT JOIN
                (SELECT * FROM t_hosts_in_min5 WHERE ip=%s AND ts BETWEEN %s AND %s AND line=0 ) b ON (b.ts BETWEEN
                A.ts_open AND CASE WHEN A.ts_shut IS NULL THEN now() ELSE A.ts_shut END ) AND A.ip = b.ip WHERE A.ip=%s
                AND A .user_org=%s AND {0} AND {1}) T WHERE ts IS NOT NULL GROUP BY date_trunc('day', ts) + CAST
                (FLOOR (EXTRACT(hour FROM ts) / 3) * 3 || ' hour' AS INTERVAL ) ORDER BY ts;""".format(package_id_sql, user_end_sql)
                data = self.application.dbcurflow.queryall_dict(sql, (ip, starttime_dt, endtime_dt, ip, user_org,))

            if data:
                for i in data:
                    count_data = {}
                    count_data['KBPS'] = 0 if i['bps_avg'] is None else int(int(i['bps_avg']) * band_m / 1000)
                    count_data['PPS'] = 0 if i['pps_avg'] is None else int(int(i['pps_avg']) * band_m)
                    count_data['KBPS_MAX'] = 0 if i['bps_max'] is None else int(int(i['bps_max']) * band_m / 1000)
                    count_data['PPS_MAX'] = 0 if i['pps_max'] is None else int(int(i['pps_max']) * band_m)
                    count_data['TimeStamp'] = i['ts'].replace('-T', 'T')
                    ip_info['Data'].append(count_data)
                data_info['IPMonitorData'].append(ip_info)
            else:
                count_data = {}
                count_data['KBPS'] = 0
                count_data['PPS'] = 0
                count_data['KBPS_MAX'] = 0
                count_data['PPS_MAX'] = 0
                count_data['TimeStamp'] = starttime
                ip_info['Data'].append(count_data)
                data_info['IPMonitorData'].append(ip_info)

        res = sc(code.Success)
        res.result = 'Success'
        res.redata = data_info
        raise gen.Return(res)
