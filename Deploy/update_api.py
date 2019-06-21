#! python2
# -*- coding:utf-8 -*-
# @Author: Gtlions Lai

import os
import sys
import time
import tarfile
from gittle import Gittle
import xmlrpclib
server = xmlrpclib.Server('http://user:Fh6XNs@36.248.12.89:9001/RPC2')


def process_control(process, action):
    # get process current state
    process_state = server.supervisor.getProcessInfo(process)['state']
    # start process
    if action == 'start':
        if process_state == 0 or process_state == 40:
            server.supervisor.startProcess(process, True)
            print('%s has been started' % process)
        elif process_state == 100 or process_state == 1000:
            # supervisor programming error,restart supervisor
            server.supervisor.restart()
            print('supervisor programming error,restart supervisor')
        elif process_state == 200:
            # process could not be started successfully
            print('%s has some problem,please check it.' % process)
        else:
            print("%s error,(not stopped)" % process)
    # stop process
    if action == 'stop':
        if process_state == 10 or process_state == 20 or process_state == 30:
            server.supervisor.stopProcess(process, True)
            print('%s has been stopped' % process)
        else:
            print("%s error,(not running)" % process)
    # restart process
    if action == 'restart':
        if process_state == 0 or process_state == 40:
            print('%s error(not running)' % process)
            server.supervisor.startProcess(process, True)
            print('%s has been restarted' % process)
        else:
            server.supervisor.stopProcess(process, True)
            server.supervisor.startProcess(process, True)
            print('%s has been restarted' % process)


def make_targz(output_filename, source_dir):
    # only package，change "w:gz" to "w:" or "w".
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir)    # arcname=os.path.basename(source_dir)


def process_update(process):
    process_control(process, 'stop')    # stop process
    if process == 'bgpapi_8108':
        filename = 'bgpapi_' + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + '.tar.gz'
        path = '/home/API/bgpapi'
        mv_path = '/home/API/backup'
        make_targz('/home/API/' + filename, path)  # backup
        os.system('mv %s %s' % ('/home/API/' + filename, mv_path))
        os.system("rm -rf %s" % path)  # delete
        repo_url = 'git@mgrser:root/bgpapi.git'
        Gittle.clone(repo_url, path)  # git clone
        repo = Gittle(path, origin_uri='git@mgrser:root/bgpapi.git')
        repo.switch_branch('master')
        repo.pull()
    elif process == 'bgpapi_8109':
        path = '/home/API/bgpapi_ha'
        os.system("rm -rf %s" % path)  # delete
        repo_url = 'git@mgrser:root/bgpapi.git'
        Gittle.clone(repo_url, path)  # git clone
        repo = Gittle(path, origin_uri='git@mgrser:root/bgpapi.git')
        repo.switch_branch('master')
        repo.pull()
    else:
        print('You cannot do with this %s' % process)
    process_control(process, 'start')  # start process
    print('%s has been updated.' % process)


if __name__ == '__main__':
    process_update('bgpapi_8108')
    process_update('bgpapi_8109')
