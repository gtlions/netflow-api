#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Gtlions Lai

import os
import psycopg2
import psycopg2.extensions
import psycopg2.extras
import psycopg2.pool


ENV = os.getenv('BGPAPPS_ENV')

if ENV == 'PROD':
    pg_host = '10.35.0.86'
    pg_port = '5432'
    pg_user = 'api'
    pg_pwd = 'FAFQZOVR6zL'
    pg_dbname = 'api'
else:
    # pg_host = '45.126.122.143'
    pg_host = '127.0.0.1'
    pg_port = '5432'
    pg_user = 'api'
    pg_pwd = '9sppAFAFQZOVR6zL'
    pg_dbname = 'api'


class PGDBCursorFactory(psycopg2.extensions.cursor):
    def __init__(self, query, vars=None):
        psycopg2.extensions.cursor.__init__(self, query, vars)

    def execute(self, query, vars=None):
        return psycopg2.extensions.cursor.execute(self, query, vars)


class PostgreSQLDB(object):
    def __init__(self, host, port, user, pwd, dbname, *args, **kwargs):
        self.host = host
        self.port = port
        self.user = user
        self.password = pwd
        self.dbname = dbname
        self.dns = "host=" + self.host + " port=" + \
                   str(self.port) + " dbname=" + self.dbname + \
                   " user=" + self.user + " password=" + self.password + " connect_timeout=15"
        self.dbconn = psycopg2.connect(self.dns)
        self.dbcur = self.dbconn.cursor(cursor_factory=PGDBCursorFactory)


def clear_api_log():
    postgre = PostgreSQLDB(pg_host, pg_port, pg_user, pg_pwd, pg_dbname)
    postgre.dbcur.execute("""
        INSERT INTO t_api_info_his (ts, api_id, api_name, count_suc, count_all ) SELECT CURRENT_DATE, api_id, api_name,
        count_suc, count_all FROM t_api_info;UPDATE t_api_info SET count_suc=0, count_all=0;""")
    postgre.dbconn.commit()
    postgre.dbconn.close()


if __name__ == '__main__':
    clear_api_log()
