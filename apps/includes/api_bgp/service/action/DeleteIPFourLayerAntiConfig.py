#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import ipaddress
from apps.common.remoteoper import RemoteOper
from tornado import gen
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase
# @Author: Gtlions Lai


class DeleteIPFourLayerAntiConfig(ActionBase):
    '''删除高防IP四层防护配置'''

    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        #self.application.logger.info(self.init_msg)

    @gen.coroutine
    def run(self):
        res = sc(code.Success)
        res.result = 'Success'
        action = self.params['Action']
        ts = self.application.ts_begin
        ip = self.params['IP']
        serialuuid = self.params['UUID']
        accesskeyid = self.params['AccessKeyId']
        if len(ip.split(',')) > 1:
            res = sc(code.ParamError)
            raise gen.Return(res)
        try:
            ipaddress.ip_address(ip)
        except:
            res = sc(code.ParamError)
            raise gen.Return(res)

        sql = "SELECT cfgfile from t_slb_four_layer where ip=%s and uuid=%s and configtype !='Del'"
        data = self.application.dbcur.queryone(sql, (ip, serialuuid,))
        if not data:
            res = sc(code.SLBConfNotExist)
            res.result = res.result % serialuuid
            raise gen.Return(res)
        old_cfgfile = data[0]
        data = self.application.dbcur.queryall_dict('select name,value,type,idx from t_sys_parameter')
        sys_parameter = {ret['name'] + ret['idx']: {ret['idx']: ret['value']} for ret in data}
        remoteser = RemoteOper(hostname=ip)
        res = remoteser.init_remote()
        if isinstance(res, sc):
            raise gen.Return(res)
        remoteser.file.remove(old_cfgfile)
        # restart|reload nginx
        stdin, stdout, stderr = remoteser.exec_cmd(sys_parameter['SLBNginxRESTART' + 'TCP']['TCP'])
        execret = stdout.readlines() + stderr.readlines()
        # with open('C:\Temp/new_four.log', 'w') as four:
        with open('/tmp/new_four.log', 'w') as four:
            four.write(str(ts) + '\r\n')
            four.write(str(stdin) + '\r\n')
            four.write(str(execret) + '\r\n')
        remoteser.put_file(four.name, '/logs/nginx/new_four.log')
        remoteser.exec_cmd('cat /logs/nginx/new_four.log >> /logs/nginx/four.log')
        os.remove(four.name) if os.path.isfile(four.name) else None

        # if execret:
        #     res = sc(code.RemoteSerExecCMDErr)
        #     res.result = res.result % (str(execret) + ip)
        #     return res
        sql = "UPDATE t_slb_four_layer SET configtype='Del' where ip=%s and uuid=%s"
        self.application.dbcur.execute(sql, (ip, serialuuid,))
        res = sc(code.Success)
        res.result = 'Success'
        raise gen.Return(res)
