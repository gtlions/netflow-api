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
            # "AccessKeyId": "con1",  # 靠谱云开发账户
            # "AccessKeyId": "kpyglpt",  # 靠谱云生产账户
            # "AccessKeyId": "afegxgu0VdR5fT7K",  # 系统
            # "AccessKeyId": "kpyxianxia",  # 线下
            "Timestamp": "2017-11-09T11:01:31Z",
            # "SignatureNonce": "686",
            "SignatureNonce": "614f56de-54e8-43b5-a00d-cef377881f2c",
            "Version": '2',
            "Action": '',
        }

        # self.AccessKeySecret = 'b2cd9c1319ea16ec3c5e1f3fee1432b3'  # 系统
        # self.AccessKeySecret = 'dqdert2354gd712itdgegdfgwew11'   #金山
        # self.AccessKeySecret = 'sadfgJUlkqsdfonsK'    # 生产环境
        self.AccessKeySecret = 'dev1gdfdihfcd9cdfh'  # 开发账户1
        # self.AccessKeySecret = 'dev2gdfdihfcd9cdfh'   #开发账户2
        # self.AccessKeySecret = 'con1gd9cdfh'  # 靠谱云开发账户
        # self.AccessKeySecret = 'fdl342kjdfsljqkaqpdfaldhkkfasl93'#cdn
        # self.AccessKeySecret = 'xiddfgJDansKdfAdf'  # 线下

        self.local_url = 'http://127.0.0.1:8000'
        self.dev_url = 'http://antiddos.api-test.kaopuyun.com'
        self.prod_url = 'http://antiddos.api.kaopuyun.com'

        # self.baseurl = 'https://api.kaopuyun.com' #cdn

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
        print((requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text))

    def AddIPWhiteList(self):
        parames = self.common_parames
        parames['Action'] = 'AddIPWhiteList'
        # parames['IP'] = '27.148.196.1'
        parames['PackageID'] = 'a19cb3f6-5e36-11e8-bf0e-a3798c6d2281'
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
        print((requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text))

    def DeleteProtectPackage(self):
        parames = self.common_parames
        parames['Action'] = 'DeleteProtectPackage'
        parames['PackageID'] = 'a19cb3f6-5e36-11e8-bf0e-a3798c6d2281'
        parames['IPUserID'] = 'mosco'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text))

    def run(self):
        # self.CreateProtectPackage()               # 32. 创建高防防护包
        # self.AddIPWhiteList()                     # 24. 添加防火墙IP白名单
        self.DeleteProtectPackage()
        pass


if __name__ == '__main__':
    client = apitest()
    client.run()
