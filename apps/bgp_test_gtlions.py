#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hmac
import urllib.parse
from hashlib import sha1
import datetime
import requests
import base64


class apiText():
    def __init__(self, ip, ackid, ackseckey):
        self.ip=ip
        self.common_parames = {
            "AccessKeyId": ackid,
            "Timestamp": "2017-05-09T11:01:31Z",
            "SignatureNonce": "614f56de-54e8-43b5-a00d-cef377881f2c",
            "Version": '2',
            "Action": '',
        }

        self.AccessKeySecret = ackseckey
        self.local_url = 'http://127.0.0.1:8000'
        self.dev_url = 'http://antiddos.api-test.kaopuyun.com:8000'
        self.prod_url = 'http://antiddos.api.kaopuyun.com'

    def sign_request(self, parame):
        hashed = hmac.new(self.AccessKeySecret.encode('utf-8'), parame.encode('utf-8'), digestmod=sha1)
        signature = base64.b64encode(hashed.digest())
        return signature

    # 特殊字符处理
    def res(self, par):
        par = par.encode("utf-8")
        par = urllib.parse.quote(par)
        par = par.replace('+', '%20')
        par = par.replace('*', '%2A')
        par = par.replace('%7E', '~')
        par = par.replace('/', '%2F')
        return par

    def DescribeIPMonitorData(self):
        parames = self.common_parames
        parames['Action'] = 'DescribeIPMonitorData'
        parames['IP'] = self.ip
        parames['StartTime'] = "2017-10-30T03:00:00Z"
        parames['EndTime'] = "2017-10-30T03:05:10Z"
        parames['Region'] = 'cn-fuzhou-4'
        parames['Zone'] = 'cn-fuzhou-4-a'
        parames['BandwithType'] = 'AntiBGP'
        parame = sorted(list(parames.items()), key=lambda d: d[0])
        str_url_bgp = 'GET&/ip&' + urllib.parse.urlencode(parame)
        # print((parames['Action']))
        # print(str_url_bgp)
        parames['Signature'] = self.sign_request(str_url_bgp)
        # print((self.local_url + '/ip?' + urllib.parse.urlencode(parames)))
        # print((self.dev_url + '/ip?' + urllib.parse.urlencode(parames)))
        # print((self.prod_url + '/ip?' + urllib.parse.urlencode(parames)))
        print((requests.get(self.dev_url + '/ip?' + urllib.parse.urlencode(parames))))

    def run(self):
        self.DescribeIPMonitorData()

def runTest(ip, ackid, ackseckey):
    client = apiText(ip, ackid, ackseckey)
    client.run()
    # print((requests.get(
        # 'http://antiddos.api-test.kaopuyun.com:8000/ip?Action=DescribeIPMonitorData&EndTime=2017-10-30T21:03:00Z&SignatureNonce=cc58bb01-0144-4a90-928e-15f3014e52bc&Version=2&AccessKeyId=con1&IP=125.77.25.125,125.77.25.123,36.248.12.61,125.77.25.117,36.248.12.60&Signature=NyiztPSXoU4EZfrqGEDpBVMaHhQ=&StartTime=2017-10-30T21:00:00Z&Timestamp=2017-10-30T01:50:50Z')))
if __name__ == '__main__':
    import psycopg2
    import threading
    host = '45.126.120.122'
    port = '5432'
    user = 'api'
    password = '9sppAFAFQZOVR6zL'
    database = 'api'

    dns = "host=" + host + " port=" + str(
        port) + " dbname=" + database + " user=" + user + " password=" + password + " connect_timeout=3"
    conn = psycopg2.connect(dns)
    cur = conn.cursor()
    sql = 'select host(a.ip) ip,b.ackid,b.ackseckey from t_ip_protect a,t_users b where a.user_org=b.ackid and a.status=True'
    cur.execute(sql)
    data = cur.fetchall()
    threads=[]
    for i in data:
        ip = i[0]
        ackid = i[1]
        ackseckey = i[2]
        t=threading.Thread(target=runTest,args=(ip,ackid,ackseckey))
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()