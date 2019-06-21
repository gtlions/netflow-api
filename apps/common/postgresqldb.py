#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Authors    : Gtlions Lai <gtlions.l@qq.com>
"""
"""
import psycopg2
from apps.common.pgdb_cursor_factory import PGDBCursorFactory


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


if __name__ == "__main__":
    host = '45.126.120.147'
    port = '5432'
    dbname = 'api'
    user = 'api'
    password = '9sppAFAFQZOVR6zL'
    db = PostgreSQLDB(host, port, user, password, dbname)
    ret = db.dbcur.queryone('select now();')
    print(ret)

# host = '36.248.12.73'
# port = 5432
# database = 'flowdb'
# user = 'collect'
# password = '9sppAFAFQZOVR6zL'
# dns = "host=" +host + " port=" + str(port) + " dbname=" + database +  " user=" + user + " password=" + password + " connect_timeout=3"
# conn=psycopg2.connect(dns)
# cur=conn.cursor()