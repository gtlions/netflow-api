#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Gtlions Lai

import datetime
from tornado import gen

from apps.includes.api_bgp.service.actionbase.action_base import ActionBase
from apps.common.statusconfig import code
from apps.common.statusconfig import statusconfig as sc
from apps.common.apicom import get_ip_serialuuids


class DescribeBlackHoleInfo(ActionBase):
    '''查询IP黑洞信息'''

    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        # self.application.logger.info(self.init_msg)

    @gen.coroutine
    def run(self):
        ips = self.params['IP'] if 'IP' in self.params else None
        user_org = self.params['AccessKeyId']
        user_end = self.params['IPUserID'] if 'IPUserID' in self.params else None
        starttime = self.params['StartTime']
        endtime = self.params['EndTime']
        dt = self.application.ts_begin

        starttime_str = starttime.replace('T', ' ').replace('Z', '')
        endtime_str = endtime.replace('T', ' ').replace('Z', '')
        starttime_dt = datetime.datetime.strptime(starttime_str, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)
        endtime_dt = datetime.datetime.strptime(endtime_str, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)

        if starttime_dt > dt or starttime_dt > endtime_dt or starttime_dt + datetime.timedelta(hours=24) < dt:
            res = sc(code.TimeError)
            raise gen.Return(res)

        data_info = {}
        data_info['IPBlockHoleData'] = []
        if ips:
            ip_l = ips.split(',')
            if 'IPUserID' in self.params:
                sql = "SELECT count(*) from t_ip_protect where ip IN ('" + ips.replace(',', "','") + "')and user_org=%s AND user_end=%s and status = True AND iptype=0"
                ip_data = self.application.dbcur.queryall_dict(sql, (user_org, user_end))
                if ip_data[0]['count'] != len(ip_l):
                    res = sc(code.PermissionDenied)
                    res.result = res.result % str(ip_l)
                    raise gen.Return(res)
        else:
            ip_l = []
            if 'IPUserID' in self.params:
                sql = "SELECT HOST (ip) AS ip FROM t_ip_protect WHERE user_org=%s AND user_end=%s AND status=TRUE AND iptype=0"
                ip_data = self.application.dbcur.queryall_dict(sql, (user_org, user_end,))
            else:
                sql = "SELECT HOST (ip) AS ip FROM t_ip_protect WHERE user_org=%s AND status=TRUE AND iptype=0"
                ip_data = self.application.dbcur.queryall_dict(sql, (user_org,))
            for i in ip_data:
                ip_l.append(i['ip'])
            ip_l = list(set(ip_l))
            ips = ",".join(ip_l)
        ips = ips.replace(",", "','")

        if len(ips) == 0:
            sql = """
            SELECT HOST (ip) AS ip, line_id AS line, to_char((ts - INTERVAL '8 hours'), 'YYYY-MM-DD-THH24:MI:SSZ')
            AS createdt, to_char((ts + b.ban_time- INTERVAL '8 hours'), 'YYYY-MM-DD-THH24:MI:SSZ') AS enddt,
            current_value, threshold_value, to_char(b.ban_time,'HH24:MI:SS') AS ban_time, direction FROM
            t_blockhole_his b LEFT JOIN ft_t_line ON b.line =
            ft_t_line.id WHERE b.ts BETWEEN %s AND %s"""
        else:
            sql = """
            SELECT HOST (ip) AS ip, line_id AS line, to_char((ts - INTERVAL '8 hours'), 'YYYY-MM-DD-THH24:MI:SSZ')
            AS createdt, to_char((ts + b.ban_time- INTERVAL '8 hours'), 'YYYY-MM-DD-THH24:MI:SSZ') AS enddt,
            current_value, threshold_value, to_char(b.ban_time,'HH24:MI:SS') AS ban_time, direction FROM
            t_blockhole_his b LEFT JOIN ft_t_line ON b.line =
            ft_t_line.id WHERE b.ts BETWEEN %s AND %s AND ip IN ('""" + ips + """')"""
        data = self.application.dbcurflow.queryall_dict(sql, (starttime_dt, endtime_dt,))

        if data:
            for i in data:
                count_data = {}
                count_data['IP'] = i['ip']
                count_data['Line'] = i['line']
                count_data['Createdt'] = i['createdt'].replace('-T', 'T')
                count_data['Enddt'] = i['enddt'].replace('-T', 'T')
                count_data['Current_value'] = i['current_value']
                count_data['Threshold_value'] = i['threshold_value']
                count_data['Ban_time'] = i['ban_time']
                count_data['Direction'] = i['direction']
                data_info['IPBlockHoleData'].append(count_data)

        res = sc(code.Success)
        res.result = 'Success'
        res.redata = data_info
        raise gen.Return(res)
