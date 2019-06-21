#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Gtlions Lai

import datetime
import requests
import re

from bs4 import BeautifulSoup
from datetime import timedelta
from apps.API_BGP.config.config import CONFIG


def block_ctc_log():
    url = CONFIG.CTCFireWall.firewall_url
    record_way = CONFIG.RecordLog.record_way
    user_date = {'param_type': 'login', 'param_username': CONFIG.CTCFireWall.user,
                 'param_password': CONFIG.CTCFireWall.pwd}
    login_url = url + 'cgi-bin/login.cgi'
    fb_link_url = url + 'cgi-bin/status_fblink.cgi'
    dt = datetime.datetime.now()
    mysqlhelp = MySQLHelper(CONFIG.MySQLDB.host, CONFIG.MySQLDB.port, CONFIG.MySQLDB.user, CONFIG.MySQLDB.pwd)
    mysqlhelp.selectDb(CONFIG.MySQLDB.db)
    s = requests.session()
    s.post(login_url, data=user_date)
    sel_ip = {'param_submit_type': 'select', 'param_filter': '', 'param_this_sort': '-3'}
    page = s.post(fb_link_url, data=sel_ip)
    soup = BeautifulSoup(page.content, 'html.parser')
    if record_way == 'new':
        tag_str = str(soup.find('page_title'))
        page_list = re.findall(r"\d+\.?\d*", tag_str[-25:])
        page_num = int(page_list[0])
        for num in range(page_num):
            new_page = s.post(fb_link_url, data={'param_submit_type': 'show', 'param_filter': '',
                                                 'param_page': num, 'param_this_sort': '-3'})
            new_soup = BeautifulSoup(new_page.content, 'html.parser')
            la_list = new_soup.find_all('local_address')
            ra_list = new_soup.find_all('remote_address')
            rt_list = new_soup.find_all('release_time')
            for ra_tag in ra_list:
                la = la_list.pop(0).string
                ra = ra_tag.string
                rt = rt_list.pop(0).string[10:-8]
                record = mysqlhelp.queryRow('SELECT COUNT(0) FROM t_fw_block_list_log WHERE sourceip="' + la + '" AND remoteip="'+ ra + '" AND type=1')
                if record == (0,):
                    mysqlhelp.insert('t_fw_block_list_log', {'sourceip': la, 'remoteip': ra, 'releasetime': rt,
                                                             'type': 1, 'createdt': dt})
                else:
                    pass
    else:
        la_list = soup.find_all('local_address')
        ra_list = soup.find_all('remote_address')
        rt_list = soup.find_all('release_time')
        for ra_tag in ra_list:
            la = la_list.pop(0).string
            ra = ra_tag.string
            rt = rt_list.pop(0).string[10:-8]
            old_rt = mysqlhelp.queryRow('SELECT releasetime FROM t_fw_block_list_log WHERE sourceip="' + la + '" AND remoteip="' + ra + '" AND type=1 ORDER BY createdt DESC')
            if old_rt is None:
                mysqlhelp.insert('t_fw_block_list_log', {'sourceip': la, 'remoteip': ra, 'releasetime': rt,
                                                         'type': 1, 'createdt': dt})
            else:
                old_finish_time = mysqlhelp.queryRow('SELECT SUBDATE(createdt,INTERVAL -"' + old_rt[0] +'" SECOND) AS finishdt FROM t_fw_block_list_log WHERE sourceip="' + la + '" AND remoteip="' + ra + '" AND type=1 ORDER BY createdt DESC')[0]
                new_finish_time = dt + timedelta(seconds=int(rt)) - timedelta(seconds=5)
                if new_finish_time > old_finish_time:
                    mysqlhelp.insert('t_fw_block_list_log', {'sourceip': la, 'remoteip': ra, 'releasetime': rt,
                                                             'type': 1, 'createdt': dt})
                else:
                    pass


