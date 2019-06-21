#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Gtlions Lai

from tornado import gen
import datetime
from apps.common import tools
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase
from apps.common.statusconfig import code
from apps.common.statusconfig import statusconfig as sc
from apps.common.apicom import get_ip_serialuuids


class DescribeNormalIPData(ActionBase):
    '''查看普通IP信息'''
    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        # self.application.logger.info(self.init_msg)

    @gen.coroutine
    def run(self):
        res = sc(code.Success)
        res.result = 'Success'

        ip = self.params['IP']
        user_org = self.params['AccessKeyId']
        starttime = self.params['StartTime']
        endtime = self.params['EndTime']

        starttime_str = starttime.replace('T', ' ').replace('Z', '')
        endtime_str = endtime.replace('T', ' ').replace('Z', '')
        starttime_dt = datetime.datetime.strptime(starttime_str, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)
        endtime_dt = datetime.datetime.strptime(endtime_str, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)
        dt = self.application.ts_begin
        band_m = self.application.dbcur.queryone("select bandmultiple from t_users where ackid=%s", (user_org, ))[0]
        total_times = (endtime_dt - starttime_dt).total_seconds()
        if starttime_dt > self.application.ts_begin or starttime_dt > endtime_dt:
            res = sc(code.TimeError)
            raise gen.Return(res)

        if datetime.datetime.now() - datetime.timedelta(days=30) > starttime_dt:    # 30天之外去day表
            sql = """select to_char(a.ts - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts,a.bps_max,a.bps_avg,a.pps_max,a.pps_avg from t_hosts_in_day a
            left join ft_t_ip_protect b on a.ip=b.ip and a.ts between b.ts_open and nvl(b.ts_shut,b.ts_open+'10000 days'::interval)
            where a.ip=%s and a.line=0 and b.id is null and a.ts between %s and %s
            order by a.bps_max desc"""
            data_max = self.application.dbcurflow.queryone(sql, (ip, starttime_dt, endtime_dt,))

        elif starttime_dt + datetime.timedelta(seconds=300) > endtime_dt:   # 时间差300秒以内
            from_time = datetime.datetime.strptime(tools.front5min(str(starttime_dt)), "%Y-%m-%d %H:%M:%S")
            sql = """select to_char(a.ts - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ'),a.bps_max,a.bps_avg,a.pps_max,a.pps_avg from t_hosts_in_min5 a
            left join ft_t_ip_protect b on a.ip=b.ip and a.ts between b.ts_open and nvl(b.ts_shut,b.ts_open+'10000 days'::interval)
            where a.ip=%s and a.line=0 and b.id is null and a.ts = %s
            order by a.bps_max desc"""
            data_max = self.application.dbcurflow.queryone(sql, (ip, from_time,))
        else:       # 时间差300秒外，30天内5min表
            sql = """select to_char(a.ts - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts,a.bps_max,a.bps_avg,a.pps_max,a.pps_avg from t_hosts_in_min5 a
            left join ft_t_ip_protect b on a.ip=b.ip and a.ts between b.ts_open and nvl(b.ts_shut,b.ts_open+'10000 days'::interval)
            where a.ip=%s and a.line=0 and b.id is null and a.ts between %s and %s
            order by a.bps_max desc"""
            data_max = self.application.dbcurflow.queryone(sql, (ip, starttime_dt, endtime_dt,))
        ts = data_max[0].replace('-T', 'T')if data_max else tools.front5min(starttime)+'Z'
        max_value = data_max[1] if data_max else 0
        max_pps = data_max[2] if data_max else 0
        ip_info = {}
        ip_info['Data'] = []
        if dt - datetime.timedelta(days=30) > starttime_dt:    # 30天外，day表
            from_time_st = datetime.datetime.strptime(tools.front1day(str(starttime_dt)), "%Y-%m-%d %H:%M:%S")
            from_time_ed = datetime.datetime.strptime(tools.front1day(str(endtime_dt)), "%Y-%m-%d %H:%M:%S")
            sql = """
              select to_char(a.ts - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts,a.bps_max AS bps_max,a.bps_avg AS bps_avg,a.pps_max AS pps_max,a.pps_avg AS pps_avg
              from t_hosts_in_day a
              left join ft_t_ip_protect b on a.ip=b.ip and a.ts between b.ts_open and nvl(b.ts_shut,b.ts_open+'10000 days'::interval)
              where a.ip=%s and b.id is null and a.ts BETWEEN %s and %s and a.line=0 order by a.ts"""
            data = self.application.dbcurflow.queryall_dict(sql, (ip, from_time_st, from_time_ed, ))

        elif total_times <= 86400:
            if starttime_dt + datetime.timedelta(seconds=300) > endtime_dt:
                from_time = datetime.datetime.strptime(tools.front5min(str(starttime_dt)), "%Y-%m-%d %H:%M:%S")

                sql = """
                  select to_char(a.ts - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts,a.bps_max AS bps_max,a.bps_avg AS bps_avg,a.pps_max AS pps_max,a.pps_avg AS pps_avg
                  from t_hosts_in_min5 a
                  left join ft_t_ip_protect b on a.ip=b.ip and a.ts between b.ts_open and nvl(b.ts_shut,b.ts_open+'10000 days'::interval)
                  where a.ip=%s and b.id is null and a.ts = %s and a.line=0 order by a.ts"""
                data = self.application.dbcurflow.queryall_dict(sql, (ip, from_time,))
            else:
                sql = """
                  select to_char(a.ts - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts,a.bps_max AS bps_max,a.bps_avg AS bps_avg,a.pps_max AS pps_max,a.pps_avg AS pps_avg
                  from t_hosts_in_min5 a
                  left join ft_t_ip_protect b on a.ip=b.ip and a.ts between b.ts_open and nvl(b.ts_shut,b.ts_open+'10000 days'::interval)
                  where a.ip=%s and b.id is null and a.ts BETWEEN %s and %s and a.line=0 order by a.ts"""
                data = self.application.dbcurflow.queryall_dict(sql, (ip, starttime_dt, endtime_dt,))

        elif total_times <= 259200:

            sql = """
              select to_char(date_trunc('hour', a.ts) + CAST (FLOOR (EXTRACT(minutes FROM a.ts) / 15) * 15 || ' minutes'
              AS INTERVAL ) - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts,SUM(a.bps_max) AS bps_max,avg(a.bps_avg) AS bps_avg,sum(a.pps_max) AS pps_max,avg(a.pps_avg) AS pps_avg
              from t_hosts_in_min5 a
              left join ft_t_ip_protect b on a.ip=b.ip and a.ts between b.ts_open and nvl(b.ts_shut,b.ts_open+'10000 days'::interval)
              where a.ip=%s and b.id is null and a.ts BETWEEN %s and %s and a.line=0 group by to_char(date_trunc('hour', a.ts) + CAST (FLOOR (EXTRACT(minutes FROM a.ts) / 15) * 15 || ' minutes'
              AS INTERVAL ) - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') order by a.ts"""

            data = self.application.dbcurflow.queryall_dict(sql, (ip, starttime_dt, endtime_dt,))

        elif total_times <= 518400:
            sql = """
              select to_char(date_trunc('hour', a.ts) + CAST (FLOOR (EXTRACT(minutes FROM a.ts) / 30) * 30 || ' minutes'
              AS INTERVAL ) - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts,SUM(a.bps_max) AS bps_max,avg(a.bps_avg) AS bps_avg,sum(a.pps_max) AS pps_max,avg(a.pps_avg) AS pps_avg
              from t_hosts_in_min5 a
              left join ft_t_ip_protect b on a.ip=b.ip and a.ts between b.ts_open and nvl(b.ts_shut,b.ts_open+'10000 days'::interval)
              where a.ip=%s and b.id is null and a.ts BETWEEN %s and %s and a.line=0 group by to_char(date_trunc('hour', a.ts) + CAST (FLOOR (EXTRACT(minutes FROM a.ts) / 30) * 30 || ' minutes'
              AS INTERVAL ) - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ'),a.ts order by a.ts"""
            data = self.application.dbcurflow.queryall_dict(sql, (ip, starttime_dt, endtime_dt,))

        elif total_times <= 1036800:

            sql = """
              select to_char(date_trunc('day', a.ts) + CAST (FLOOR (EXTRACT(hour FROM a.ts) / 1) * 1 || ' hour' AS
              INTERVAL ) - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts,SUM(a.bps_max) AS bps_max,avg(a.bps_avg) AS bps_avg,sum(a.pps_max) AS pps_max,avg(a.pps_avg) AS pps_avg
              from t_hosts_in_min5 a
              left join ft_t_ip_protect b on a.ip=b.ip and a.ts between b.ts_open and nvl(b.ts_shut,b.ts_open+'10000 days'::interval)
              where a.ip=%s and b.id is null and a.ts BETWEEN %s and %s and a.line=0 group by to_char(date_trunc('day', a.ts) + CAST (FLOOR (EXTRACT(hour FROM a.ts) / 1) * 1 || ' hour' AS
              INTERVAL ) - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ'),a.ts order by a.ts"""

            data = self.application.dbcurflow.queryall_dict(sql, (ip, starttime_dt, endtime_dt,))

        else:

            sql = """
              select to_char(date_trunc('day', a.ts) + CAST (FLOOR (EXTRACT(hour FROM a.ts) / 3) * 3 || ' hour' AS
              INTERVAL ) - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts,SUM(a.bps_max) AS bps_max,avg(a.bps_avg) AS bps_avg,sum(a.pps_max) AS pps_max,avg(a.pps_avg) AS pps_avg
              from t_hosts_in_min5 a
              left join ft_t_ip_protect b on a.ip=b.ip and a.ts between b.ts_open and nvl(b.ts_shut,b.ts_open+'10000 days'::interval)
              where a.ip=%s and b.id is null and a.ts BETWEEN %s and %s and a.line=0 group by to_char(date_trunc('day', a.ts) + CAST (FLOOR (EXTRACT(hour FROM a.ts) / 3) * 3 || ' hour' AS
              INTERVAL ) - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ'),a.ts order by a.ts"""
            data = self.application.dbcurflow.queryall_dict(sql, (ip, starttime_dt, endtime_dt,))
        sinfo = {}
        sinfo['IPDataInfo'] = []
        data_info = {}
        data_info['MonitorDataMax'] = []
        data_info['MonitorData'] = []

        if data:
            for i in data:
                count_data = {}
                count_data['KBPS'] = 0 if i['bps_avg'] is None else int(int(i['bps_avg']) * band_m / 1000)
                count_data['PPS'] = 0 if i['pps_avg'] is None else int(int(i['pps_avg']) * band_m)
                count_data['KBPS_MAX'] = 0 if i['bps_max'] is None else int(int(i['bps_max']) * band_m / 1000)
                count_data['PPS_MAX'] = 0 if i['pps_max'] is None else int(int(i['pps_max']) * band_m)
                count_data['TimeStamp'] = i['ts'].replace('-T', 'T')
                data_info['MonitorData'].append(count_data)
        else:
            count_data = {}
            count_data['KBPS'] = 0
            count_data['PPS'] = 0
            count_data['KBPS_MAX'] = 0
            count_data['PPS_MAX'] = 0
            count_data['TimeStamp'] = starttime
            data_info['MonitorData'].append(count_data)

        count_data_max = {}
        count_data_max['KBPS_MAX'] = int(int(max_value) * band_m / 1000)
        count_data_max['PPS_MAX'] = int(int(max_pps) * band_m)
        count_data_max['TimeStamp'] = ts
        data_info['MonitorDataMax'].append(count_data_max)
        sinfo['IPDataInfo'].append(data_info)

        res.redata = sinfo
        raise gen.Return(res)
