#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Gtlions Lai

import re
import requests
from bs4 import BeautifulSoup

from apps.common.statusconfig import statusconfig as sc, code
from apps.API_BGP.config.config import CONFIG


class Firewall(object):
    def __init__(self, operator_network):
        if operator_network == 'cnc':
        #   self.url = CONFIG.ZXFireWall.cnc_url
            self.number = 0
        # elif operator_network == 'cmcc':
        #     self.url = CONFIG.ZXFireWall.cmcc_url
        #     self.number = 1
        # elif operator_network == 'ctc':
        #     self.url = CONFIG.ZXFireWall.ctc_url
        #     self.number = 2
        elif operator_network == 'cc':
            self.url = CONFIG.ZXFireWall.cc_url
            self.number = 3

        self.user_date = {'param_type': 'login', 'param_username': CONFIG.FireWall.user,
                          'param_password': CONFIG.FireWall.pwd}
        self.login_url = self.url + 'cgi-bin/login.cgi'
        self.bw_list_url = self.url + 'cgi-bin/status_bwlist.cgi'
        self.domain_url = self.url + 'cgi-bin/status_domains.cgi'
        self.fb_link_url = self.url + 'cgi-bin/status_fblink.cgi'
        self.hostset_url = self.url + 'cgi-bin/status_hostset.cgi'

    # 查询防火墙黑白名单
    def select_white_list(self, ip_add):
        s = requests.session()
        s.post(self.login_url, data=self.user_date)
        data = {'param_submit_type': 'select', 'param_address': ip_add, 'param_page': '0', 'param_this_sort': '1'}
        page = s.post(self.bw_list_url, data=data)
        soup = BeautifulSoup(page.content, 'html.parser')
        all_flags = soup.find_all('flags')
        address = soup.find_all('address')
        if all_flags:
            for index, add in enumerate(address[1:]):
                if add.string == ip_add:
                    num = index
                    if all_flags[num].string == 'whitelist':
                        return 'white'
                    elif soup.find('flags').string == 'blacklist':
                        return 'black'
                else:
                    return 'null'
        else:
            return 'null'

    # 添加IP至白名单
    def add_white_list(self, ip_add):
        s = requests.session()
        s.keep_alive = False
        s.post(self.login_url, data=self.user_date)
        data = {'param_submit_type': 'submit', 'param_address': '+' + ip_add, 'param_page': '0',
                'param_this_sort': '1'}
        page = s.post(self.bw_list_url, data=data)
        soup = BeautifulSoup(page.content, 'html.parser')
        if soup.find('success'):
            return True
        else:
            return False

    # 从白名单删除IP
    def del_white_list(self, ip_add):
        s = requests.session()
        s.post(self.login_url, data=self.user_date)  # login
        data = {'param_submit_type': 'delete', 'param_address': ip_add, 'param_page': '0', 'param_this_sort': '1'}
        page = s.post(self.bw_list_url, data=data)
        soup = BeautifulSoup(page.content, 'html.parser')
        if soup.find('success'):
            return True
        else:
            return False

    # 查询域名白名单
    def query_domain_name(self, domain):
        s = requests.session()
        s.post(self.login_url, data=self.user_date)  # login
        data = {'param_submit_type': 'query', 'param_domain_name': domain, 'param_page': '0',
                'param_show_flags': 'blacklist+whitelist+collect'}
        page = s.post(self.domain_url, data=data)
        soup = BeautifulSoup(page.content, 'html.parser')
        name_list = list(soup.find_all('name'))
        for i in name_list:
            if domain == i.string:
                return True
        return False

    # 添加域名至白名单
    def add_domain_name(self, domain):
        if not self.query_domain_name(domain):
            s = requests.session()
            s.post(self.login_url, data=self.user_date)  # login
            data = {'param_submit_type': 'submit', 'param_domain_name': domain, 'param_page': '0',
                    'param_show_flags': 'blacklist+whitelist+collect'}
            page = s.post(self.domain_url, data=data)
            soup = BeautifulSoup(page.content, 'html.parser')
            if soup.find('success'):
                return True
            else:
                return False
        else:
            return True

    # 从白名单删除域名
    def del_domain_name(self, domain):
        s = requests.session()
        s.keep_alive = False
        s.post(self.login_url, data=self.user_date)  # login
        data = {'param_submit_type': 'delete', 'param_domain_name': domain, 'param_page': '0',
                'param_show_flags': 'blacklist+whitelist+collect'}
        page = s.post(self.domain_url, data=data)
        soup = BeautifulSoup(page.content, 'html.parser')
        if soup.find('success'):
            return True
        else:
            return False

    # 查询防火墙屏蔽列表
    def select_block_list(self, ip_add):
        s = requests.session()
        s.post(self.login_url, data=self.user_date)
        sel_ip = {'param_submit_type': 'select', 'param_filter': ip_add, 'param_this_sort': '-3'}
        page = s.post(self.fb_link_url, data=sel_ip)
        soup = BeautifulSoup(page.content, 'html.parser')
        fb_dict = {}
        tag_str = str(soup.find('page_title'))
        page_list = re.findall(r"\d+\.?\d*", tag_str[-25:])
        page_num = int(page_list[0])
        for num in range(0, page_num):
            new_page = s.post(self.fb_link_url, data={'param_submit_type': 'show', 'param_filter': ip_add,
                                                      'param_page': num, 'param_this_sort': '-3'})
            new_soup = BeautifulSoup(new_page.content, 'html.parser')
            la_list = new_soup.find_all('local_address')
            ra_list = new_soup.find_all('remote_address')
            rt_list = new_soup.find_all('release_time')
            for ra_tag in ra_list:
                fb_dict[la_list.pop(0).string + '-' + ra_tag.string] = rt_list.pop(0).string[10:-8]
        return fb_dict

    # 重置屏蔽列表
    def reset_block_list(self, ip_add, remote_ip):
        s = requests.session()
        s.post(self.login_url, data=self.user_date)
        reset_ip = {'param_submit_type': 'reset', 'param_filter': ip_add + '-' + remote_ip,
                    'param_this_sort': '1', 'links_element': 'on'}
        page = s.post(self.fb_link_url, data=reset_ip)
        soup = BeautifulSoup(page.content, 'html.parser')
        if soup.find('success'):
            return True
        else:
            return False

    # 查询主机状态集序号
    def query_protect_serial_number(self, ip_add):
        s = requests.session()
        s.keep_alive = False
        s.post(self.login_url, data=self.user_date)
        hostadd_url = self.url + 'cgi-bin/status_hostset.cgi?hostaddr=' + ip_add
        page = s.get(hostadd_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        pro_dict = {}
        try:
            pro_dict['param_set'] = soup.find('param_set').string
            pro_dict['filter_set'] = soup.find('filter_set').string
            pro_dict['PortTCP'] = soup.find('portpro_set_tcp').string
            pro_dict['PortUDP'] = soup.find('portpro_set_udp').string
        except AttributeError:
            pro_dict['set_collection'] = sc(code.IPNotExist).result % ip_add
        return pro_dict

    # 设置防护参数集
    def set_protect_serial_number(self, ip_add, param_set='', filter_set='', set_tcp='', set_udp=''):
        s = requests.session()
        s.post(self.login_url, data=self.user_date)
        ip_gateway = ip_add.split('.')
        ip_gateway[3] = '0'
        ip_gateway = '.'.join(ip_gateway)
        param_set_data = {'param_setting_addr': ip_add, 'param_prefix': '24', 'param_exist': 'ON',
                          'param_gateway_ip': ip_gateway, 'param_param_set': param_set, 'param_filter_set': filter_set,
                          'param_portpro_set_tcp': set_tcp, 'param_portpro_set_udp': set_udp,
                          'param_force_protect': 'ON'
                          }
        page = s.post(self.hostset_url, data=param_set_data)
        soup = BeautifulSoup(page.content, 'html.parser')
        if soup.find('success'):
            return True
        else:
            return False


if __name__ == '__main__':
    fire = Firewall('cc')