def block_cmcc_log():
    url = CONFIG.CMCCFirewall.firewall_url
    user_date = {'param_type': 'login', 'param_username': CONFIG.CMCCFirewall.user,
                 'param_password': CONFIG.CMCCFirewall.pwd}
    record_way = CONFIG.RecordLog.record_way
    login_url = url + 'cgi-bin/login.cgi'
    fb_link_url = url + 'cgi-bin/status_fblink.cgi'
    dt = datetime.datetime.now()
    mysqlhelp = MySQLHelper(CONFIG.MySQLDB.host, CONFIG.MySQLDB.port, CONFIG.MySQLDB.user, CONFIG.MySQLDB.pwd)
    mysqlhelp.selectDb(CONFIG.MySQLDB.db)
    s = requests.session()
    s.post(login_url, data=user_date)
    sel_ip = {'param_submit_type': 'select', 'param_filter': '', 'param_this_sort': '-3'}
    page = s.post(fb_link_url, data=sel_ip)
    soup = BeautifulSoup(page.content, 'html.parser')
    if record_way == 'new':
        tag_str = str(soup.find('page_title'))
        page_list = re.findall(r"\d+\.?\d*", tag_str[-25:])
        page_num = int(page_list[0])
        for num in range(page_num):
            new_page = s.post(fb_link_url, data={'param_submit_type': 'show', 'param_filter': '',
                                                 'param_page': num, 'param_this_sort': '3'})
            new_soup = BeautifulSoup(new_page.content, 'html.parser')
            la_list = new_soup.find_all('local_address')
            ra_list = new_soup.find_all('remote_address')
            rt_list = new_soup.find_all('release_time')
            for ra_tag in ra_list:
                la = la_list.pop(0).string
                ra = ra_tag.string
                rt = rt_list.pop(0).string[10:-8]
                record = mysqlhelp.queryRow('SELECT COUNT(0) FROM t_fw_block_list_log WHERE sourceip="' + la + '" AND remoteip="'+ ra + '" AND type=3')
                if record == (0,):
                    mysqlhelp.insert('t_fw_block_list_log', {'sourceip': la, 'remoteip': ra, 'releasetime': rt,
                                                             'type': 3, 'createdt': dt})
                else:
                    pass
    else:
        la_list = soup.find_all('local_address')
        ra_list = soup.find_all('remote_address')
        rt_list = soup.find_all('release_time')
        for ra_tag in ra_list:
            la = la_list.pop(0).string
            ra = ra_tag.string
            rt = rt_list.pop(0).string[10:-8]
            old_rt = mysqlhelp.queryRow('SELECT releasetime FROM t_fw_block_list_log WHERE sourceip="' + la + '" AND remoteip="' + ra + '" AND type=3 ORDER BY createdt DESC')
            if old_rt is None:
                mysqlhelp.insert('t_fw_block_list_log', {'sourceip': la, 'remoteip': ra, 'releasetime': rt,
                                                         'type': 3, 'createdt': dt})
            else:
                old_finish_time = mysqlhelp.queryRow('SELECT SUBDATE(createdt,INTERVAL -"' + old_rt[0] +'" SECOND) AS finishdt FROM t_fw_block_list_log WHERE sourceip="' + la + '" AND remoteip="' + ra + '" AND type=3 ORDER BY createdt DESC')[0]
                new_finish_time = dt + timedelta(seconds=int(rt)) - timedelta(seconds=5)
                if new_finish_time > old_finish_time:
                    mysqlhelp.insert('t_fw_block_list_log', {'sourceip': la, 'remoteip': ra, 'releasetime': rt,
                                                             'type': 3, 'createdt': dt})
                else:
                    pass


def block_cnc_log():
    url = CONFIG.CNCFirewall.firewall_url
    record_way = CONFIG.RecordLog.record_way
    user_date = {'param_type': 'login', 'param_username': CONFIG.CNCFirewall.user,
                 'param_password': CONFIG.CNCFirewall.pwd}
    login_url = url + 'cgi-bin/login.cgi'
    fb_link_url = url + 'cgi-bin/status_fblink.cgi'
    dt = datetime.datetime.now()
    mysqlhelp = MySQLHelper(CONFIG.MySQLDB.host, CONFIG.MySQLDB.port, CONFIG.MySQLDB.user, CONFIG.MySQLDB.pwd)
    mysqlhelp.selectDb(CONFIG.MySQLDB.db)
    s = requests.session()
    s.post(login_url, data=user_date)
    sel_ip = {'param_submit_type': 'select', 'param_filter': '', 'param_this_sort': '-3'}
    page = s.post(fb_link_url, data=sel_ip)
    soup = BeautifulSoup(page.content, 'html.parser')
    if record_way == 'new':
        tag_str = str(soup.find('page_title'))
        page_list = re.findall(r"\d+\.?\d*", tag_str[-25:])
        page_num = int(page_list[0])
        for num in range(page_num):
            new_page = s.post(fb_link_url, data={'param_submit_type': 'show', 'param_filter': '',
                                                 'param_page': num, 'param_this_sort': '3'})
            new_soup = BeautifulSoup(new_page.content, 'html.parser')
            la_list = new_soup.find_all('local_address')
            ra_list = new_soup.find_all('remote_address')
            rt_list = new_soup.find_all('release_time')
            for ra_tag in ra_list:
                la = la_list.pop(0).string
                ra = ra_tag.string
                rt = rt_list.pop(0).string[10:-8]
                record = mysqlhelp.queryRow(
                    'SELECT COUNT(0) FROM t_fw_block_list_log WHERE sourceip="' + la + '" AND remoteip="' + ra + '" AND type=2')
                if record == (0,):
                    mysqlhelp.insert('t_fw_block_list_log', {'sourceip': la, 'remoteip': ra, 'releasetime': rt,
                                                             'type': 2, 'createdt': dt})
                else:
                    pass
    else:
        la_list = soup.find_all('local_address')
        ra_list = soup.find_all('remote_address')
        rt_list = soup.find_all('release_time')
        for ra_tag in ra_list:
            la = la_list.pop(0).string
            ra = ra_tag.string
            rt = rt_list.pop(0).string[10:-8]
            old_rt = mysqlhelp.queryRow('SELECT releasetime FROM t_fw_block_list_log WHERE sourceip="' + la + '" AND remoteip="' + ra + '" AND type=2 ORDER BY createdt DESC')
            if old_rt is None:
                mysqlhelp.insert('t_fw_block_list_log', {'sourceip': la, 'remoteip': ra, 'releasetime': rt,
                                                         'type': 2, 'createdt': dt})
            else:
                old_finish_time = mysqlhelp.queryRow('SELECT SUBDATE(createdt,INTERVAL -"' + old_rt[0] +'" SECOND) AS finishdt FROM t_fw_block_list_log WHERE sourceip="' + la + '" AND remoteip="' + ra + '" AND type=2 ORDER BY createdt DESC')[0]
                new_finish_time = dt + timedelta(seconds=int(rt)) - timedelta(seconds=5)
                if new_finish_time > old_finish_time:
                    mysqlhelp.insert('t_fw_block_list_log', {'sourceip': la, 'remoteip': ra, 'releasetime': rt,
                                                             'type': 2, 'createdt': dt})
                else:
                    pass

if __name__ == '__main__':
    block_cmcc_log()
