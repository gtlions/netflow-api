#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Authors    : Gtlions Lai <gtlions.l@qq.com>
"""
"""
import psycopg2.extras
from json import JSONEncoder

from apps.API_BGP.config.config import CONFIG
from apps.common.postgresqldb import PostgreSQLDB


def api_log_add_manual(cts, ip, ackid, api_id, api_detail, params, code, messages, status, duration=None):
    db_conn = PostgreSQLDB(CONFIG.DB.host, CONFIG.DB.port, CONFIG.DB.user,
                           CONFIG.DB.pwd, CONFIG.DB.dbname)

    t_api_logs_data = {}
    t_api_logs_data['cts'] = cts
    t_api_logs_data['ip'] = ip
    t_api_logs_data['ackid'] = ackid
    t_api_logs_data['api_id'] = api_id
    t_api_logs_data['api_detail'] = api_detail
    t_api_logs_data['params'] = JSONEncoder().encode(params) if type(params) is dict else params
    t_api_logs_data['code'] = code
    t_api_logs_data['messages'] = messages
    t_api_logs_data['status'] = status
    t_api_logs_data['duration'] = duration
    db_conn.dbcur.insert_dict('t_api_logs', t_api_logs_data)

def get_ip_serialuuids_old(user_org, user_end=None, ips=None, status=None):
    '''
    :param user_org:一级用户ID
    :param user_end: 二级用户ID
    :param ips: 字符串，IP记录，多个IP记录之间用逗号隔开
    :param status: IP状态，open--在用，close--已关闭
    :return: T_IP表的serialuuids组成的列表以及对应的字符串,ip组成的列表以及对应的字符串
    :返回示例:['a61068ae-782e-11e7-9eb8-000ec6c6d278', 'f97637c7-798c-11e7-a854-f45c899a7eaf'] "a61068ae-782e-11e7-9eb8-000ec6c6d278","f97637c7-798c-11e7-a854-f45c899a7eaf" ['10.1.1.2', '10.1.1.41'] "10.1.1.2","10.1.1.41"
    '''
    db_conn = PostgreSQLDB(CONFIG.PostgreSQLDB.host, CONFIG.PostgreSQLDB.port, CONFIG.PostgreSQLDB.user,
                           CONFIG.PostgreSQLDB.pwd, CONFIG.PostgreSQLDB.dbname)
    sqls = []
    sql = 'select serialnum,host(ip) ip from t_ip_protect where user_org=%s'
    sqls.append(sql)
    sql = " and ip in ('" + ips.replace(',', "','") + "')" if ips else ''
    sqls.append(sql)
    sql = " and user_end in ('" + user_end + "')" if user_end else ''
    sqls.append(sql)
    sql = " and status=True" if status == 'open' else ''
    sqls.append(sql)
    sql = " and status=False" if status == 'close' else ''
    sqls.append(sql)
    sql = " order by ip,id desc,status desc"
    sqls.append(sql)
    sql_all = ''.join(sqls)
    data = db_conn.dbcur.queryall_dict(sql_all, (user_org, ))
    l1 = []
    l2 = []
    for x in data:
        if x['ip'] not in l1:
            l1.append(x['ip'])
            l2.append(x)
    uuids_list = [x['serialnum'] for x in l2]
    uuids_str = '"' + ','.join(uuids_list).replace(',', '","') + '"' if uuids_list else None
    ips_list = [x['ip'] for x in l2]
    ips_str = '"' + ','.join(ips_list).replace(',', '","') + '"' if ips_list else None
    return uuids_list, uuids_str, ips_list, ips_str

def get_ip_serialuuids(user_org, user_end=None, ips=None, status=None):
    '''
    :param user_org:一级用户ID
    :param user_end: 二级用户ID
    :param ips: 字符串，IP记录，多个IP记录之间用逗号隔开
    :param status: IP状态，open--在用，close--已关闭
    :return: T_IP表的serialuuids组成的列表以及对应的字符串,ip组成的列表以及对应的字符串
    :返回示例:['a61068ae-782e-11e7-9eb8-000ec6c6d278', 'f97637c7-798c-11e7-a854-f45c899a7eaf'] "a61068ae-782e-11e7-9eb8-000ec6c6d278","f97637c7-798c-11e7-a854-f45c899a7eaf" ['10.1.1.2', '10.1.1.41'] "10.1.1.2","10.1.1.41"
    '''
    db_conn = PostgreSQLDB(CONFIG.PostgreSQLDB.host, CONFIG.PostgreSQLDB.port, CONFIG.PostgreSQLDB.user,
                           CONFIG.PostgreSQLDB.pwd, CONFIG.PostgreSQLDB.dbname)
    sqls = []
    # sql = "select WM_CONCAT(''''||serialnum||'''') serialnum,WM_CONCAT(''''||ip||'''') ip from (select serialnum,host(ip) as ip,rank() over(partition by ip order by ip,id desc,status desc) as rn from t_ip_protect where user_org=%s"
    sql = "select '['||WM_CONCAT(''''||serialnum||'''')||']' serialnum,'['||WM_CONCAT(''''||ip||'''')||']' ip from (select serialnum,host(ip) as ip,rank() over(partition by ip order by ip,id desc,status desc) as rn from t_ip_protect where user_org=%s"

    sqls.append(sql)
    sql = " and ip in ('" + ips.replace(',', "','") + "')" if ips else ''
    sqls.append(sql)
    sql = " and user_end in ('" + user_end + "')" if user_end else ''
    sqls.append(sql)
    sql = " and status=True" if status == 'open' else ''
    sqls.append(sql)
    sql = " and status=False" if status == 'close' else ''
    sqls.append(sql)
    sql = " ) a where rn=1"
    sqls.append(sql)
    sql_all = ''.join(sqls)
    data = db_conn.dbcur.queryall_dict(sql_all, (user_org,))[0] if db_conn.dbcur.queryall_dict(sql_all, (user_org,)) else None
    serialnum = data['serialnum']
    ip = data['ip']
    uuids_list = list(eval(serialnum)) if serialnum else []
    uuids_str = '"' + ','.join(uuids_list).replace(',', '","') + '"' if uuids_list else None
    ips_list = list(eval(ip)) if ip else []
    ips_str = '"' + ','.join(ips_list).replace(',', '","') + '"' if ips_list else None

    return uuids_list, uuids_str, ips_list, ips_str


if __name__ == "__main__":
    uuids_list, uuids_str, ips_list, ips_str = get_ip_serialuuids(user_org='dev1',
                                                                  ips='45.126.100.100')
    print((uuids_list, uuids_str, ips_list, ips_str),'rewr')

    # uuids_list, uuids_str, ips_list, ips_str = get_ip_serialuuids(user_org='dev1',
    #                                                               ips='45.126.120.147,100.100.100.189')
    # print((uuids_list, uuids_str, ips_list, ips_str),'rrrrrrrrrr')

    uuids_list, uuids_str, ips_list, ips_str = get_ip_serialuuids_old(user_org='dev1',
                                                                  ips='45.126.100.100')
    # r = netutil(['10.1.1.2', '10.1.1.257'])
    print((uuids_list, uuids_str, ips_list, ips_str),'rdsfa')
    #
    # uuids_list, uuids_str, ips_list, ips_str = get_ip_serialuuids_old(user_org='dev1',
    #                                                               ips='45.126.120.147,100.100.100.189')
    # print((uuids_list, uuids_str, ips_list, ips_str),'7777777777')
