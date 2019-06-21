#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Gtlions Lai

import os, uuid
import re
import ipaddress
import platform
from apps.common.remoteoper import RemoteOper
import urllib.request, urllib.parse, urllib.error
from tornado import gen
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class UpdateIPFourLayerAntiConfig(ActionBase):
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
        configs = urllib.parse.unquote(self.params['Configs'])
        self.application.logger.info(self.params['Configs'])
        self.application.logger.info(configs)
        if len(ip.split(',')) > 1:
            res = sc(code.ParamError)
            raise gen.Return(res)
        try:
            ipaddress.ip_address(ip)
        except:
            res = sc(code.ParamError)
            raise gen.Return(res)

        configs_dict = eval(configs)
        if len(configs_dict) != 1:
            res = sc(code.SLBConfTcpNoSingle)
            raise gen.Return(res)
        four_layer_info = {}
        four_layer_info['uuid'] = serialuuid
        four_layer_info['ip'] = ip
        four_layer_info['configtype'] = 'Mod'
        # parames['Configs'] = urllib.unquote(parames['Configs'])
        four_layer_info['uts'] = ts
        data = self.application.dbcur.queryall_dict('select name,value,type,idx from t_sys_parameter')
        sys_parameter = {ret['name'] + ret['idx']: {ret['idx']: ret['value']} for ret in data}
        remoteser = RemoteOper(hostname=ip)
        remoteser.init_remote()

        for config in configs_dict:
            try:
                port = config['Port']
                protocol = config['Protocol']
                sourceip = config['SourceIP']
                four_layer_info['port'] = port
                four_layer_info['protocol'] = protocol
                four_layer_info['sourceip'] = sourceip
            except Exception as e:
                self.application.logger.info(e)
                res = sc(code.ParamError)
                res.result = res.result % config
                raise gen.Return(res)

            stdin, stdout, stderr = remoteser.exec_cmd('ls ' + sys_parameter['SLBConfigWrokDir' + 'TCP']['TCP'])
            file_exist = stdout.readlines()
            if protocol not in ['TCP']:
                res = sc(code.ParamError)
                res.result = res.result % protocol
                raise gen.Return(res)

            for i in file_exist:
                if port in i:
                    stdin, stdout, stderr = remoteser.exec_cmd('cat ' + sys_parameter['SLBConfigWrokDir' + 'TCP']['TCP'] + port + '.conf')
                    get_oldip = stdout.readlines()
                    if ip in get_oldip:
                        res = sc(code.SLBConfDuplicate)
                        res.result = res.result % (ip + ':' + port)
                        raise gen.Return(res)

            try:
                int(port)
                if not re.match('^\d{1,5}$', port):
                    res = sc(code.ParamError)
                    res.result = res.result % port
                    raise gen.Return(res)
                if int(port) < 0 or int(port) > 65536:
                    res = sc(code.ParamError)
                    res.result = res.result % port
                    raise gen.Return(res)
            except Exception as e:
                res = sc(code.ParamError)
                res.result = res.result % port
                raise gen.Return(res)

            try:
                if re.findall(':', sourceip):
                    sourceip_ip, sourceip_port = sourceip.split(':')
                    int(sourceip_port)
                    if not re.match('^\d{1,5}$', sourceip_port):
                        res = sc(code.ParamError)
                        res.result = res.result % sourceip_port
                        raise gen.Return(res)
                    if int(sourceip_port) < 0 or int(sourceip_port) > 65536:
                        res = sc(code.ParamError)
                        res.result = res.result % sourceip_port
                        raise gen.Return(res)
                else:
                    sourceip += ':' + port
            except Exception as e:
                res = sc(code.ParamError)
                res.result = res.result % sourceip
                raise gen.Return(res)
            sql = 'SELECT cfgfile from t_slb_four_layer where ip=%s and uuid=%s'
            data = self.application.dbcur.queryone(sql, (ip, serialuuid,))
            if not data:
                res = sc(code.SLBConfNotExist)
                res.result = res.result % serialuuid
                raise gen.Return(res)
            old_cfgfile = data[0]
            old_cfgfile_apibak = old_cfgfile + '.apibak'
            nginx_conf_lines = 'upstream tcp_' + port + ' {\n'
            nginx_conf_lines += '\tserver ' + sourceip + ';\n'
            nginx_conf_lines += '}\n'
            nginx_conf_lines += 'server {\n'
            nginx_conf_lines += '\tlisten ' + port + ';\n'
            nginx_conf_lines += '\tproxy_pass tcp_' + port + ';\n'
            nginx_conf_lines += '}\n'

        res = remoteser.init_remote()
        if isinstance(res, sc):
            raise gen.Return(res)
        if platform.system() == 'Windows':
            with open('C:\Temp' + str(uuid.uuid1()) + str(ip) + str(port) + '.conf', 'w') as nginx_file:
                nginx_file.write(nginx_conf_lines)
        elif platform.system() == 'Linux':
            with open('/tmp/' + str(uuid.uuid1()) + str(ip) + str(port) + '.conf', 'w') as nginx_file:
                nginx_file.write(nginx_conf_lines)
        REMOTE_FILE = os.path.join(sys_parameter['SLBConfigWrokDir' + 'TCP']['TCP'], str(port) + '.conf')
        remoteser.file.rename(old_cfgfile, old_cfgfile_apibak)
        res = remoteser.put_file(nginx_file.name, REMOTE_FILE)
        os.remove(nginx_file.name) if os.path.isfile(nginx_file.name) else None
        if isinstance(res, sc):
            raise gen.Return(res)
        four_layer_info['cfgfile'] = REMOTE_FILE
        # check nginx conf file
        stdin, stdout, stderr = remoteser.exec_cmd(
            sys_parameter['SLBNginxCMD' + 'TCP']['TCP'] + ' -t -c ' + sys_parameter['SLBConfigMainConfig' + 'TCP']['TCP'])
        execret = stdout.readlines() + stderr.readlines()
        with open('/tmp/new_four.log', 'w') as four:
            four.write(str(ts) + '\r\n')
            four.write(str(stdin) + '\r\n')
            four.write(str(nginx_conf_lines) + '\r\n')
            four.write(str(execret) + '\r\n')
        remoteser.put_file(four.name, '/logs/tcp_nginx/new_four.log')
        remoteser.exec_cmd('cat /logs/tcp_nginx/new_seven.log >> /logs/tcp_nginx/four.log')
        os.remove(four.name) if os.path.isfile(four.name) else None
        if not [x for x in execret if 'successful' in x]:
            res = sc(code.SLBConfCheckFaile)
            res.result = res.result % (str(execret) + ip)
            remoteser.file.remove(REMOTE_FILE)
            remoteser.file.rename(old_cfgfile_apibak, old_cfgfile)
            return res
        # restart|reload nginx
        stdin, stdout, stderr = remoteser.exec_cmd(sys_parameter['SLBNginxRESTART' + 'TCP']['TCP'])
        execret = stdout.readlines() + stderr.readlines()
        with open('/tmp/new_four.log', 'w') as four:
            four.write(str(ts) + '\r\n')
            four.write(str(stdin) + '\r\n')
            four.write(str(execret) + '\r\n')
        remoteser.put_file(four.name, '/logs/tcp_nginx/new_four.log')
        remoteser.exec_cmd('cat /logs/tcp_nginx/new_four.log >> /logs/tcp_nginx/four.log')
        os.remove(four.name) if os.path.isfile(four.name) else None
        # if execret:
        #     res = sc(code.RemoteSerExecCMDErr)
        #     res.result = res.result % (str(execret) + ip)
        #     return res
        remoteser.file.remove(old_cfgfile_apibak)
        self.application.dbcur.update_dict('t_slb_four_layer', four_layer_info, 'uuid', serialuuid)
        res = sc(code.Success)
        res.result = 'Success'
        raise gen.Return(res)
