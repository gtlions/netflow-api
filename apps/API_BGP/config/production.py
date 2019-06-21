#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apps.common.postgresqldb import PostgreSQLDB

ENV = 'PROD'

PGHOST = '10.35.0.86'
PGPORT = '5432'
PGUSER = 'api'
PGPWD = 'FAFQZOVR6zL'
PGDBNAME = 'api'

FLOW_PGHOST = '10.35.0.171'
FLOW_PGPORT = '5432'
FLOW_PGUSER = 'collect'
FLOW_PGPWD = 'FAFQZOVR6zL'
FLOW_PGDBNAME = 'collect'


db = PostgreSQLDB(PGHOST, PGPORT, PGUSER, PGPWD, PGDBNAME, application_name='Apps@API', connect_timeout=5)
data = db.dbcur.queryall_dict('select name,value,type,idx from t_sys_parameter')
sys_parameter = {ret['name'] + ret['idx']: {ret['idx']: ret['value']} for ret in data}


class ProductionConfig(object):
    class PostgreSQLDB():
        host = PGHOST
        user = PGUSER
        pwd = PGPWD
        port = PGPORT
        dbname = PGDBNAME

    class DB(PostgreSQLDB):
        pass

    class FlowPostgreSQLDB():
        host = FLOW_PGHOST
        user = FLOW_PGUSER
        pwd = FLOW_PGPWD
        port = FLOW_PGPORT
        dbname = FLOW_PGDBNAME

    class FlowDB(FlowPostgreSQLDB):
        pass

    class FireWall():
        user = sys_parameter['FIREWALL_USER' + 'Default']['Default']
        pwd = sys_parameter['FIREWALL_PASSWORD' + 'Default']['Default']

    class ZXFireWall():
        cc_url = sys_parameter['FIREWALL_URL' + 'CC']['CC']

    class ZhiFireWall():
        cnc_url = sys_parameter['ZHI_FIREWALL_URL' + 'CNC']['CNC']
        ctc_url = sys_parameter['ZHI_FIREWALL_URL' + 'CTC']['CTC']
        cmcc_url = sys_parameter['ZHI_FIREWALL_URL' + 'CMCC']['CMCC']
