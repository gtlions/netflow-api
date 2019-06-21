#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Gtlions Lai

import json
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from apps.API_BGP.config.config import CONFIG

urllib3.disable_warnings(InsecureRequestWarning)


class ZhiFirewall(object):
    def __init__(self, operator_network):
        if operator_network == 'cnc':
            self.url = CONFIG.ZhiFireWall.cnc_url
            self.number = 0
        elif operator_network == 'cmcc':
            self.url = CONFIG.ZhiFireWall.cmcc_url
            self.number = 1
        elif operator_network == 'ctc':
            self.url = CONFIG.ZhiFireWall.ctc_url
            self.number = 2

        self.user_date = json.dumps({"username": CONFIG.FireWall.user, "password": CONFIG.FireWall.pwd})
        self.login_url = self.url + 'auth'
        self.domain_url = self.url + 'domain/'
        self.iplist_url = self.url + 'iplist/'
        self.defence_url = self.url + 'defence/status/'
        self.label = 'CreatedByAPI'

    def login(self):
        s = requests.session()
        s.keep_alive = False
        page = s.post(self.login_url, data=self.user_date, verify=False)
        page_dict = json.loads(page.text)
        token = page_dict['data']['token']
        return token

    # 查询防火墙白名单
    def select_white_list(self, ip_add):
        token = self.login()
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer ' + token}
        black_page = requests.get(self.iplist_url + "black?search=" + ip_add, headers=headers, verify=False)
        white_page = requests.get(self.iplist_url + "white?search=" + ip_add, headers=headers, verify=False)
        black_dict = json.loads(black_page.text)
        white_dict = json.loads(white_page.text)
        black_rows = black_dict['data']['rows']
        white_rows = white_dict['data']['rows']
        if len(black_rows) != 0:
            return 'black'
        if len(white_rows) == 0:
            return 'null'
        for i in white_rows:
            if self.label in i['name']:
                return 'white'
            else:
                return 'null'

    # 添加IP至白名单
    def add_white_list(self, ip_add):
        condition = self.select_white_list(ip_add)
        if condition == 'black':
            return False
        if condition == 'white':
            return True
        else:
            token = self.login()
            headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer ' + token}
            page = requests.post(self.iplist_url + "white/ip/" + ip_add, headers=headers, verify=False)
            success = json.loads(page.text)['success']
            return success

    # 从白名单删除IP
    def del_white_list(self, ip_add):
        condition = self.select_white_list(ip_add)
        if condition != 'white':
            return True
        else:
            token = self.login()
            headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer ' + token}
            page = requests.delete(self.iplist_url + "white/ip/" + ip_add, headers=headers, verify=False)
            success = json.loads(page.text)['success']
            return success

    # 查询域名白名单
    def query_domain_name(self, domain):
        token = self.login()
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer ' + token}
        page = requests.get(self.domain_url + "white?search=" + domain, headers=headers, verify=False)
        white_dict = json.loads(page.text)
        rows = white_dict['data']['rows']
        domain_id = 0
        if len(rows) == 0:
            return False, domain_id
        for i in rows:
            if domain == i['name']:
                domain_id = i['id']
                return True, domain_id
            else:
                return False, domain_id

    # 添加域名至白名单
    def add_domain_name(self, domain):
        condition, domain_id = self.query_domain_name(domain)
        if not condition:
            token = self.login()
            headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer ' + token}
            data = {'name': domain, 'enable': 1}
            data = json.dumps(data)
            page = requests.post(self.domain_url + "white", headers=headers, data=data, verify=False)
            success = json.loads(page.text)['success']
            return success
        else:
            return True

    # 从白名单删除域名
    def del_domain_name(self, domain):
        condition, domain_id = self.query_domain_name(domain)
        if condition:
            token = self.login()
            headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer ' + token}
            page = requests.delete(self.domain_url + "white/" + str(domain_id), headers=headers, verify=False)
            success = json.loads(page.text)['success']
            return success
        else:
            return True

    # 查询防火墙屏蔽列表
    def select_block_list(self, ip_add):
        token = self.login()
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer ' + token}
        page1 = requests.get(self.defence_url + 'blocked?ruleType=1&dip=' + ip_add, headers=headers, verify=False)
        page2 = requests.get(self.defence_url + 'blocked?ruleType=2&dip=' + ip_add, headers=headers, verify=False)
        block_dict1 = json.loads(page1.text)
        block_dict2 = json.loads(page2.text)
        rows1 = block_dict1['data']['rows']
        rows2 = block_dict2['data']['rows']
        fb_dict = {}
        if rows1:
            for i in rows1:
                fb_dict[i['dip']+'-'+i['sip']] = i['time_out']
        if rows2:
            for i in rows2:
                fb_dict[i['dip']+'-'+i['sip']] = i['time_out']
        return fb_dict

    # 重置防火墙屏蔽列表
    def reset_block_list(self, ip_add, remote_ip):
        block_dict = self.select_block_list(ip_add)
        block = ip_add + '-' + remote_ip
        if block in block_dict:
            token = self.login()
            headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer ' + token}
            page = requests.delete(self.defence_url + 'blocked/chear?sip=' + remote_ip + '&dip=' + ip_add, headers=headers, verify=False)
            success = json.loads(page.text)['success']
            return success
        else:
            return True


if __name__ == '__main__':
    cc = ZhiFirewall('ctc')
    # cc = ZhiFirewall('cmcc')
    print(cc.select_white_list('10.10.10.3'))
    # print(cc.add_white_list('10.10.10.3'))
    # print(cc.del_white_list('10.10.10.3'))
