#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Gtlions Lai

from tornado import gen

from apps.common.apicom import get_ip_serialuuids
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class DescribeIPStatus(ActionBase):
    '''查看高防IP的状态'''

    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        # self.application.logger.info(self.init_msg)

    def get_ban_list(self, uuids_str):
        sql = "SELECT host(ip) AS ip, coalesce(line_id, 'all') as line,to_char((ts - INTERVAL '8 hours'), 'YYYY-MM-DD-THH24:MI:SSZ') AS createdt,to_char((ts + ft_t_blockhole.ban_time - INTERVAL '8 hours'), 'YYYY-MM-DD-THH24:MI:SSZ') AS enddt FROM ft_t_blockhole LEFT JOIN t_line  ON ft_t_blockhole.line = t_line.id WHERE ts + ft_t_blockhole.ban_time>now() AND ip in (SELECT ip FROM t_ip_protect WHERE serialnum IN ('" + uuids_str.replace('"', '') + "'))"
        data = self.application.dbcur.queryall_dict(sql)
        ban_info = {}
        blackhole_info = {}
        if data is None:
            return ban_info
        for i in data:
            blackhole_info.setdefault(i['line'], [i['createdt'], i['enddt']])
            ban_info[i['ip']] = blackhole_info
        return ban_info

    @gen.coroutine
    def run(self):
        res = sc(code.Success)
        res.result = 'Success'

        ips = self.params['IP'] if 'IP' in self.params else None
        user_org = self.params['AccessKeyId']
        user_end = self.params['IPUserID'] if 'IPUserID' in self.params else None

        data_info = {}
        data_info['IPStatusData'] = []
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
            uuids_list, uuids_str, _, _ = get_ip_serialuuids(user_org=user_org, user_end=user_end, ips=ip, status='open')
            if uuids_list:
                sql = "SELECT host(ip) AS ip,(SELECT pp.protect_id AS guaranteeprotect FROM t_ip_protect aa,t_protect pp WHERE aa.serialnum in (%s) AND aa.protect_base = pp.id),(SELECT pp.protect_id AS elasticprotect FROM t_ip_protect aa, t_protect pp WHERE aa.serialnum in (%s) AND aa.protect_max = pp.id),protect_state AS protect FROM t_ip_protect WHERE serialnum in (%s)"
                data = self.application.dbcur.queryall_dict(sql, (uuids_str.replace('"', ''), uuids_str.replace('"', ''), uuids_str.replace('"', ''),))
                ip_lists = {}
                for i in data:
                    ip_lists[i['ip']] = [i['guaranteeprotect'], i['elasticprotect'], i['protect']]
                ips = list(ip_lists.keys())

                ban_lists = self.get_ban_list(uuids_str)
                for ip in ips:
                    ip_status = {}
                    ip_status['IP'] = ip
                    if ip in list(ban_lists.keys()):
                        ip_status['IPStatus'] = 'BlackHole'
                        blackhole = {}
                        for blackhole_k in list(ban_lists[ip].keys()):
                            details = {}
                            details.setdefault('StartTime', ban_lists[ip][blackhole_k][0].replace('-T', 'T'))
                            details.setdefault('EndTime', ban_lists[ip][blackhole_k][1].replace('-T', 'T'))
                            blackhole.setdefault(blackhole_k, details)
                        ip_status['BlackHoleStatus'] = blackhole
                        if ip_lists[ip][2] == 2:
                            ip_status['protectGroupStatus'] = 'Elastic'
                        elif ip_lists[ip][2] == 1:
                            ip_status['protectGroupStatus'] = 'Guarantee'
                        else:
                            ip_status['protectGroupStatus'] = 'Close'

                    else:
                        ip_status['IPStatus'] = 'Normal'
                        ip_status['BlackHoleStatus'] = {}
                        if ip_lists[ip][2] == 2:
                            ip_status['protectGroupStatus'] = 'Elastic'
                        elif ip_lists[ip][2] == 1:
                            ip_status['protectGroupStatus'] = 'Guarantee'
                        else:
                            ip_status['protectGroupStatus'] = 'Close'
                    data_info['IPStatusData'].append(ip_status)
            else:
                res = sc(code.IPNotUsed)
                res.result = res.result % str(ip)
                raise gen.Return(res)

        res.redata = data_info
        raise gen.Return(res)
