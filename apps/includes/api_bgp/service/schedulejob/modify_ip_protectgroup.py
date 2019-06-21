#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import datetime
from apps.API_BGP.config.config import CONFIG
from apps.API_BGP.config.config import logger_name
from apps.common.postgresqldb import PostgreSQLDB
logger = logging.getLogger(logger_name)


def modify_ip_protectgroup():
    ts = datetime.datetime.now()
    postgre = PostgreSQLDB(CONFIG.PostgreSQLDB.host, CONFIG .PostgreSQLDB.port, CONFIG.PostgreSQLDB.user,
                           CONFIG.PostgreSQLDB.pwd, CONFIG.PostgreSQLDB.dbname)
    sql = "select b.protect_state as protect,a.id as id,a.serialnum as serialnum,a.ip as ip,a.actions as actions,a.ts_actions as ts_actions,a.p1 as p1,a.p2 as p2,a.p3 as p3,a.p4 as p4,b.serialnum as serialnum from t_job a,t_ip_protect b where a.ip=b.ip and a.p5=b.serialnum and a.actions='ModifyIPProtectGroup' and a.ts_actions<=now() ORDER BY a.id"
    data = postgre.dbcur.queryall_dict(sql)
    ret = {k['serialnum']: [v for v in data if v['serialnum'] == k['serialnum']] for k in data}

    for k, v in list(ret.items()):
        if len(v) > 2:
            continue
        ip_info = {}
        for i in v:
            job_id = i['id']
            ip_info['ip'] = i['ip']
            ip_info['serialnum'] = i['serialnum']
            serialnum = ip_info['serialnum']

            if i['p1'] == 'guaranteeprotect':
                ip_info['protect_base'] = i['p4']
                sql = "delete from t_job where actions='ModifyIPProtectGroup' and id= %s"
                postgre.dbcur.execute(sql, (job_id,))

            if i['p1'] == 'elasticprotect':
                ip_info['protect_max'] = i['p4']
                sql = "delete from t_job where actions='ModifyIPProtectGroup' and id=%s"
                postgre.dbcur.execute(sql, (job_id,))

            postgre.dbcur.update_dict('t_ip_protect', ip_info, 'serialnum', serialnum)

            sql = "SELECT 'insert into t_ip_protect_his( '||wm_concat(column_name)||',cts,actions) select '||wm_concat(column_name)||',%s,%s from t_ip_protect where serialnum=%s'from information_schema.columns " \
                  "where table_name ='t_ip_protect' and column_name != 'id';"
            postgre.dbcur.execute(sql)
            real_sql = postgre.dbcur.fetchone()[0]
            postgre.dbcur.execute(real_sql, (str(ts), 'ModifyIPProtectGroup',  ip_info['serialnum'],))
        # sql = "INSERT INTO t_ip_protect_his (serialnum,ip,region,zone,protect_base,protect_max,protect_state,user_org,user_end,status,metric_pct_bps,metric_pct_pps,ts_open,ts_shut,actions,cts,iptype,bandtype) select serialnum,ip,region,zone,protect_base,protect_max,protect_state,user_org,user_end,status,metric_pct_bps,metric_pct_pps,ts_open,ts_shut,'ModifyIPProtectGroup',%s,iptype,bandtype from t_ip_protect where serialnum=%s"
        # postgre.dbcur.execute(sql, (str(ts), serilnum,))

            postgre.dbconn.commit()


