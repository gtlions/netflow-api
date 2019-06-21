#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apps.common.postgresqldb import PostgreSQLDB

ENV = 'DEBUG'

PGHOST = '45.126.120.122'
PGPORT = '5432'
PGUSER = 'api'
PGPWD = '9sppAFAFQZOVR6zL'
PGDBNAME = 'apidbg'

FLOW_PGHOST = '45.126.121.216'
FLOW_PGPORT = '5432'
FLOW_PGUSER = 'api'
FLOW_PGPWD = '9sppAFAFQZOVR6zL'
FLOW_PGDBNAME = 'flowdb'


db = PostgreSQLDB(PGHOST, PGPORT, PGUSER, PGPWD, PGDBNAME, application_name='Apps@API', connect_timeout=5)
data = db.dbcur.queryall_dict('select name,value,type,idx from t_sys_parameter')
sys_parameter = {ret['name'] + ret['idx']: {ret['idx']: ret['value']} for ret in data}
# block_parameter = {ret['name'] + ret['idx']: {ret['idx']: ret['value']} for ret in data}


class DebugConfig(object):
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
        ctc_url = sys_parameter['FIREWALL_URL' + 'CTC']['CTC']
        cmcc_url = sys_parameter['FIREWALL_URL' + 'CMCC']['CMCC']
        cnc_url = sys_parameter['FIREWALL_URL' + 'CNC']['CNC']
        cc_url = sys_parameter['FIREWALL_URL' + 'CC']['CC']

    class ZhiFireWall():
        ctc_url = sys_parameter['ZHI_FIREWALL_URL' + 'CTC']['CTC']
        cmcc_url = sys_parameter['ZHI_FIREWALL_URL' + 'CMCC']['CMCC']

        # # 电信InfluxDB
        # class CTCInfluxDB():
        #     host = '45.126.121.216'
        #     port = 8086
        #     user = 'kpy'
        #     pwd = 'Kpy@2016'
        #     db = 'graphite'
        #
        # # 移动InfluxDB
        # class CMCCInfluxDB():
        #     host = '125.77.23.86'
        #     port = 8086
        #     user = 'kpy'
        #     pwd = 'Kpy@2016'
        #     db = 'graphite'
        #
        # # 联通InfluxDB
        # class CNCInfluxDB():
        #     host = '125.77.23.98'
        #     port = 8086
        #     user = 'kpy'
        #     pwd = 'Kpy@2016'
        #     db = 'graphite'
        #
        # class CTCFastNetMon():
        #     ctcmax = ['ctcmax_ctc', int(sys_parameter['THRESHOLD_CTCMAX' + 'CTC']['CTC'])]
        #     bgpmax = ['bgpmax_ctc', int(sys_parameter['THRESHOLD_BGPMAX' + 'CTC']['CTC'])]
        #     superctcmax = ['superctcmax_ctc', int(sys_parameter['THRESHOLD_SUPERCTCMAX' + 'CTC']['CTC'])]
        #     superbgpmax = ['superbgpmax_ctc', int(sys_parameter['THRESHOLD_SUPERBGPMAX' + 'CTC']['CTC'])]
        #     fastmon_hostgroup = sys_parameter['FT_URL_HOSTGROUP' + 'CTC']['CTC']
        #     fastmon_commit = sys_parameter['FT_URL_COMMIT' + 'CTC']['CTC']
        #
        # class CMCCFastNetMon():
        #     bgpmax = ['bgpmax_cmcc', int(sys_parameter['THRESHOLD_BGPMAX' + 'CMCC']['CMCC'])]
        #     superbgpmax = ['superbgpmax_cmcc', int(sys_parameter['THRESHOLD_SUPERBGPMAX' + 'CMCC']['CMCC'])]
        #     fastmon_hostgroup = sys_parameter['FT_URL_HOSTGROUP' + 'CMCC']['CMCC']
        #     fastmon_commit = sys_parameter['FT_URL_COMMIT' + 'CMCC']['CMCC']
        #
        # class CNCFastNetMon():
        #     bgpmax = ['bgpmax_cnc', int(sys_parameter['THRESHOLD_BGPMAX' + 'CNC']['CNC'])]
        #     superbgpmax = ['superbgpmax_cnc', int(sys_parameter['THRESHOLD_SUPERBGPMAX' + 'CNC']['CNC'])]
        #     fastmon_hostgroup = sys_parameter['FT_URL_HOSTGROUP' + 'CNC']['CNC']
        #     fastmon_commit = sys_parameter['FT_URL_COMMIT' + 'CNC']['CNC']
