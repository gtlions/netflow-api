#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Gtlions Lai


from tornado import gen
from apps.common.zx_firewall import Firewall
from apps.common.statusconfig import code
from apps.common.statusconfig import statusconfig as sc
from apps.includes.api_bgp.service.actionbase.action_base import ActionBase


class SetIPFirewallProtect(ActionBase):
    '''设置防火墙防护策略'''

    def __init__(self, params=None, application=None, *args, **kwargs):
        ActionBase.__init__(self)
        self.params = params
        self.application = application
        # self.application.logger.info(self.init_msg)

    @gen.coroutine
    def run(self):
        ip = self.params['IP']
        # ip = '45.126.122.111'
        user_org = self.params['AccessKeyId']
        user_end = self.params['IPUserID'] if 'IPUserID' in self.params else None
        ps_level = self.params['GlobalProtectLevel'] if 'GlobalProtectLevel' in self.params else None
        pt_level = self.params['WebProtectLevel'] if 'WebProtectLevel' in self.params else None

        sql = "SELECT user_end FROM t_ip_protect WHERE user_org=%s AND ip=%s AND status=TRUE;"
        userid_list = self.application.dbcur.queryall_dict(sql, (user_org, ip,))
        userid = userid_list[0]['user_end']
        if len(userid_list) == 0:
            res = sc(code.NotInCorrectStatus)
            res.result = res.result % ip

        firewall = Firewall(self.application.ccfirewall)
        if ps_level is None:
            protect_dict = firewall.query_protect_serial_number(ip)
            ps_level = protect_dict['param_set']
        else:
            try:
                ps_level_int = int(ps_level)
            except ValueError:
                res = sc(code.ProetctLevelNotExist)
                res.result = res.result % ps_level
                raise gen.Return(res)
            if ps_level_int < 0 or ps_level_int > 2:
                res = sc(code.ProetctLevelNotExist)
                res.result = res.result % ps_level_int
                raise gen.Return(res)
            v = list(self.application.param_set_dict.values())
            k = list(self.application.param_set_dict.keys())
            ps_level = k[v.index(ps_level)]
        if pt_level is None:
            protect_dict = firewall.query_protect_serial_number(ip)
            pt_level = protect_dict['PortTCP']
        else:
            try:
                pt_level_int = int(pt_level)
            except ValueError:
                res = sc(code.ProetctLevelNotExist)
                res.result = res.result % pt_level
                raise gen.Return(res)
            if pt_level_int < 0 or pt_level_int > 2:
                res = sc(code.ProetctLevelNotExist)
                res.result = res.result % pt_level_int
                raise gen.Return(res)
            v = list(self.application.port_tcp_dict.values())
            k = list(self.application.port_tcp_dict.keys())
            pt_level = k[v.index(pt_level)]

        data_info = dict()
        data_info['SetIPFirewallProtectData'] = []
        if userid is None or userid == user_end:
            if firewall.set_protect_serial_number(ip, param_set=ps_level, set_tcp=pt_level):
                data_info['SetIPFirewallProtectData'].append(ip + '防护策略已设置')
                res = sc(code.Success)
                res.redata = data_info
            else:
                res = sc(code.IPNotExist)
                res.result = res.result % ip
        else:
            res = sc(code.PermissionDenied)
            res.result = res.result % ip

        raise gen.Return(res)
        # v_protect = self.params['ParamSet'] if 'ParamSet' in self.params else ''
        # v_filter = self.params['FilterSet'] if 'FilterSet' in self.params else ''
        # v_tcp = self.params['PortTCP'] if 'PortTCP' in self.params else ''
        # v_udp = self.params['PortUDP'] if 'PortUDP' in self.params else ''
