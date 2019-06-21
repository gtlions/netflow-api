#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors    : Gtlions Lai <gtlions.l@qq.com>
import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        args = self.request.arguments

        self.params = {}
        for a in args:
            self.params.setdefault(a, self.get_argument(a))

        self.fileparams = self.request.files
        for f in self.fileparams:
            self.params.setdefault(f, "file")

    def on_finish(self):
        try:
            self.application.dbconn.commit()
        except Exception as exc:
            print('-错误-dbconn commit error.')
            print(exc)

        try:
            self.application.dbpool.putconn(self.application.dbconn)
        except Exception as exc:
            print('-错误-dbconn putconn error.')
            print(exc)

        try:
            self.application.dbconnflow.commit()
        except Exception as exc:
            print('-错误-dbconnflow commit error.')
            print(exc)

        try:
            self.application.dbpoolflow.putconn(self.application.dbconnflow)
        except Exception as exc:
            print('-错误-dbconnflow putconn error.')
            print(exc)

    def history_backup_t_ip_protect(self, filter,column_extra_value):
        target_table = 't_ip_protect_his'
        source_table = 't_ip_protect'
        column_ignore = ['id']
        column_extra = 'cts,actions'
        column_extra_value = column_extra_value
        filter = filter
        execute_sql=''
        sql="select 'insert into '||%s||'('||col||','||%s from (select WM_CONCAT(attname) over(partition by attrelid order by attnum) col,row_number() over( order by attnum desc) rn from pg_attribute where attrelid = %s::regclass and attnum>0 and not attisdropped and attname<>all(%s)) a where rn=1;"
        self.application.dbcur.execute(sql, (target_table,column_extra, source_table, column_ignore))
        execute_sql+=self.application.dbcur.fetchone()[0]
        sql="select ') select '|| col||%s||' from '||%s||' where 1=1 and '||%s from (select WM_CONCAT(attname) over(partition by attrelid order by attnum) col,row_number() over( order by attnum desc) rn from pg_attribute where attrelid = %s::regclass and attnum>0 and not attisdropped and attname<>all(%s)) a where rn=1;"
        self.application.dbcur.execute(sql,(column_extra_value,source_table,filter,source_table,column_ignore))
        execute_sql += self.application.dbcur.fetchone()[0]
        self.application.dbcur.execute(execute_sql)

    def history_backup_t_package_protect(self, filter,column_extra_value):
        target_table = 't_package_protect_his'
        source_table = 't_package_protect'
        column_ignore = ['id']
        column_extra = 'cts,actions'
        column_extra_value = column_extra_value
        filter = filter
        execute_sql=''
        sql="select 'insert into '||%s||'('||col||','||%s from (select WM_CONCAT(attname) over(partition by attrelid order by attnum) col,row_number() over( order by attnum desc) rn from pg_attribute where attrelid = %s::regclass and attnum>0 and attname<>all(%s)) a where rn=1;"
        self.application.dbcur.execute(sql, (target_table,column_extra, source_table, column_ignore))
        execute_sql+=self.application.dbcur.fetchone()[0]
        sql="select ') select '|| col||%s||' from '||%s||' where 1=1 and '||%s from (select WM_CONCAT(attname) over(partition by attrelid order by attnum) col,row_number() over( order by attnum desc) rn from pg_attribute where attrelid = %s::regclass and attnum>0 and attname<>all(%s)) a where rn=1;"
        self.application.dbcur.execute(sql,(column_extra_value,source_table,filter,source_table,column_ignore))
        execute_sql += self.application.dbcur.fetchone()[0]
        self.application.dbcur.execute(execute_sql)