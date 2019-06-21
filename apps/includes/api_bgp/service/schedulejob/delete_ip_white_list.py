#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Gtlions Lai

import logging
import datetime
import psycopg2.extras
from tornado import netutil
from apps.API_BGP.config.config import CONFIG, logger_name
from apps.common.my_thread import MyThread
from apps.common.postgresqldb import PostgreSQLDB
from apps.common.zhi_firewall import ZhiFirewall
from apps.common.zx_firewall import Firewall
logger = logging.getLogger(logger_name)


def delete_white_list(operator, hostname):
    zhifirewalllist = ['ctc', 'cmcc']
    firewall = ZhiFirewall(operator) if operator in zhifirewalllist else Firewall(operator)
    if netutil.is_valid_ip(hostname) is True:
        return firewall.del_white_list(hostname)
    else:
        return firewall.del_domain_name(hostname)


def delete_ip_white_list():
    zhifirewalllist = ['ctc', 'cmcc']
    postgre = PostgreSQLDB(CONFIG.PostgreSQLDB.host, CONFIG.PostgreSQLDB.port, CONFIG.PostgreSQLDB.user,
                           CONFIG.PostgreSQLDB.pwd, CONFIG.PostgreSQLDB.dbname)
    sql = "SELECT p5,p1,p2 FROM t_job WHERE actions='DeleteWhiteList' AND ts_actions<=now();"
    data = postgre.dbcur.queryall_dict(sql)
    if data:
        for i in data:
            wl_condition = {}
            ipOrPackage = i['p5']
            hostname = i['p1']
            status_num = int(i['p2'])
            thread_list = []
            if status_num == 15:
                firewalllist = ['ctc', 'cmcc', 'cnc', 'cc']
            elif status_num == 12:
                firewalllist = ['ctc', 'cc']
            elif status_num == 10:
                firewalllist = ['cmcc', 'cc']
            elif status_num == 9:
                firewalllist = ['cnc', 'cc']
            else:
                break
            for j in firewalllist:
                t = MyThread(delete_white_list, args=(j, hostname))
                thread_list.append(t)
            for t in thread_list:
                t.start()
            for t in thread_list:
                t.join()
            for index, item in enumerate(thread_list):
                wl_condition[firewalllist[index]] = item.get_result()
            for k, v in wl_condition.items():
                if v is True:
                    firewall = ZhiFirewall(k) if k in zhifirewalllist else Firewall(k)
                    status_num = status_num ^ 2 ** firewall.number
            if len(ipOrPackage) > 20:
                update_sql = 'UPDATE t_firewall SET status=%s, updatedt=%s WHERE hostname=%s AND package_protect_id=%s;'
                postgre.dbcur.execute(update_sql, (status_num, datetime.datetime.now(), hostname, str(ipOrPackage),))
            else:
                update_sql = 'UPDATE t_firewall SET status=%s, updatedt=%s WHERE hostname=%s AND ip=%s;'
                postgre.dbcur.execute(update_sql, (status_num, datetime.datetime.now(), hostname, str(ipOrPackage),))
            update_sql = 'UPDATE t_job SET p2=%s WHERE p1=%s AND p5=%s;'
            postgre.dbcur.execute(update_sql, (status_num, hostname, ipOrPackage,))
    postgre.dbcur.execute("DELETE FROM t_job WHERE actions='DeleteWhiteList' AND p2='0';")
    postgre.dbconn.commit()


if __name__ == '__main__':
    delete_ip_white_list()