def modify_package():
    ts = datetime.datetime.now()
    postgre = PostgreSQLDB(CONFIG.PostgreSQLDB.host, CONFIG.PostgreSQLDB.port, CONFIG.PostgreSQLDB.user,
                           CONFIG.PostgreSQLDB.pwd, CONFIG.PostgreSQLDB.dbname)
    sql = 'select t_job.id, p1,p3,p4,p5 from t_job LEFT JOIN t_package_protect aa on t_job.serialnum=aa.package_protect_id where t_job.ip is NULL and aa.status=TRUE and t_job.ts_actions<= now()'
    package_data = postgre.dbcur.queryall_dict(sql)
    for i in package_data:
        package_info = {}
        package_info['package_protect_id'] = i['p5']
        if i['p1'] == 'guaranteeprotect':
            package_info['protect_base'] = i['p4']
            sql = 'update t_ip_protect aa set protect_base=%s WHERE package=(select id FROM t_package_protect WHERE package_protect_id=%s)AND aa.status=TRUE;'
            postgre.dbcur.execute(sql, (package_info['protect_base'], package_info['package_protect_id'],))
            # sql = "INSERT INTO t_ip_protect_his (serialnum,ip,region,zone,protect_base,protect_max,protect_state,user_org,user_end,status,metric_pct_bps,metric_pct_pps,ts_open,ts_shut,actions,cts,iptype,bandtype,protect_previous) select serialnum,ip,region,zone,protect_base,protect_max,protect_state,user_org,user_end,status,metric_pct_bps,metric_pct_pps,ts_open,ts_shut,'ModifyProtectPackage',%s,iptype,bandtype,protect_previous from t_ip_protect where package=(select id FROM t_package_protect WHERE package_protect_id=%s)"
            # postgre.dbcur.execute(sql, (str(ts), package_info['package_protect_id'],))

        if i['p1'] == 'elasticprotect':
            package_info['protect_max'] = i['p4']
            sql = 'update t_ip_protect aa set protect_max=%s WHERE package=(select id FROM t_package_protect WHERE package_protect_id=%s)AND aa.status=TRUE ;'
            postgre.dbcur.execute(sql, (package_info['protect_max'], package_info['package_protect_id'],))
            # sql = "INSERT INTO t_ip_protect_his (serialnum,ip,region,zone,protect_base,protect_max,protect_state,user_org,user_end,status,metric_pct_bps,metric_pct_pps,ts_open,ts_shut,actions,cts,iptype,bandtype,protect_previous) select serialnum,ip,region,zone,protect_base,protect_max,protect_state,user_org,user_end,status,metric_pct_bps,metric_pct_pps,ts_open,ts_shut,'ModifyProtectPackage',%s,iptype,bandtype,protect_previous from t_ip_protect where package=(select id FROM t_package_protect WHERE package_protect_id=%s)"
            # postgre.dbcur.execute(sql, (str(ts), package_info['package_protect_id'],))

        sql = "SELECT 'insert into t_ip_protect_his( '||wm_concat(column_name)||',cts,actions) select '||wm_concat(column_name)||',%s,%s from t_ip_protect where package=(select id FROM t_package_protect WHERE package_protect_id=%s)'from information_schema.columns " \
              "where table_name ='t_ip_protect' and column_name != 'id';"
        postgre.dbcur.execute(sql)
        real_sql = postgre.dbcur.fetchone()[0]
        postgre.dbcur.execute(real_sql, (str(ts), 'ModifyProtectPackage', package_info['package_protect_id'],))

        sql = "delete from t_job where actions='ModifyProtectPackage' and id=%s"
        postgre.dbcur.execute(sql, (i['id'],))
        postgre.dbcur.update_dict('t_package_protect', package_info, 'package_protect_id', package_info['package_protect_id'])
        # sql = 'insert into t_package_protect_his(ts_due,protect_base,protect_max,package,ipnums,package_protect_id,package_protect_name,user_org,user_end,protect_state,ts_open,ts_shut,serialnum,status,cts,actions) select ts_due,protect_base,protect_max,package,ipnums,package_protect_id,package_protect_name,user_org,user_end,protect_state,ts_open,ts_shut,serialnum,status,%s,%s from t_package_protect where package_protect_id=%s;'
        # postgre.dbcur.execute(sql, (str(ts), 'ModifyProtectPackage', package_info['package_protect_id']))
        sql = "SELECT 'insert into t_package_protect_his( '||wm_concat(column_name)||',cts,actions) select '||wm_concat(column_name)||',%s,%s from t_package_protect where package_protect_id=%s'from information_schema.columns " \
              "where table_name ='t_package_protect' and column_name != 'id';"
        postgre.dbcur.execute(sql)
        real_sql = postgre.dbcur.fetchone()[0]
        postgre.dbcur.execute(real_sql, (str(ts), 'ModifyProtectPackage', package_info['package_protect_id'],))
        postgre.dbconn.commit()

if __name__ == '__main__':
    modify_ip_protectgroup()
    modify_package()
