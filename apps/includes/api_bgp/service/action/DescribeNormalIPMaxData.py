#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Gtlions Lai

from tornado import gen
import datetime
from apps.common import tools
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase
from apps.common.statusconfig import code
from apps.common.statusconfig import statusconfig as sc


class DescribeNormalIPMaxData(ActionBase):
    '''查看普通IP峰值信息与黑洞次数'''
    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        # self.application.logger.info(self.init_msg)

    @gen.coroutine
    def run(self):
        res = sc(code.Success)
        res.result = 'Success'

        ips = self.params['IP']
        user_org = self.params['AccessKeyId']
        starttime = self.params['StartTime']
        endtime = self.params['EndTime']
        ip_l = self.params['IP'].split(',')

        starttime_str = starttime.replace('T', ' ').replace('Z', '')
        endtime_str = endtime.replace('T', ' ').replace('Z', '')
        starttime_dt = datetime.datetime.strptime(starttime_str, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)
        endtime_dt = datetime.datetime.strptime(endtime_str, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)
        band_m = self.application.dbcur.queryone("select bandmultiple from t_users where ackid=%s", (user_org, ))[0]
        if starttime_dt > self.application.ts_begin or starttime_dt > endtime_dt:
            res = sc(code.TimeError)
            raise gen.Return(res)
        sinfo={}
        sinfo['DataSet'] = []
        for ip in ip_l:
            sql = 'select count(ip) from t_blockhole_his WHERE ip=%s and ts BETWEEN %s AND %s GROUP BY ip'
            black_hole = self.application.dbcurflow.queryone(sql, (ip, starttime_dt, endtime_dt))

            if datetime.datetime.now() - datetime.timedelta(days=30) > starttime_dt:  # 30天之外去day表
                sql = """select to_char(a.ts - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts,a.bps_max,a.bps_avg,a.pps_max,a.pps_avg from t_hosts_in_day a
                left join ft_t_ip_protect b on a.ip=b.ip and a.ts between b.ts_open and nvl(b.ts_shut,b.ts_open+'10000 days'::interval)
                where a.ip=%s and a.line=0 and b.id is null and a.ts between %s and %s
                order by a.bps_max desc"""
                data_max = self.application.dbcurflow.queryone(sql, (ip, starttime_dt, endtime_dt,))

            elif starttime_dt + datetime.timedelta(seconds=300) > endtime_dt:  # 时间差300秒以内
                from_time = datetime.datetime.strptime(tools.front5min(str(starttime_dt)), "%Y-%m-%d %H:%M:%S")
                sql = """select to_char(a.ts - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts,a.bps_max,a.bps_avg,a.pps_max,a.pps_avg from t_hosts_in_min5 a
                left join ft_t_ip_protect b on a.ip=b.ip and a.ts between b.ts_open and nvl(b.ts_shut,b.ts_open+'10000 days'::interval)
                where a.ip=%s and line=0 and b.id is null and a.ts = %s
                order by a.bps_max desc"""
                data_max = self.application.dbcurflow.queryone(sql, (ip, from_time,))
            else:  # 时间差300秒外，30天内5min表
                sql = """select to_char(a.ts - INTERVAL '8hour', 'YYYY-MM-DD-THH24:MI:SSZ') AS ts,a.bps_max,a.bps_avg,a.pps_max,a.pps_avg from t_hosts_in_min5 a
                left join ft_t_ip_protect b on a.ip=b.ip and a.ts between b.ts_open and nvl(b.ts_shut,b.ts_open+'10000 days'::interval)
                where a.ip=%s and line=0 and b.id is null and a.ts between %s and %s
                order by a.bps_max desc"""
                data_max = self.application.dbcurflow.queryone(sql, (ip, starttime_dt, endtime_dt,))
            ts = data_max[0].replace('-T', 'T') if data_max else tools.front5min(starttime)+'Z'
            max_value = data_max[1] if data_max else 0
            max_pps = data_max[2] if data_max else 0

            count_data_max = {}
            ip_data={}
            ip_data['IP'] = ip

            ip_data['MonitorDataMax'] = []
            count_data_max['KBPS_MAX'] = int(int(max_value) * band_m / 1000) if max_value else 0
            count_data_max['PPS_MAX'] = int(int(max_pps) * band_m) if max_value else 0
            count_data_max['TimeStamp'] = ts
            ip_data['MonitorDataMax'] = count_data_max
            ip_data['BlackHoleTimes'] = black_hole[0] if black_hole else 0
            sinfo['DataSet'].append(ip_data)

        res.redata = sinfo
        raise gen.Return(res)
