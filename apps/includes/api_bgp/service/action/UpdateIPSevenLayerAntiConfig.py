#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, uuid
import re
import urllib.parse
import platform

from tornado import gen, netutil

from apps.common.remoteoper import RemoteOper
from apps.common.statusconfig import code, statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class UpdateIPSevenLayerAntiConfig(ActionBase):
    '''更新高防IP七层防护配置'''

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
        configs = urllib.parse.unquote(self.params['Configs'])
        self.application.logger.info(self.params['Configs'])
        self.application.logger.info(configs)
        if len(ip.split(',')) > 1:
            res = sc(code.ParamError)
            raise gen.Return(res)

        configs_dict = eval(configs)
        seven_layer_info = {}
        seven_layer_info['uuid'] = serialuuid
        seven_layer_info['ip'] = ip
        seven_layer_info['configtype'] = 'Mod'
        # parames['Configs'] = urllib.unquote(parames['Configs'])
        seven_layer_info['uts'] = ts

        for config in configs_dict:
            try:
                a_type = config['Type']
                domain = config['Domain']
                cname = config['Cname'] if 'Cname'in config else ''
                protocol = config['Protocol']
                port = config['Port']
                publickey = config['PublicKey'] if 'PublicKey'in config else ''
                privatekey = config['PrivateKey'] if 'PrivateKey'in config else ''
                sourceips = config['SourceIPs']
                seven_layer_info['types'] = a_type
                seven_layer_info['domains'] = domain
                seven_layer_info['cname'] = cname
                seven_layer_info['protocol'] = protocol
                seven_layer_info['port'] = port
                seven_layer_info['publickey'] = publickey
                seven_layer_info['privatekey'] = privatekey
                seven_layer_info['sourceips'] = sourceips
            except Exception as e:
                self.application.logger.info(e)
                res = sc(code.ParamError)
                res.result = res.result % config
                raise gen.Return(res)

            # check config
            if a_type not in ['Site', 'App']:
                res = sc(code.ParamError)
                res.result = res.result % protocol
                raise gen.Return(res)
            if protocol not in ['HTTP', 'HTTPS']:
                res = sc(code.ParamError)
                res.result = res.result % protocol
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
                self.application.logger.info(e)
                res = sc(code.ParamError)
                res.result = res.result % port
                raise gen.Return(res)
            sourceips_check = re.findall(r'\d+.\d+.\d+.\d+', str(sourceips.split(",")))
            for i in sourceips_check:
                if not netutil.is_valid_ip(i):
                    res = sc(code.ParamError)
                    res.result = res.result % sourceips
                    raise gen.Return(res)

            sql = "SELECT cfgfile FROM t_slb_seven_layer WHERE ip=%s AND uuid=%s"
            data = self.application.dbcur.queryone(sql, (ip, serialuuid,))
            if not data:
                res = sc(code.SLBConfNotExist)
                res.result = res.result % serialuuid
                raise gen.Return(res)
            old_cfgfile = data[0]
            old_cfgfile_apibak = old_cfgfile + '.apibak'
            if protocol == 'HTTP':
                nginx_conf_lines = 'upstream ' + domain + ' {\n'
                default_port = '80'
            else:
                nginx_conf_lines = 'upstream ' + domain + '_443 {\n'
                default_port = '443'
            try:
                for sourceip in sourceips.split(','):
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
                        sourceip = sourceip + ':' + default_port
                    nginx_conf_lines += '\tserver ' + sourceip + ';\n'
                nginx_conf_lines += '}\n'
            except Exception as e:
                res = sc(code.ParamError)
                res.result = res.result % sourceips
                raise gen.Return(res)
        data = self.application.dbcur.queryall_dict('select name,value,type,idx from t_sys_parameter')
        sys_parameter = {ret['name'] + ret['idx']: {ret['idx']: ret['value']} for ret in data}
        remoteser = RemoteOper(hostname=ip)
        res = remoteser.init_remote()
        if isinstance(res, sc):
            raise gen.Return(res)
        if platform.system() == 'Windows':
            with open('C:\Temp' + str(uuid.uuid1()) + str(ip) + str(port) + '.conf', 'w') as nginx_file:
                nginx_file.write(nginx_conf_lines)
        elif platform.system() == 'Linux':
            with open('/tmp/' + str(uuid.uuid1()) + str(ip) + str(port) + '.conf', 'w') as nginx_file:
                nginx_file.write(nginx_conf_lines)
        if protocol == 'HTTP':
            REMOTE_FILE = os.path.join(sys_parameter['SLBConfigWrokDir' + 'HTTP']['HTTP'], str(domain) + '.conf')
        else:
            REMOTE_FILE = os.path.join(sys_parameter['SLBConfigWrokDir' + 'HTTP']['HTTP'], str(domain) + '_443.conf')

        remoteser.file.rename(old_cfgfile, old_cfgfile_apibak)
        res = remoteser.put_file(nginx_file.name, REMOTE_FILE)
        os.remove(nginx_file.name) if os.path.isfile(nginx_file.name) else None
        if isinstance(res, sc):
            raise gen.Return(res)
        seven_layer_info['cfgfile'] = REMOTE_FILE
        # check nginx conf file
        stdin, stdout, stderr = remoteser.exec_cmd(
            sys_parameter['SLBNginxCMD' + 'HTTP']['HTTP'] + ' -t -c ' + sys_parameter['SLBConfigMainConfig' + 'HTTP'][
                'HTTP'])
        execret = stdout.readlines() + stderr.readlines()
        # with open('C:\Temp\seven.log', 'w') as seven:
        with open('/tmp/seven.log', 'w') as seven:
            seven.write(str(ts) + '\r\n')
            seven.write(str(stdin) + '\r\n')
            seven.write(str(nginx_file) + '\r\n')
            seven.write(str(execret) + '\r\n')
        remoteser.put_file(seven.name, '/logs/nginx/new_seven.log')
        remoteser.exec_cmd('cat /logs/nginx/new_seven.log >> /logs/nginx/seven.log')
        os.remove(seven.name) if os.path.isfile(seven.name) else None
        if not [x for x in execret if 'successful' in x]:
            res = sc(code.SLBConfCheckFaile)
            res.result = res.result % (str(execret) + ip)
            remoteser.file.remove(REMOTE_FILE)
            remoteser.file.rename(old_cfgfile_apibak, old_cfgfile)
            return res
        # https key files
        if protocol == 'HTTPS':
            httpspublickey = sys_parameter['HTTPSPublicKey' + 'Default']['Default']
            httpsprivatekey = sys_parameter['HTTPSPrivateKey' + 'Default']['Default']
            if publickey:
                if platform.system() == 'Windows':
                    with open('C:\Temp' + str(uuid.uuid1()) + str(ip) + str(port) + '.conf', 'w') as httpspublickeyfile:
                        httpspublickeyfile.write(publickey)
                elif platform.system() == 'Linux':
                    with open('/tmp/' + str(uuid.uuid1()) + str(ip) + str(port) + '.conf', 'w') as httpspublickeyfile:
                        httpspublickeyfile.write(publickey)
                res = remoteser.put_file(httpspublickeyfile.name, httpspublickey)
                os.remove(httpspublickeyfile.name) if os.path.isfile(httpspublickeyfile.name) else None
                if isinstance(res, sc):
                    raise gen.Return(res)
            if privatekey:
                if platform.system() == 'Windows':
                    with open('C:\Temp' + str(uuid.uuid1()) + str(ip) + str(port) + '.conf', 'w') as httpsprivatekeyfile:
                        httpsprivatekeyfile.write(privatekey)
                elif platform.system() == 'Linux':
                    with open('/tmp/' + str(uuid.uuid1()) + str(ip) + str(port) + '.conf', 'w') as httpsprivatekeyfile:
                        httpsprivatekeyfile.write(privatekey)
                res = remoteser.put_file(httpsprivatekeyfile.name, httpsprivatekey)
                os.remove(httpsprivatekeyfile.name) if os.path.isfile(httpsprivatekeyfile.name) else None
                if isinstance(res, sc):
                    raise gen.Return(res)
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

        remoteser.file.remove(old_cfgfile_apibak)
        self.application.dbcur.update_dict('t_slb_seven_layer', seven_layer_info, 'uuid', serialuuid)
        res = sc(code.Success)
        res.result = 'Success'
        raise gen.Return(res)
