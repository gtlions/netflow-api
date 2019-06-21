#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import paramiko
from apps.common.postgresqldb import PostgreSQLDB
from apps.common.statusconfig import statusconfig as sc, code
from apps.API_BGP.config.config import CONFIG


class RemoteOper():
    def __init__(self, hostname, port=None, username=None, password=None, private_key=None, timeout=3,
                 auth_timeout=3):
        db_conn = PostgreSQLDB(CONFIG.DB.host, CONFIG.DB.port, CONFIG.DB.user, CONFIG.DB.pwd, CONFIG.DB.dbname)
        data = db_conn.dbcur.queryall_dict('select name,value,type,idx from t_sys_parameter')
        sys_parameter = {ret['name'] + ret['idx']: {ret['idx']: ret['value']} for ret in data}
        self.hostname = hostname
        if not port:
            self.port = int(sys_parameter['RemoteServerPort' + 'Default']['Default'])
        else:
            self.port = port
        if not username:
            self.username = sys_parameter['RemoteServerUserName' + 'Default']['Default']
        else:
            self.username = username
        self.password = password
        if not private_key:
            for keyfile in sys_parameter['RemoteServerLoginKey' + 'Private']['Private'].split(','):
                keyfile = keyfile.replace('{$HOME}', os.path.expanduser('~'))
                if os.path.isfile(keyfile):
                    self.private_key = keyfile
        else:
            self.private_key = private_key
        self.timeout = timeout
        self.auth_timeout = auth_timeout

    def init_remote(self):
        self.shell = paramiko.SSHClient()
        self.shell.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        PRIVATE_KEY = paramiko.RSAKey.from_private_key_file(self.private_key)
        try:
            self.shell.connect(hostname=self.hostname, port=self.port, username=self.username, password=self.password,
                               pkey=PRIVATE_KEY, timeout=self.timeout)
            self.sftpcon = paramiko.Transport((self.hostname, self.port))
            self.sftpcon.connect(username=self.username, password=self.password, pkey=PRIVATE_KEY)
            self.file = paramiko.SFTPClient.from_transport(self.sftpcon)
        except Exception as e:
            if type(e).__name__ == 'timeout':
                res = sc(code.RemoteSerConnTimeout)
                res.result = res.result % self.hostname
                return res
            if type(e).__name__ == 'AuthenticationException':
                res = sc(code.RemoteSerAuthFaile)
                res.result = res.result % self.hostname
                return res
            res = sc(code.RemoteSerConnFaile)
            res.result = res.result % self.hostname
            return res
        return True

    def exec_cmd(self, cmd):
        std_in, std_out, std_err = self.shell.exec_command(cmd, timeout=self.timeout)
        return std_in, std_out, std_err

    def put_file(self, local, remote):
        try:
            self.file.put(local, remote)
        except Exception as e:
            if type(e).__name__ == 'IOError':
                res = sc(code.RemoteSerIOErr)
                res.result = res.result % (str(e) + ':[' + local + remote + '] ' + self.hostname)
                return res
        return True

    def remove_file(self, remote):
        try:
            self.file.remove(remote)
        except Exception as e:
            if type(e).__name__ == 'IOError':
                res = sc(code.RemoteSerIOErr)
                res.result = res.result % (str(e) + ':[' + remote + '] ' + self.hostname)
                return res
        return True

    def __del__(self):
        try:
            self.shell.close()
            self.sftpcon.close()
        except Exception as e:
            pass


if __name__ == "__main__":
    hostname = '27.148.196.94'
    port = 22
    username = 'root'
    # PUBLIC_KEY = '/Users/gtlions/.ssh/id_rsa.pubnew'
    # PRIVATE_KEY = '/Users/gtlions/.ssh/id_rsanew'
    cp = RemoteOper(hostname=hostname, port=port)
    cp.init_remote()
    # cp.shell.exec_command('ls /')
