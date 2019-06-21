#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Gtlions Lai

import datetime
import psycopg2.extras
from tornado import gen
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class GetIPMetricInfo(ActionBase):
    '''获取高防IP预警信息'''

    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        # self.application.logger.info(self.init_msg)

    @gen.coroutine
    def run(self):
        res = sc(code.Success)
        res.result = 'Success'
        current_dt = self.application.ts_begin

        if ('StartTime' not in self.params and 'EndTime' in self.params) or (
                        'StartTime' in self.params and 'EndTime' not in self.params):
            res = sc(code.ParamNotPair)
            res.result = res.result % ('StartTime', 'EndTime')
            raise gen.Return(res)

        user_org = self.params['AccessKeyId']
        sql = 'select serialnum,host(ip) ip from t_ip_protect where user_org= %s order by ip,status desc,ts_open desc'
        data = self.application.dbcur.queryall_dict(sql, (user_org,))

        if 'IP' in self.params:
            ip_l = self.params['IP'].split(',')
            sql = 'select serialnum,host(ip) ip from t_ip_protect where user_org= %s and ip in %s order by ip,status desc ,ts_open desc '
            data = self.application.dbcur.queryall_dict(sql, (user_org, tuple(self.makeinet(x) for x in ip_l)))

        if 'IPUserID' in self.params:
            user_end = self.params['IPUserID']
            ip_l = self.params['IP'].split(',')
            sql = 'select serialnum,host(ip) ip from t_ip_protect where user_org= %s and ip in (%s) AND user_end = %s order by ip,status desc ,ts_open desc '
            data = self.application.dbcur.queryall_dict(sql, (user_org, tuple(self.makeinet(x) for x in ip_l), user_end))

        l1 = []
        l2 = []
        for x in data:
            if x['ip'] not in l1:
                l1.append(x['ip'])
                l2.append(x)

        serialuuids = [x['serialnum'] for x in l2]
        serialuuids_s = ",".join(serialuuids).replace(',', "','")
        serialuuids_s = "'" + serialuuids_s + "'"

        sql = 'select host(ip) ip from t_ip_protect where serialnum in (' + serialuuids_s + ')'
        data = self.application.dbcur.queryall_dict(sql)
        iplist_l = [psycopg2.extras.Inet(x['ip']) for x in data]

        clrts = current_dt
        if 'StartTime' not in self.params and 'EndTime' not in self.params:
            sql = "select name,host(ip) ip,to_char((ts - INTERVAL '8 HOUR'), 'YYYY-MM-DD-THH24:MI:SSZ') ts,current,threshold,line,ratio::FLOAT ,msg,alerttype from t_metric_msg where ts<=%s and ts > now()-INTERVAL '24 HOUR' and ip=any(%s) and getstate=0 order by ip,ts;"
            data = self.application.dbcurflow.queryall_dict(sql, (current_dt, iplist_l))

            # get_sql = "select name,host(ip) ip,to_char((ts - INTERVAL '8 HOUR'), 'YYYY-MM-DD-THH24:MI:SSZ') ts,current,threshold,line,ratio::FLOAT ,msg,alerttype from t_metric_msg where ts<=%s and ip in ("+iplist_s+") and getstate=0 order by ip,ts;"
            # data = self.application.dbcur.queryall_dict(get_sql, (current_dt,))
        else:
            if 'StartTime' in self.params:
                starttime = self.params['StartTime']
                starttime = datetime.datetime.strptime(starttime.replace('T', ' ').replace('Z', ''),
                                                       '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)
            if 'EndTime' in self.params:
                endtime = self.params['EndTime']
                endtime = datetime.datetime.strptime(endtime.replace('T', ' ').replace('Z', ''),
                                                     '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)

            if starttime > endtime:
                res = sc(code.TimeError)
                raise gen.Return(res)
            if (endtime - starttime).days != 0 and (endtime - starttime).seconds > 600:
                res = sc(code.TimeIntervalTooLong)
                res.result = res.result % '600秒'
                raise gen.Return(res)

            sql = "select name,host(ip) ip,to_char((ts - INTERVAL '8 HOUR'), 'YYYY-MM-DD-THH24:MI:SSZ') ts,current,threshold,line,ratio::FLOAT ,msg,alerttype from t_metric_msg where ts between %s and %s and ts > now()-INTERVAL '24 HOUR' and ip=any(%s) and getstate=0 order by ip,ts"
            data = self.application.dbcurflow.queryall_dict(sql, (starttime, endtime, iplist_l))

            clrts = endtime

        sql = 'update t_metric_msg set getstate=1 where ts<=%s and ip=any(%s);'
        self.application.dbcurflow.execute(sql, (clrts, iplist_l))

        data_info = {}
        data_info['IPMetricsInfoData'] = []
        for ipinfo in data:
            sinfo = {}
            sinfo['Name'] = ipinfo['name']
            sinfo['IP'] = ipinfo['ip']
            sinfo['Timestamp'] = ipinfo['ts'].replace('-T', 'T')
            sinfo['Current'] = ipinfo['current']
            sinfo['Threshold'] = ipinfo['threshold']
            sinfo['Line'] = ipinfo['line']
            sinfo['Ratio'] = ipinfo['ratio']
            sinfo['Msg'] = ipinfo['msg']
            sinfo['Type'] = ipinfo['alerttype']
            data_info['IPMetricsInfoData'].append(sinfo)
        res.redata = data_info
        raise gen.Return(res)
