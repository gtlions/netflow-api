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


if __name__ == '__main__':
    process_control('bgpapi_8108', 'restart')
    process_control('bgpapi_8109', 'restart')
