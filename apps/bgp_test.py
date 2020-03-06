#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hmac
import urllib.parse
from hashlib import sha1
import datetime
import requests
import base64


class apitest():
    def __init__(self):
        self.common_parames = {
            # "AccessKeyId": "dgkad1234iaqwfda",#cdn
            # "AccessKeyId": "hsefbawrfg",  #金山
            "AccessKeyId": "dev1",  # 开发账户1
            # "AccessKeyId": "dev2",  #开发账户2
            # "AccessKeyId": "con1",  # xx云开发账户
            # "AccessKeyId": "pan1",  # xx云开发账户
            # "AccessKeyId": "kpyglpt",  # xx云生产账户
            # "AccessKeyId": "afegxgu0VdR5fT7K",  # 系统
            # "AccessKeyId": "kpyxianxia",  # 线下
            "Timestamp": "2018-06-14T03:30:00Z",
            # "SignatureNonce": "686",
            "SignatureNonce": "614f56de-54e8-43b5-a00d-cef377881f2c",
            "Version": '2',
            "Action": '',
        }

        # self.AccessKeySecret = 'b2cd9c1319ea16ec3c5e1f3fee1432b3'  # 系统
        # self.AccessKeySecret = 'dqdert2354gd712itdgegdfgwew11'   #金山
        # self.AccessKeySecret = 'sadfgJUlkqsdfonsK'    # 生产环境
        self.AccessKeySecret = 'dev1gdfdihfcd9cdfh'  # 开发账户1
        # self.AccessKeySecret = 'pan1gd9cdfh'  # 开发账户1
        # self.AccessKeySecret = 'dev2gdfdihfcd9cdfh'   #开发账户2
        # self.AccessKeySecret = 'con1gd9cdfh'  # xx云开发账户
        # self.AccessKeySecret = 'fdl342kjdfsljqkaqpdfaldhkkfasl93'#cdn
        # self.AccessKeySecret = 'xiddfgJDansKdfAdf'  # 线下

        self.local_url = 'http://127.0.0.1:8000'
        self.dev_url = 'http://antiddos.api-test.youdomain.com'
        self.prod_url = 'http://antiddos.api.youdomain.com'

        # self.baseurl = 'https://api.youdomain.com' #cdn

    def sign_request(self, parame):
        hashed = hmac.new(self.AccessKeySecret.encode('utf-8'), parame.encode('utf-8'), digestmod=sha1)
        signature = base64.b64encode(hashed.digest())
        return signature

    # 特殊字符处理
    def res(self, par):
        #        par = par.decode('raw_unicode_escape').encode("utf-8")
        par = par.encode("utf-8")
        par = urllib.parse.quote(par)
        par = par.replace('+', '%20')
        par = par.replace('*', '%2A')
        par = par.replace('%7E', '~')
        par = par.replace('/', '%2F')
        return par

    def DescribeProtectGroup(self):
        parames = self.common_parames
        parames['Action'] = 'DescribeProtectGroup'
        parames['Region'] = 'cn-fuzhou-4'
        parames['Zone'] = 'cn-fuzhou-4-a'
        parames['BandwithType'] = 'AntiBGP'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def AddProtectGroupIP(self):
        parames = self.common_parames
        parames['Action'] = 'AddProtectGroupIP'
        parames['IP'] = '192.168.16.191'
        parames['IPUserID'] = 'da'
        parames['guaranteeProtectGroupID'] = 'antibgp_60g'
        parames['elasticProtectGroupID'] = 'antibgp_100g'
        parames['Region'] = 'cn-fuzhou-4'
        parames['Zone'] = 'cn-fuzhou-4-a'
        parames['BandwithType'] = 'AntiBGP'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DescribeIPInfo(self):
        parames = self.common_parames
        parames['Action'] = 'DescribeIPInfo'
        parames['IP'] = '10.1.1.88'
        # parames['IPUserID'] = 'da'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DescribeIPStatus(self):
        parames = self.common_parames
        parames['Action'] = 'DescribeIPStatus'
        parames['IP'] = '45.126.122.65'
        # parames['IPUserID'] = 'a'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def ModifyIPProtectGroup(self):
        parames = self.common_parames
        parames['Action'] = 'ModifyIPProtectGroup'
        parames['IP'] = '10.1.1.88'
        # parames['IPUserID'] = 'a'
        parames['GuaranteeProtectGroupID'] = 'antibgp_200g'
        parames['GuaranteeEnableTime'] = '2017-11-30T05:48:00Z'
        parames['ElasticProtectGroupID'] = 'antibgp_300g'
        parames['ElasticEnableTime'] = (
            datetime.datetime.now() - datetime.timedelta(hours=8) + datetime.timedelta(minutes=1)).strftime(
            '%Y-%m-%dT%H:%M:%SZ')
        parames['Region'] = 'cn-fuzhou-4'
        parames['Zone'] = 'cn-fuzhou-4-a'
        parames['BandwithType'] = 'AntiBGP'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def CloseIPElasticAntiDDos(self):
        parames = self.common_parames
        parames['Action'] = 'CloseIPElasticAntiDDos'
        parames['IP'] = '10.2.2.5'
        # parames['IPUserID'] = 'da'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def OpenIPElasticAntiDDos(self):
        parames = self.common_parames
        parames['Action'] = 'OpenIPElasticAntiDDos'
        parames['IP'] = '10.2.2.5'
        # parames['IPUserID'] = 'da'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def CloseIPAntiDDos(self):
        parames = self.common_parames
        parames['Action'] = 'CloseIPAntiDDos'
        parames['IP'] = '﻿10.10.10.1'
        # parames['IPUserID'] = 'da'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def OpenIPAntiDDos(self):
        parames = self.common_parames
        parames['Action'] = 'OpenIPAntiDDos'
        parames['IP'] = '100.100.100.100'
        # parames['IPUserID'] = 'da'
        parames['ElasticEnable'] = 'True'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DeleteProtectGroupIP(self):
        parames = self.common_parames
        parames['Action'] = 'DeleteProtectGroupIP'
        parames['IP'] = '11.28.9.8'
        # parames['IPUserID'] = 'da'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DescribeIPMonitorData(self):
        parames = self.common_parames
        parames['Action'] = 'DescribeIPMonitorData'
        # parames['IP'] = ',27.148.196.106,27.148.196.124,45.126.122.157,45.126.122.171,45.126.122.188,45.126.122.172,45.126.122.159,45.126.122.147,45.126.122.143,45.126.122.131,45.126.122.138,45.126.122.160,45.126.122.164,27.148.196.79,45.126.122.181'
        parames['IP'] = '125.77.24.24'
        parames['PackageID'] = '86761cca-6bc1-11e8-ab80-16167465338b'
        parames['IPUserID'] = '110849'
        parames['StartTime'] = "2018-06-14T03:20:00Z"
        parames['EndTime'] = "2018-06-14T03:30:00Z"
        parames['Region'] = 'cn-fuzhou-4'
        parames['Zone'] = 'cn-fuzhou-4-a'
        parames['BandwithType'] = 'AntiBGP'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((requests.get(self.dev_url + '/ip?' + urllib.parse.urlencode(parames)).text))

    def DescribeIPMaxMonitorData(self):
        parames = self.common_parames
        parames['Action'] = 'DescribeIPMaxMonitorData'
        parames['IP'] = '45.126.120.122'
        parames['IPUserID'] = 'da'
        parames['StartTime'] = "2017-10-31T05:51:00Z"
        parames['EndTime'] = "2017-10-31T05:54:00Z"
        parames['Region'] = 'cn-fuzhou-4'
        parames['Zone'] = 'cn-fuzhou-4-a'
        parames['BandwithType'] = 'AntiBGP'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DescribeIPLineMonitorData(self):
        parames = self.common_parames
        parames['Action'] = 'DescribeIPLineMonitorData'
        # parames['IP'] = '45.126.122.67,45.126.122.75,45.126.122.65,45.126.122.71,45.126.122.70,45.126.122.93,45.126.122.72,45.126.122.92,45.126.122.80,45.126.122.86'
        parames['IP'] = '45.126.120.122'
        # parames['IPUserID'] = 'da'
        parames['StartTime'] = "2017-09-27T03:04:00Z"
        parames['EndTime'] = "2017-10-31T00:10:00Z"
        parames['Region'] = 'cn-fuzhou-4'
        parames['Zone'] = 'cn-fuzhou-4-a'
        parames['BandwithType'] = 'AntiBGP'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def CreateIPFourLayerAntiConfig(self):
        parames = self.common_parames
        parames['Action'] = 'CreateIPFourLayerAntiConfig'
        # parames['IP'] = '27.148.196.94'
        parames['IP'] = '45.126.122.147'
        parames['BackIP'] = '192.168.16.192'
        # parames['Configs'] = self.res("[{'Protocol':'TCP','Port':'8128','SourceIP':'27.148.196.94:8000'}]")
        parames['Configs'] = self.res('[{"Port": "38", "Protocol": "TCP", "SourceIP": "3.3.3.3"}]')
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def UpdateIPFourLayerAntiConfig(self):
        parames = self.common_parames
        parames['Action'] = 'UpdateIPFourLayerAntiConfig'
        # parames['IP'] = '45.126.122.147'
        parames['IP'] = '27.148.196.94'
        parames['UUID'] = 'SLBFourLayer-849a7bae-bdf1-11e7-9f0a-10846e80fc6e'
        parames['Configs'] = self.res("[{'Protocol':'TCP','Port':'8002','SourceIP':'1.1.1.1'}]")
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DeleteIPFourLayerAntiConfig(self):
        parames = self.common_parames
        parames['Action'] = 'DeleteIPFourLayerAntiConfig'
        # parames['IP'] = '45.126.122.149'
        parames['IP'] = '27.148.196.94'
        parames['UUID'] = 'SLBFourLayer-849a7bae-bdf1-11e7-9f0a-10846e80fc6e'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def CreateIPSevenLayerAntiConfig(self):
        parames = self.common_parames
        parames['Action'] = 'CreateIPSevenLayerAntiConfig'
        parames['IP'] = '27.148.196.94'  # '27.148.158.136'
        parames['Configs'] = self.res(
            "[{'Type':'Site','Domain':'xiaohua.youdomain.com','Cname':'antiddos.api-test.youdomain.com','Protocol':'HTTP','Port':'80','SourceIPs':'10.1.1.1:800,10.1.1.99'}]")
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((requests.get(self.dev_url + '/ip?' + urllib.parse.urlencode(parames)).text))

    def UpdateIPSevenLayerAntiConfig(self):
        parames = self.common_parames
        parames['Action'] = 'UpdateIPSevenLayerAntiConfig'
        parames['IP'] = '27.148.196.94'
        parames['UUID'] = 'SLBSevenLayer-048ec746-331a-11e8-a935-16167465338b'
        parames['Configs'] = self.res(
            "[{'Type':'Site','Domain':'api-test.youdomain.com','Cname':'antiddos.api-test.youdomain.com','Protocol':'HTTP','Port':'80','SourceIPs':'1.2.3.4'}]")
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DeleteIPSevenLayerAntiConfig(self):
        parames = self.common_parames
        parames['Action'] = 'DeleteIPSevenLayerAntiConfig'
        parames['IP'] = '27.148.196.94'
        parames['UUID'] = 'SLBSevenLayer-048ec746-331a-11e8-a935-16167465338b'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((requests.get(self.dev_url + '/ip?' + urllib.parse.urlencode(parames)).text))

    def GetIPMetricInfo(self):
        parames = self.common_parames
        parames['Action'] = 'GetIPMetricInfo'
        parames['IP'] = '45.126.122.110'
        parames['StartTime'] = "2017-11-12T13:15:34Z"
        parames['EndTime'] = "2017-11-12T13:24:42Z"
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DescribeDomainFirewallList(self):
        parames = self.common_parames
        parames['Action'] = 'DescribeDomainFirewallList'
        parames['Hostname'] = 'test.com'
        # parames['Operator'] = 'ctc'
        parames['Operator'] = 'bgp'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DescribeIPFirewallList(self):
        parames = self.common_parames
        parames['Action'] = 'DescribeIPFirewallList'
        parames['Hostname'] = '10.10.10.3'
        parames['IPUserID'] = 'mosco'
        parames['Operator'] = 'bgp'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def AddDomainWhiteList(self):
        parames = self.common_parames
        parames['Action'] = 'AddDomainWhiteList'
        parames['IP'] = '10.1.1.188'
        # parames['PackageID'] = '76896cd8-bfa0-11e7-9142-000ec6c6d278'
        parames['Hostname'] = 'test.com'
        parames['IPUserID'] = 'mosco'
        parames['Operator'] = 'bgp'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def AddIPWhiteList(self):
        parames = self.common_parames
        parames['Action'] = 'AddIPWhiteList'
        parames['IP'] = '11.28.9.8'
        # parames['PackageID'] = 'e2460470-5ef3-11e8-8f3e-005056c00008'
        parames['Hostname'] = '10.10.19.66'
        parames['IPUserID'] = 'mosco'
        parames['Operator'] = 'bgp'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DeleteDomainWhiteList(self):
        parames = self.common_parames
        parames['Action'] = 'DeleteDomainWhiteList'
        parames['IP'] = '10.1.1.188'
        # parames['PackageID'] = '76896cd8-bfa0-11e7-9142-000ec6c6d278'
        parames['Hostname'] = 'test.com'
        parames['IPUserID'] = 'mosco'
        parames['Operator'] = 'bgp'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DeleteIPWhiteList(self):
        parames = self.common_parames
        parames['Action'] = 'DeleteIPWhiteList'
        # parames['IP'] = '45.126.120.122'
        parames['PackageID'] = '76896cd8-bfa0-11e7-9142-000ec6c6d278'
        parames['Hostname'] = '10.10.10.3'
        parames['IPUserID'] = 'mosco'
        parames['Operator'] = 'bgp'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DescribeBlockList(self):
        parames = self.common_parames
        parames['Action'] = 'DescribeBlockList'
        parames['SourceIP'] = '27.148.157.86'
        parames['Operator'] = 'bgp'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def ResetBlockIP(self):
        parames = self.common_parames
        parames['Action'] = 'ResetBlockIP'
        parames['SourceIP'] = '45.126.123.149'
        parames['RemoteIP'] = '186.150.202.131'
        parames['IPUserID'] = 'mosco'
        parames['Operator'] = 'bgp'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DescribeIPFirewallProtect(self):
        parames = self.common_parames
        parames['Action'] = 'DescribeIPFirewallProtect'
        parames['IP'] = '150.242.99.9'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def SetIPFirewallProtect(self):
        parames = self.common_parames
        parames['Action'] = 'SetIPFirewallProtect'
        parames['IP'] = '150.242.99.9'
        parames['IPUserID'] = 'da'
        parames['GlobalProtectLevel'] = '2'
        parames['WebProtectLevel'] = '2'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DescribeBlackHoleInfo(self):
        parames = self.common_parames
        parames['Action'] = 'DescribeBlackHoleInfo'
        parames['IP'] = '125.77.24.175,125.77.25.120'
        parames['StartTime'] = '2018-05-28T09:00:10Z'
        parames['EndTime'] = '2018-05-29T08:00:50Z'
        parames['IPUserID'] = '10005'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DescribeSysProtectPackage(self):
        parames = self.common_parames
        parames['Action'] = 'DescribeSysProtectPackage'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def CreateProtectPackage(self):
        parames = self.common_parames
        parames['Action'] = 'CreateProtectPackage'
        parames['IPUserID'] = 'mosco'
        parames['PackageName'] = 'pkg_00312'
        parames['GuaranteeProtectGroupID'] = 'antibgp_10g'
        parames['ElasticProtectGroupID'] = 'antibgp_100g'
        parames['BandwithType'] = 'AntiBGP'
        parames['IPNums'] = 26
        parames['LifeDay'] = 20
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DescribeProtectPackage(self):
        parames = self.common_parames
        parames['Action'] = 'DescribeProtectPackage'
        parames['IPUserID'] = 'mosco'
        # parames['PackageID'] = '8f0aa154-c9af-11e7-8aed-50e54919757f'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def AddProtectPackageIP(self):
        parames = self.common_parames
        parames['Action'] = 'AddProtectPackageIP'
        parames['PackageID'] = '855d723a-c9c6-11e7-96a6-50e54919757f'
        parames['IP'] = '10.1.1.74,10.1.1.75'
        parames['IPUserID'] = 'mosco'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def ModifyProtectPackage(self):
        parames = self.common_parames
        parames['Action'] = 'ModifyProtectPackage'
        parames['IPUserID'] = 'mosco'
        parames['GuaranteeProtectGroupID'] = 'antibgp_30g'
        parames['GuaranteeEnableTime'] = '2017-11-30T00:00:10Z'
        parames['ElasticProtectGroupID'] = 'antibgp_50g'
        parames['ElasticEnableTime'] = '2017-11-30T00:00:10Z'
        # parames['BandwithType'] = 'AntiBGP'
        parames['PackageID'] = '855d723a-c9c6-11e7-96a6-50e54919757f'
        # parames['IPNums'] = 80
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DeleteProtectPackageIP(self):
        parames = self.common_parames
        parames['Action'] = 'DeleteProtectPackageIP'
        parames['PackageID'] = '84375164-caab-11e7-b2d2-50e54919757f'
        parames['IP'] = '10.1.1.41'
        parames['IPUserID'] = 'mosco'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DeleteProtectPackage(self):
        parames = self.common_parames
        parames['Action'] = 'DeleteProtectPackage'
        parames['PackageID'] = 'e2460470-5ef3-11e8-8f3e-005056c00008'
        parames['IPUserID'] = 'mosco'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def ExtendProtectPackageDueTime(self):
        parames = self.common_parames
        parames['Action'] = 'ExtendProtectPackageDueTime'
        parames['PackageID'] = '855d723a-c9c6-11e7-96a6-50e54919757f'
        parames['LifeDay'] = 20
        parames['IPUserID'] = 'mosco'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def ClosePackageElasticAntiDDos(self):
        parames = self.common_parames
        parames['Action'] = 'ClosePackageElasticAntiDDos'
        parames['PackageID'] = '577e2768-ca74-11e7-8415-50e54919757f'
        parames['IPUserID'] = 'mosco'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def OpenPackageElasticAntiDDos(self):
        parames = self.common_parames
        parames['Action'] = 'OpenPackageElasticAntiDDos'
        parames['PackageID'] = '577e2768-ca74-11e7-8415-50e54919757f'
        parames['IPUserID'] = 'mosco'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DescribeNormalIPData(self):
        parames = self.common_parames
        parames['Action'] = 'DescribeNormalIPData'
        parames['IP'] = '125.77.30.197'
        parames['StartTime'] = "2017-12-20T05:00:00Z"
        parames['EndTime'] = "2018-01-20T06:00:00Z"
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DescribeUserFirewallWhiteList(self):
        parames = self.common_parames
        parames['Action'] = 'DescribeUserFirewallWhiteList'
        parames['IPUserID'] = 'mosco'
        # parames['PackageID'] = '39c4d5e0-dbb8-11e7-b73f-10846e80fc6e'
        # parames['IP'] = '45.126.120.122'
        # parames['Domain'] = False
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DescribeNormalIPBlackHoleInfo(self):
        parames = self.common_parames
        parames['Action'] = 'DescribeNormalIPBlackHoleInfo'
        parames['IP'] = '27.148.157.23,27.155.88.183'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def DescribeNormalIPMaxData(self):
        parames = self.common_parames
        parames['Action'] = 'DescribeNormalIPMaxData'
        parames['IP'] = '45.126.120.122'
        parames['StartTime'] = "2018-01-20T05:00:00Z"
        parames['EndTime'] = "2018-01-20T06:00:00Z"
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def InitAntiConfig(self):
        parames = self.common_parames
        parames['Action'] = 'InitAntiConfig'
        parames['IP'] = '192.168.16.191'
        parames['BackIP'] = '192.168.1.2'
        parames['Configs'] = self.res('[{"Port": "38", "Protocol": "TCP", "SourceIP": "3.3.3.3"}]')
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print(requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text)

    def run(self):
        # self.DescribeProtectGroup()               # 1.查看可用的防护组列表
        # self.AddProtectGroupIP()                  # 2.添加IP到指定的防护组*
        # self.DescribeIPInfo()                     # 3.获取IP的防护组信息
        # self.DescribeIPStatus()                   # 4.查看高防IP的状态
        # self.ModifyIPProtectGroup()               # 5.修改IP的防护组*
        # self.CloseIPElasticAntiDDos()             # 6.关闭IP的弹性流量服务*
        # self.OpenIPElasticAntiDDos()              # 7.开启IP的弹性流量服务*
        # self.CloseIPAntiDDos()                    # 8.关闭高防IP防护*
        # self.OpenIPAntiDDos()                     # 9.开启高防IP防护*
        # self.DescribeIPMonitorData()              # 11. 查看高防IP的带宽信息
        # self.DescribeIPMaxMonitorData()           # 12. 查看高防IP的带宽峰值
        # self.DescribeIPLineMonitorData()          # 19. 查看高防IP分线路的带宽信息
        # self.DeleteProtectGroupIP()               # 10.从指定防护组删除IP*
        # self.CreateIPFourLayerAntiConfig()        # 13. 创建高防IP四层防护配置
        # self.UpdateIPFourLayerAntiConfig()        # 14. 更新高防IP四层防护配置
        # self.DeleteIPFourLayerAntiConfig()        # 15. 删除高防IP四层防护配置
        # self.CreateIPSevenLayerAntiConfig()       # 16. 创建高防IP七层防护配置
        # self.UpdateIPSevenLayerAntiConfig()       # 17. 更新高防IP七层防护配置
        # self.DeleteIPSevenLayerAntiConfig()       # 18. 删除高防IP七层防护配置
        # self.GetIPMetricInfo()                    # 20. 获取高防IP预警信息
        # self.DescribeDomainFirewallList()         # 21. 查询防火墙域名白名单
        # self.DescribeIPFirewallList()             # 22. 查询防火墙IP白名单
        # self.AddDomainWhiteList()                 # 23. 添加防火墙域名白名单
        # self.AddIPWhiteList()                     # 24. 添加防火墙IP白名单
        # self.DeleteDomainWhiteList()              # 25. 删除防火墙域名白名单
        # self.DeleteIPWhiteList()                  # 26. 删除防火墙IP白名单
        # self.DescribeBlockList()                  # 27. 查询防火墙屏蔽列表
        # self.ResetBlockIP()                       # 28. 释放防火墙屏蔽IP
        # self.DescribeIPFirewallProtect()          # 29. 查询防火墙主机状态集序号
        # self.SetIPFirewallProtect()               # 30. 设置防火墙主机状态集序号
        # self.DescribeBlackHoleInfo()              # 31. 查询IP黑洞信息
        # self.CreateProtectPackage()               # 32. 创建高防防护包
        # self.DescribeProtectPackage()             # 33. 查询防护包信息
        # self.AddProtectPackageIP()                # 34. 添加IP到高防防护包
        # self.ModifyProtectPackage()               # 35. 修改高防防护包配置
        # self.DeleteProtectPackageIP()             # 36. 从高防防护包删除IP
        # self.DeleteProtectPackage()               # 37. 删除高防防护包
        # self.ExtendProtectPackageDueTime()        # 38. 延长高防防护包期限
        # self.ClosePackageElasticAntiDDos()        # 39. 关闭高防防护包弹性防护
        # self.OpenPackageElasticAntiDDos()         # 40. 关闭高防防护包弹性防护
        # self.DescribeNormalIPData()               # 41. 查看IP信息
        # self.DescribeUserFirewallWhiteList()      # 42. 查询用户名白名单记录
        # self.DescribeNormalIPBlackHoleInfo()      # 43. 查看普通IP黑洞信息
        # self.DescribeNormalIPMaxData()            # 44. 查看普通IP峰值信息与黑洞次数
        # self.InitAntiConfig()
        pass


if __name__ == '__main__':
    client = apitest()
    client.run()
    # print client.sign_request('GET&/cdn&AccessKeyId=dgkad1234iaqwfda&Action=CdnPreload&SignatureNonce=686&Timestamp=2017-03-31T11%3a01%3a31Z&Urls=%5b%22http%3a%2f%2ffileioscdn.37376.com%2fgao7ios.png%22%5d&Version=1')
