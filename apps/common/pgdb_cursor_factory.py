#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Authors    : Gtlions Lai <gtlions.l@qq.com>
"""
"""
import psycopg2.extensions
import psycopg2.extras
import psycopg2.pool
import re


class PGDBCursorFactory(psycopg2.extensions.cursor):
    def __init__(self, query, vars=None):
        psycopg2.extensions.cursor.__init__(self, query, vars)

    def execute(self, query, vars=None):
        return psycopg2.extensions.cursor.execute(self, query, vars)

    def queryone(self, query, vars=None):
        psycopg2.extensions.cursor.execute(self, query, vars)
        datas = psycopg2.extensions.cursor.fetchone(self)
        return datas

    def queryone_dict(self, query, vars=None):
        try:
            psycopg2.extensions.cursor.execute(self, query, vars)
            columns = self.description
            datas = psycopg2.extensions.cursor.fetchone(self)
            ret = []
            _d = {}
            for i in range(0, len(datas)):
                _d[columns[i][0]] = datas[i]
            ret.append(_d)
            return ret
        except Exception as exc:
            print(exc)

    def queryall(self, query, vars=None):
        psycopg2.extensions.cursor.execute(self, query, vars)
        datas = psycopg2.extensions.cursor.fetchall(self)
        return datas

    def queryall_dict(self, query, vars=None):
        try:
            psycopg2.extensions.cursor.execute(self, query, vars)
            columns = self.description
            datas = psycopg2.extensions.cursor.fetchall(self)
            ret = []
            for data in datas:
                _d = {}
                for i in range(0, len(data)):
                    _d[columns[i][0]] = data[i]
                ret.append(_d)
            return ret
        except Exception as exc:
            print(exc)

    def insert_dict(self, table, data, noneisnull=False):
        p_data = {}
        for key in data:
            if noneisnull and data[key] is None:
                pass
            else:
                p_data[key] = "'" + str(data[key]) + "'"
        key = ','.join(list(p_data.keys()))
        value = ','.join(list(p_data.values()))
        real_sql = "INSERT INTO " + table + " (" + key + ") VALUES (" + value + ");"
        # print(real_sql)
        strinfo = re.compile("'None'")
        real_sql = strinfo.sub('NULL', real_sql)
        return psycopg2.extensions.cursor.execute(self, real_sql)

    def update_dict(self, table, data, where_key, where_value, noneisnull=False):
        p_data = {}
        for k in data:
            p_data[k] = "'" + str(data[k]) + "'"
        real_sql = "update " + table
        real_sql += ' set '
        for k in list(p_data.keys()):
            real_sql += k
            real_sql += "="
            real_sql += p_data[k]
            real_sql += ","
        real_sql = real_sql[0:-1] + " where " + where_key + "='" + where_value + "'"
        return psycopg2.extensions.cursor.execute(self, real_sql)

    def update_double(self, table, data, where_key, where_value, where_key1, where_value1, noneisnull=False):
        p_data = {}
        for k in data:
            p_data[k] = "'" + str(data[k]) + "'"
        real_sql = "update " + table
        real_sql += ' set '
        for k in list(p_data.keys()):
            real_sql += k
            real_sql += "="
            real_sql += p_data[k]
            real_sql += ","
        real_sql = real_sql[0:-1] + " where " + where_key + "='" + where_value + "' and " + where_key1 + "='" + where_value1 + "'"
        return psycopg2.extensions.cursor.execute(self, real_sql)


class PGDBCursorFactoryDBG(psycopg2.extensions.cursor):
    def __init__(self, query, vars=None):
        psycopg2.extensions.cursor.__init__(self, query, vars)
        # psycopg2.extras.register_inet()

    #
    # def execute(self, query, vars=None):
    #     return psycopg2.extensions.cursor.execute(self, query, vars)
    def queryone(self, query, vars=None):
        psycopg2.extensions.cursor.execute(self, query, vars)
        datas = psycopg2.extensions.cursor.fetchone(self)
        return datas


if __name__ == "__main__":
    import psycopg2

    host = '45.126.120.147'
    port = '5432'
    dbname = 'apidbg'
    user = 'api'
    password = '9sppAFAFQZOVR6zL'
    dns = "host=" + host + " port=" + \
          port + " dbname=" + dbname + \
          " user=" + user + " password=" + password + " connect_timeout=15"
    conn = psycopg2.connect(dns)
    cur = conn.cursor(cursor_factory=PGDBCursorFactoryDBG)
    # cur.execute('select ip from t_ip_protect')
    # ret=cur.fetchone()
    # print(ret[0])
    # psycopg2.extras.register_inet()
    print(cur.mogrify('SELECT ip FROM t_ip_protect where ip in %s and status=1',
                      (tuple(psycopg2.extras.Inet(x) for x in ['10.1.1.1']),)))
