#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import datetime
from apps.API_BGP.config.config import CONFIG
from apps.API_BGP.config.config import logger_name
from apps.common.postgresqldb import PostgreSQLDB
logger = logging.getLogger(logger_name)


def CheckProtectPackageDueTime():
    ts = datetime.datetime.now() + datetime.timedelta(minutes=3)
    postgre = PostgreSQLDB(CONFIG.PostgreSQLDB.host, CONFIG .PostgreSQLDB.port, CONFIG.PostgreSQLDB.user,
                           CONFIG.PostgreSQLDB.pwd, CONFIG.PostgreSQLDB.dbname)

    sql = "select date_trunc('day',ts_due) as ts_due,id from t_package_protect WHERE status=TRUE and protect_state in ('1','2') and date_trunc('day',ts_due)<%s"
    data = postgre.dbcur.queryall_dict(sql, (ts, ))
    for package in data:
        # sql = "INSERT INTO t_ip_protect_his (serialnum,ip,region,zone,protect_base,protect_max,protect_state,user_org,user_end,status,metric_pct_bps,metric_pct_pps,ts_open,ts_shut,actions,cts,iptype,bandtype) select serialnum,ip,region,zone,protect_base,protect_max,protect_state,user_org,user_end,status,metric_pct_bps,metric_pct_pps,ts_open,ts_shut,'CheckProtectPackageDueTime',%s,iptype,bandtype from t_ip_protect where t_ip_protect.package=%s and t_ip_protect.status=TRUE "
        # postgre.dbcur.execute(sql, (str(ts), package['id'], ))
        # sql = "INSERT INTO t_package_protect_his (package,ipnums,package_protect_id,package_protect_name,user_org,user_end,protect_state,ts_open,ts_shut,serialnum,status,cts,actions) SELECT package,ipnums,package_protect_id,package_protect_name,user_org,user_end,protect_state,ts_open,ts_shut,serialnum,status,%s,'CheckProtectPackageDueTime'FROM t_package_protect WHERE package =%s;"
        # postgre.dbcur.execute(sql, (str(ts), package['id'], ))
        sql = 'update t_package_protect set protect_state=0 WHERE id=%s AND status=TRUE '
        postgre.dbcur.execute(sql, (package['id'], ))
        sql = 'update t_ip_protect set protect_state=0 WHERE package=%s and status=TRUE '
        postgre.dbcur.execute(sql, (package['id'], ))
        sql = "SELECT 'insert into t_ip_protect_his( '||wm_concat(column_name)||',cts,actions) select '||wm_concat(column_name)||',%s,%s from t_ip_protect where package=%s'from information_schema.columns " \
              "where table_name ='t_ip_protect' and column_name != 'id';"
        postgre.dbcur.execute(sql)
        real_sql = postgre.dbcur.fetchone()[0]
        postgre.dbcur.execute(real_sql, (str(ts), 'CheckProtectPackageDueTime', package['id'],))
        sql = "SELECT 'insert into t_package_protect_his( '||wm_concat(column_name)||',cts,actions) select '||wm_concat(column_name)||',%s,%s from t_package_protect where id=%s'from information_schema.columns " \
              "where table_name ='t_package_protect' and column_name != 'id';"
        postgre.dbcur.execute(sql)
        real_sql = postgre.dbcur.fetchone()[0]
        postgre.dbcur.execute(real_sql, (str(ts), 'CheckProtectPackageDueTime', package['id'],))

        postgre.dbconn.commit()

if __name__ == '__main__':
    CheckProtectPackageDueTime()
