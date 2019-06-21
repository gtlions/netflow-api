#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Gtlions Lai

import os
import re
import datetime
import psutil
from apps.API_BGP.config.config import CONFIG
from apps.common.postgresqldb import PostgreSQLDB


def get_server_info():
    postgre = PostgreSQLDB(CONFIG.PostgreSQLDB.host, CONFIG.PostgreSQLDB.port, CONFIG.PostgreSQLDB.user,
                           CONFIG.PostgreSQLDB.pwd, CONFIG.PostgreSQLDB.dbname)
    ts = datetime.datetime.now()
    text = os.popen("ps -ef | grep API_BGP").read()
    content = re.findall(r'-p\s\d{1,5}', text)
    port = content[0].split()[1]
    cpu_num = psutil.cpu_count()
    mem_total = psutil.virtual_memory().total
    server_info = {}
    server_info['api_ts'] = ts
    server_info['cpu_num'] = cpu_num
    server_info['mem_total'] = mem_total
    server_info['port'] = port
    postgre.dbcur.insert_dict('t_server_info', server_info)
    postgre.dbconn.commit()
    postgre.dbconn.close()


if __name__ == '__main__':
    pass
