#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Authors    : Gtlions Lai <gtlions.l@qq.com>
"""
"""
import uuid
import requests
import MySQLdb

conn = MySQLdb.connect(host="36.248.12.89", port=3306, user="bgp",
                       passwd="FAFQZOVR6zL", db="bgp")
cur = conn.cursor()


class CTCFastNetMon():
    ctcmax = ['ctcmax_ctc', 600]
    bgpmax = ['bgpmax_ctc', 600]
    superctcmax = ['superctcmax_ctc', 600]
    superbgpmax = ['superbgpmax_ctc', 600]
    fastmon_blackhole_list = 'http://ddosanti-ctc-inc.youdomain.com/fnm/api/blackhole'
    fastmon_hostgroup = 'http://ddosanti-ctc-inc.youdomain.com/fnm/api/hostgroup'
    fastmon_commit = 'http://ddosanti-ctc-inc.youdomain.com/fnm/api/commit'


class CMCCFastNetMon():
    bgpmax = ['bgpmax_cmcc', 15]
    superbgpmax = ['superbgpmax_cmcc', 15]
    fastmon_blackhole_list = 'http://125.77.23.86/fnm/api/blackhole'
    fastmon_hostgroup = 'http://125.77.23.86/fnm/api/hostgroup'
    fastmon_commit = 'http://125.77.23.86/fnm/api/commit'


class CNCFastNetMon():
    bgpmax = ['bgpmax_cnc', 75]
    superbgpmax = ['superbgpmax_cnc', 75]
    fastmon_blackhole_list = 'http://125.77.23.98/fnm/api/blackhole'
    fastmon_hostgroup = 'http://125.77.23.98/fnm/api/hostgroup'
    fastmon_commit = 'http://125.77.23.98/fnm/api/commit'

def get_hostgroup(url, ip):
    r = requests.get(url)
    re = eval(r.text)['hostgruop']
    hostgroup = ''
    for group in re:
        dic_all = {}
        for d in group['data']:
            dic_all.update(d)
        if ip in [x.strip() for x in dic_all['networks'].split(',')]:
            hostgroup = group['name']
            break
    return hostgroup

def gen_his_open_ts():
    sql = 'select id,ip from t_ip_history where open_ts is null order by ip,id,cts'
    cur.execute(sql)
    data = cur.fetchall()
    for i in data:
        id,ip = i
        sql='select open_ts from t_ip_history where action="AddProtectGroupIP" and ip="'+ip+'" and status=1 and id<'+str(id)+' order by cts desc limit 1'
        cur.execute(sql)
        open_ts=cur.fetchone()[0]
        # print id,ip,str(open_ts)
        sql='update t_ip_history set open_ts="'+str(open_ts)+'" where id='+str(id)
        cur.execute(sql)
    conn.commit()
#
def gen_his_serial():
    sql = 'select id,ip from t_ip_history where action="AddProtectGroupIP"'
    cur.execute(sql)
    data = cur.fetchall()
    for i in data:
        id,ip = i
        sql='update t_ip_history set serialuuid="'+str(uuid.uuid1())+'" where id='+str(id)
        cur.execute(sql)

    sql = 'select id,ip from t_ip_history where serialuuid is null order by ip,id,cts'
    cur.execute(sql)
    data = cur.fetchall()
    for i in data:
        id,ip = i
        sql='select serialuuid from t_ip_history where action="AddProtectGroupIP" and ip="'+ip+'" and status=1 and id<'+str(id)+' order by cts desc limit 1'
        cur.execute(sql)
        serialuuid=cur.fetchone()[0]
        # print id,ip,str(open_ts)
        sql='update t_ip_history set serialuuid="'+serialuuid+'" where id='+str(id)
        cur.execute(sql)
    conn.commit()


def gen_ip_serial():
    sql = 'select ip,count(1) num from t_ip_history where action="AddProtectGroupIP" group by ip having count(1)=1'
    cur.execute(sql)
    data = cur.fetchall()
    for i in data:
        ip,num = i
        sql='select serialuuid from t_ip_history where action="AddProtectGroupIP" and ip="'+ip+'"'
        cur.execute(sql)
        serialuuid=cur.fetchone()[0]
        sql='update t_ip set serialuuid="'+serialuuid+'" where ip="'+ip+'"'
        cur.execute(sql)

    sql='select id,ip,serialuuid from t_ip_history where ip in (select  ip from t_ip_history where action="AddProtectGroupIP" group by  ip having count(1)>1) order by ip,id,cts'
    cur.execute(sql)
    data = cur.fetchall()
    for i in data:
        id,ip,serialuuid=i
        sql='select * from t_ip where ip="'+ip+'" and serialuuid="'+serialuuid+'"'
        cur.execute(sql)
        data = cur.fetchone()
        if data:
            sql='delete from t_ip where ip="'+ip+'" and serialuuid="'+serialuuid+'"'
            cur.execute(sql)
        sql='insert into t_ip(ip,ackid,ipuserid,bandtype,region,zone,guaranteeprotect,elasticprotect,protect,ctcprotect,cmccprotect,cncprotect,metric_bps_percent,open_ts,close_ts,status,serialuuid)' \
            'select ip,ackid,ipuserid,bandtype,region,zone,guaranteeprotect,elasticprotect,protect,ctcprotect,cmccprotect,cncprotect,metric_bps_percent,open_ts,close_ts,status,serialuuid from t_ip_history where id='+str(id)
        cur.execute(sql)
    sql = 'delete from t_ip where length(serialuuid)=0'
    cur.execute(sql)
    conn.commit()

def gen_ip_open_ts():
    sql = "select ip,count(1) num from t_ip_history where action='AddProtectGroupIP' and ip in (SELECT ip FROM  t_ip where open_Ts is null) group by ip having count(1)=1"
    cur.execute(sql)
    data = cur.fetchall()
    for i in data:
        ip,num = i
        sql='select open_ts from t_ip_history where action="AddProtectGroupIP" and ip="'+ip+'"'
        cur.execute(sql)
        open_ts=cur.fetchone()[0]
        sql='update t_ip set open_ts="'+str(open_ts)+'" where ip="'+ip+'"'
        cur.execute(sql)
    conn.commit()

gen_his_open_ts()
gen_his_serial()
gen_ip_serial()
gen_ip_open_ts()