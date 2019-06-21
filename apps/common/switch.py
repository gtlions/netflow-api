#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Gtlions Lai

import time
import paramiko
import telnetlib


def ssh_cisco(hostip, port, username, password):
    myclient = paramiko.SSHClient()
    myclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    myclient.connect(hostip, port=port, username=username, password=password, look_for_keys=False)
    chan = myclient.invoke_shell()
    time.sleep(0.1)
    chan.send('en\n')
    time.sleep(0.1)
    chan.send('conf t\n')
    time.sleep(0.1)
    chan.send('no ip routing\n')
    chan.send('int e1/0\n')
    time.sleep(0.1)
    chan.send('ip add 192.168.250.250 255.255.255.0\n')
    time.sleep(0.1)
    chan.send('do show run\n')
    time.sleep(0.5)
    output = chan.recv(65535)
    print(output)


def telnet_cisco(hostip, username, password, finish):
    tn = telnetlib.Telnet(hostip, timeout=5)
    tn.read_until('Username:')
    tn.write(username + '\n')
    tn.read_until('Password:')
    tn.write(password + '\n')
    tn.read_until('>')
    tn.write('en\n')
    tn.read_until(finish)
    tn.write('conf t\n')
    tn.read_until(finish)
    tn.write('int F1/0\n')
    tn.read_until(finish)
    tn.write('ip add 192.168.1.251 255.255.255.0\n')
    tn.read_until(finish)
    tn.write('no shutdown\n')
    tn.read_until(finish)
    tn.write('do show run\n')
    tn.close()


def ssh_huawei(hostip, port, username, password):
    myclient = paramiko.SSHClient()
    myclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    myclient.connect(hostip, port=port, username=username, password=password, look_for_keys=False)
    chan = myclient.invoke_shell()
    time.sleep(0.1)
    chan.send('sys\n')
    time.sleep(0.1)
    chan.send('vlan 7\n')
    chan.send('quit\n')
    chan.send('interface Vlanif 7\n')
    time.sleep(0.1)
    chan.send('ip add 192.168.250.250 255.255.255.0\n')
    time.sleep(0.1)
    chan.send('quit\n')
    chan.send('dis cu\n')
    time.sleep(0.5)
    output = chan.recv(65535)
    print(output)


def telnet_huawei(hostip, username, password, finish):
    tn = telnetlib.Telnet(hostip, timeout=5)
    tn.read_until('Username:')
    tn.write(username + '\n')
    tn.read_until('Password:')
    tn.write(password + '\n')
    tn.read_until('>')
    tn.write('sys\n')
    tn.read_until(finish)
    tn.write('vlan 10\n')
    tn.read_until(finish)
    tn.write('quit\n')
    tn.read_until(finish)
    tn.write('interface Vlanif 10 \n')
    tn.read_until(finish)
    tn.write('ip address 192.168.2.251 255.255.255.0\n')
    tn.read_until(finish)
    tn.write('quit\n')
    tn.read_until(finish)
    tn.write('dis cu\n')
    tn.close()

if __name__ == '__main__':
    # telnet_cisco('10.1.1.1', 'admin', 'cisco', '#')
    # ssh_cisco('10.1.1.1', 22, 'admin', 'cisco', 'cisco')
    # telnet_huawei('192.168.56.10', 'admin', 'cisco', ']')
    ssh_huawei('192.168.56.10', 22, 'admin', 'cisco')
