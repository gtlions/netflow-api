#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hmac
import urllib.parse
from hashlib import sha1
import datetime
import requests
import base64


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
            "Timestamp": "2017-05-09T11:01:31Z",
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
        self.dev_url = 'http://antiddos.api-test.kaopuyun.com:8000'
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

    def DescribeNormalIPMaxData(self):
        parames = self.common_parames
        parames['Action'] = 'DescribeNormalIPMaxData'
        parames['IP'] = '45.126.122.174,45.126.122.175'
        parames['StartTime'] = "2017-11-20T03:00:00Z"
        parames['EndTime'] = "2017-12-05T03:05:10Z"
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

    def CreateProtectPackage(self):
        parames = self.common_parames
        parames['Action'] = 'CreateProtectPackage'
        parames['IPUserID'] = 'mosco'
        parames['GuaranteeProtectGroupID'] = 'antibgp_200g'
        parames['ElasticProtectGroupID'] = 'antibgp_300g'
        parames['SysPackageID'] = 'pkg_001'
        parames['PackageName'] = 'pkg_00312'
        parames['IPNums'] = 100
        parames['LifeDay'] = 100
        parames['BandwithType'] = 'AntiBGP'

        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text))

    def DescribeProtectPackage(self):
        parames = self.common_parames
        parames['Action'] = 'DescribeProtectPackage'
        # parames['IPUserID'] = 'mosco'
        parames['PackageID'] = '9d95a69a-c44b-11e7-a308-50e54919757f'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text))

    def AddProtectPackageIP(self):
        parames = self.common_parames
        parames['Action'] = 'AddProtectPackageIP'
        parames['PackageID'] = 'c115eb34-d98c-11e7-88de-50e54919757f'
        parames['IP'] = '10.2.2.2,10.2.2.3'
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

    def ModifyProtectPackage(self):
        parames = self.common_parames
        parames['Action'] = 'ModifyProtectPackage'
        parames['IPUserID'] = 'mosco'
        parames['PackageID'] = 'c115eb34-d98c-11e7-88de-50e54919757f'
        parames['GuaranteeProtectGroupID'] = 'antibgp_100g'
        parames['GuaranteeEnableTime'] = '2017-12-05T07:30:00Z'
        parames['ElasticProtectGroupID'] = 'antibgp_100g'
        parames['ElasticEnableTime'] = '2017-12-05T07:30:00Z'
        parames['IPNums'] = 30
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        print((parames['Action']))
        print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text))

    def DeleteProtectPackageIP(self):
        parames = self.common_parames
        parames['Action'] = 'DeleteProtectPackageIP'
        parames['PackageID'] = 'c115eb34-d98c-11e7-88de-50e54919757f'
        parames['IP'] = '10.2.2.3'
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

    def DeleteProtectPackage(self):
        parames = self.common_parames
        parames['Action'] = 'DeleteProtectPackage'
        parames['PackageID'] = '186de5b0-c437-11e7-8272-50e54919757f'
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

    def DescribeNormalIPMaxData(self):
        parames = self.common_parames
        parames['Action'] = 'DescribeNormalIPMaxData'
        parames['IP'] = ''
        parames['StartTime'] = "2017-10-30T03:00:00Z"
        parames['EndTime'] = "2017-10-30T03:05:10Z"
        parames['Region'] = 'cn-fuzhou-4'
        parames['Zone'] = 'cn-fuzhou-4-a'
        parames['BandwithType'] = 'AntiBGP'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)

        parames['Signature'] = self.sign_request(str_url_bgp)
        print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((requests.get(self.local_url + '/ip?' + urllib.parse.urlencode(parames)).text))
    def run(self):
        # self.DescribeNormalIPMaxData()
        # self.CreateProtectPackage()               # 32. 创建高防防护包列表
        # self.DescribeProtectPackage()             # 33. 查询防护包列表
        # self.AddProtectPackageIP()                # 34. 添加IP高防防护包列表
        # self.ModifyProtectPackage()               # 35. 修改高防防护包
        self.DeleteProtectPackageIP()             # 36. IP从高防防护包删除
        # self.DeleteProtectPackage()               # 37. 删除高防防护包
def runTest(ip, ackid, ackseckey):
    client = apitest(ip, ackid, ackseckey)
    client.run()
    # print((requests.get(
        # 'http://antiddos.api-test.kaopuyun.com:8000/ip?Action=DescribeIPMonitorData&EndTime=2017-10-30T21:03:00Z&SignatureNonce=cc58bb01-0144-4a90-928e-15f3014e52bc&Version=2&AccessKeyId=con1&IP=125.77.25.125,125.77.25.123,36.248.12.61,125.77.25.117,36.248.12.60&Signature=NyiztPSXoU4EZfrqGEDpBVMaHhQ=&StartTime=2017-10-30T21:00:00Z&Timestamp=2017-10-30T01:50:50Z')))
if __name__ == '__main__':
    client = apitest()
    client.run()