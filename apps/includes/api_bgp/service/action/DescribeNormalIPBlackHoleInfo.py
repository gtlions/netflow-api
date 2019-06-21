#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Gtlions Lai

import datetime
from tornado import gen

from apps.includes.api_bgp.service.actionbase.action_base import ActionBase
from apps.common.statusconfig import code
from apps.common.statusconfig import statusconfig as sc
from apps.common.apicom import get_ip_serialuuids


class DescribeNormalIPBlackHoleInfo(ActionBase):
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
        ip_l = ips.split(',')
        data_info = {}
        data_info['IPBlackHoleData'] = []
        for ip in ip_l:
            sql = """
            SELECT HOST (ip) AS ip, CASE WHEN line=0 THEN 'total' WHEN line=1 then 'ctc' when line=2 then 'cmcc' WHEN line=3 THEN 'cnc'END as line, to_char((ts - INTERVAL '8 hours'), 'YYYY-MM-DD-THH24:MI:SSZ')
            AS createdt, to_char((ts + b.ban_time- INTERVAL '8 hours'), 'YYYY-MM-DD-THH24:MI:SSZ') AS enddt,
            current_value, threshold_value, to_char(b.ban_time,'HH24:MI:SS') AS ban_time, direction FROM
            t_blockhole b WHERE ip = %s"""
            data = self.application.dbcurflow.queryall_dict(sql, (ip,))
            count_data = {}
            count_data['IP'] = ip
            count_data['Line'] = data[0]['line'] if data else ''
            count_data['Createdt'] = data[0]['createdt'].replace('-T', 'T') if data else ''
            count_data['Enddt'] = data[0]['enddt'].replace('-T', 'T') if data else ''
            count_data['Current_value'] = data[0]['current_value'] if data else ''
            count_data['Threshold_value'] = data[0]['threshold_value'] if data else ''
            count_data['Ban_time'] = data[0]['ban_time'] if data else ''
            count_data['Direction'] = data[0]['direction'] if data else ''
            count_data['IPState'] = 'Normal' if not data else 'BlackHole'
            data_info['IPBlackHoleData'].append(count_data)

        res = sc(code.Success)
        res.result = 'Success'
        res.redata = data_info
        raise gen.Return(res)
