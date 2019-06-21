#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Gtlions Lai

import os

from tornado import gen

from apps.common.remoteoper import RemoteOper
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class DeleteIPSevenLayerAntiConfig(ActionBase):
    '''删除高防IP七层防护配置'''

    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        #self.application.logger.info(self.init_msg)

    @gen.coroutine
    def run(self):
        ts = self.application.ts_begin
        ip = self.params['IP']
        serialuuid = self.params['UUID']
        user_org = self.params['AccessKeyId']
        user_end = self.params['IPUserID'] if 'IPUserID' in self.params else None
        if len(ip.split(',')) > 1:
            res = sc(code.ParamError)
            raise gen.Return(res)

        sql = "SELECT cfgfile FROM t_slb_seven_layer WHERE ip=%s AND uuid=%s and configtype !='Del'"
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
        stdin, stdout, stderr = remoteser.exec_cmd(sys_parameter['SLBNginxRESTART' + 'HTTP']['HTTP'])
        execret = stdout.readlines() + stderr.readlines()
        # with open('C:\Temp\seven.log', 'w') as seven:
        with open('/tmp/new_seven.log', 'w') as seven:
            seven.write(str(ts) + '\r\n')
            seven.write(str(stdin) + '\r\n')
            seven.write(str(execret) + '\r\n')
        remoteser.put_file(seven.name, '/logs/nginx/new_seven.log')
        remoteser.exec_cmd('cat /logs/nginx/new_seven.log >> /logs/nginx/seven.log')
        os.remove(seven.name) if os.path.isfile(seven.name) else None
        self.application.dbcur.execute("UPDATE t_slb_seven_layer SET configtype='Del' where ip=%s and uuid=%s", (ip, serialuuid,))
        res = sc(code.Success)
        res.result = 'Success'
        raise gen.Return(res)
