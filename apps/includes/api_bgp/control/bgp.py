#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tornado.web
import functools
import base64
import hashlib
import hmac
import re
import time
import datetime
import urllib.request
import urllib.parse
import urllib.error
from json import JSONEncoder
import ipaddress
from tornado import gen, netutil
import psycopg2.extras
from apps.common.base_handler import BaseHandler
from apps.common.pgdb_cursor_factory import PGDBCursorFactory
from apps.common.statusconfig import code, API_VERSION, statusconfig as sc
from apps.includes.api_bgp.paramConfig.bgpParams import bgpParams
from apps.includes.api_bgp.service.ComApi import ComApiService


class MainHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        self.httpMethod = "GET"
        result = yield self.main()
        self.write(result)
        self.finish()

    def logger_error(self):
        self.application.logger.error('%s,uri: %s', self.application.ts_begin_str, self.request.uri)
        self.application.logger.error('%s,params: %s', self.application.ts_begin_str, self.params)

    @gen.coroutine
    def main(self):
        self.application.ts_begin = datetime.datetime.now()
        self.application.ts_begin_str = str(self.application.ts_begin)
        self.application.history_backup_t_ip_protect=self.history_backup_t_ip_protect
        self.application.history_backup_t_package_protect=self.history_backup_t_package_protect
        self.application.dbconn = self.application.dbpool.getconn()
        self.application.dbcur = self.application.dbconn.cursor(cursor_factory=PGDBCursorFactory)
        self.application.dbconnflow = self.application.dbpoolflow.getconn()
        self.application.dbcurflow = self.application.dbconnflow.cursor(cursor_factory=PGDBCursorFactory)
        self.application.firewalllist = ['cc']
        self.application.zhifirewalllist = ['ctc', 'cmcc','cnc']
        self.application.ccfirewall = 'cc'
        self.application.wlmaxvalue = [50, 10]
        self.application.param_set_dict = {'0': '0', '1': '1', '2': '2'}
        self.application.port_tcp_dict = {'0': '0', '11': '1', '12': '2'}

        sys_parameter_data = self.application.dbcur.queryall_dict('select name,value,type,idx from t_sys_parameter')
        self.application.sys_parameter = {ret['name'] + ret['idx']: {ret['idx']: ret['value']} for ret in
                                          sys_parameter_data}
        psycopg2.extras.register_inet()
        result = ''
        res = self.checkParams()
        if isinstance(res, sc):
            result = res.getOApiResult()
        else:
            res = self.checkProtectGroup()
            if isinstance(res, sc):
                result = res.getOApiResult()
                self.logger_error()
                raise gen.Return(result)
            res = self.checkRegion()
            if isinstance(res, sc):
                result = res.getOApiResult()
                self.logger_error()
                raise gen.Return(result)
            res = self.checkZone()
            if isinstance(res, sc):
                result = res.getOApiResult()
                self.logger_error()
                raise gen.Return(result)
            res = self.checkPackageID()
            if isinstance(res, sc):
                result = res.getOApiResult()
                self.logger_error()
                raise gen.Return(result)
            res = self.checkPackageIDUserID()
            if isinstance(res, sc):
                result = res.getOApiResult()
                self.logger_error()
                raise gen.Return(result)
            res = self.checkBandwithType()
            if isinstance(res, sc):
                result = res.getOApiResult()
                self.logger_error()
                raise gen.Return(result)
            res = self.checkPermission()
            if isinstance(res, sc):
                result = res.getOApiResult()
            else:
                if 'IP' in self.params and 'PackageID' not in self.params:
                    res = self.checkIPOwner(self.params['IP'], self.params['Action'], self.params['AccessKeyId'])
                    if isinstance(res, sc):
                        result = res.getOApiResult()
                        self.logger_error()
                    else:
                        comApiService = ComApiService()
                        res = yield comApiService.run(self.params, self.application)
                        result = res.getOApiResult()
                elif 'IP' in self.params and 'PackageID' in self.params:
                    res = self.checkPackageIP(self.params['IP'], self.params['Action'])
                    if isinstance(res, sc):
                        result = res.getOApiResult()
                        self.logger_error()
                    else:
                        comApiService = ComApiService()
                        res = yield comApiService.run(self.params, self.application)
                        result = res.getOApiResult()
                else:
                    comApiService = ComApiService()
                    res = yield comApiService.run(self.params, self.application)
                    result = res.getOApiResult()
        api_lists_query = self.application.dbcur.queryone(
            'select api_name from t_api_lists where log_enable=True and api_id=%s;', (self.params['Action'],))
        if api_lists_query is not None and self.get_status() == 200 and res.id == 200:
            t_api_logs_data = {}
            t_api_logs_data['cts'] = self.application.ts_begin
            t_api_logs_data['ip'] = self.params['IP'] if 'IP' in self.params else None
            t_api_logs_data['ackid'] = self.params['AccessKeyId']
            t_api_logs_data['api_id'] = self.params['Action']
            t_api_logs_data['api_detail'] = api_lists_query[0] if api_lists_query else None
            t_api_logs_data['params'] = JSONEncoder().encode(self.params)
            t_api_logs_data['code'] = res.id
            t_api_logs_data['messages'] = res.result
            t_api_logs_data['status'] = res.status
            t_api_logs_data['duration'] = datetime.datetime.now() - self.application.ts_begin
            self.application.dbcur.insert_dict('t_api_logs', t_api_logs_data)
        if self.get_status() == 200 and res.id == 200:
            sql = "UPDATE t_api_info SET count_suc=count_suc+1,count_all=count_all+1 WHERE api_id=%s"
            self.application.dbcur.execute(sql, (self.params['Action'],))
        else:
            sql = "UPDATE t_api_info SET count_all=count_all+1 WHERE api_id=%s"
            self.application.dbcur.execute(sql, (self.params['Action'],))

        if res.id != 200:
            self.application.logger.error(
                '%s,%s,%s,%s,%s' % (self.application.ts_begin, self.params['Action'], res.id, res.result, res.status))
        raise gen.Return(result)

    # 检查参数IP是否为正确的IP地址
    def checkIP(self):
        k = 'IP'
        ip_r = []
        if k in self.params:
            v = self.get_argument(k)
            for ip in v.split(','):
                if netutil.is_valid_ip(ip):
                    ip_r.append(ip)
            if ip_r:
                return True
            else:
                res = sc(code.ParamError)
                res.result = res.result % v
                return res
        else:
            return True

    # 检查参数Region是否正确
    def checkRegion(self):
        k = 'Region'
        if k in self.params:
            v = self.get_argument(k)
            sql = 'select 1 from t_region where region_id=%s;'
            data = self.application.dbcur.queryall_dict(sql, (v,))
            if data:
                return True
            else:
                res = sc(code.RegionNotExist)
                res.result = res.result % v
                return res

    # 检查参数Zone是否正确
    def checkZone(self):
        pre_k = 'Region'
        k = 'Zone'
        if k in self.params and pre_k not in self.params:
            res = sc(code.ParamAbsence)
            res.result = res.result % pre_k
            return res
        if k in self.params:
            pre_v = self.get_argument(pre_k)
            v = self.get_argument(k)
            sql = 'select 1 from t_zone a, t_region b where a.region=b.id and b.region_id=%s and a.zone_id=%s;'
            data = self.application.dbcur.queryall_dict(sql, (pre_v, v))
            if data:
                return True
            else:
                res = sc(code.ZoneNotExist)
                res.result = res.result % v
                return res

    # 检查参数BandwithType是否正确
    def checkBandwithType(self):
        k = 'BandwithType'
        if k in self.params:
            v = self.get_argument(k)
            sql = 'select 1 from t_bandtype where bandtype_id=%s;'
            data = self.application.dbcur.queryall_dict(sql, (v,))
            if data:
                return True
            else:
                res = sc(code.BandwithTypeNotExist)
                res.result = res.result % v
                return res

    # 检查参数PackageID是否正确
    def checkPackageID(self):
        action = self.get_argument('Action')
        k = 'PackageID'
        sql_action = 'status=True' if action != 'DescribeProtectPackage' else '1=1'
        if k in self.params:
            v = self.get_argument(k)
            sql = 'select 1 from t_package_protect where package_protect_id=%s and {0};'.format(sql_action)
            data = self.application.dbcur.queryall_dict(sql, (v,))
            if data:
                return True
            else:
                res = sc(code.PackageNotExist)
                res.result = res.result % v
                return res

    # 检查参数PackageID是否正确
    def checkPackageIDUserID(self):
        j = 'IPUserID'
        k = 'PackageID'
        if j in self.params and k in self.params:
            user_org = self.get_argument('AccessKeyId')
            v = self.get_argument(k)
            b = self.get_argument(j)
            sql = 'select 1 from t_package_protect where package_protect_id=%s and user_org=%s and user_end=%s;'
            data = self.application.dbcur.queryall_dict(sql, (v, user_org, b))
            if data:
                return True
            else:
                res = sc(code.PermissionDenied)
                res.result = res.result % b
                return res

    # 检查参数IP是否属于Package
    def checkPackageIP(self, ip, action):
        j = ip.split(',')
        k = 'PackageID'
        if action == 'AddProtectPackageIP':
            return True
        if 'IP' in self.params and k in self.params:
            user_org = self.get_argument('AccessKeyId')
            if 'IPUserID' in self.params:
                user_end = self.get_argument('IPUserID')
            else:
                res = sc(code.ParamError)
                res.result = res.result % '请输入IPUserID'
                return res
            v = self.get_argument(k)
            desc_sql = 'b.status=True' if 'DescribeIP'not in action else '1=1'
            for i in j:
                sql = 'select 1 from t_package_protect a join t_ip_protect b on a.id=b.package where a.package_protect_id=%s and b.user_org=%s and b.user_end=%s and b.ip=%s and {0};'.format(desc_sql)
                data = self.application.dbcur.queryall_dict(sql, (v, user_org, user_end, i))
                if data:
                    return True
                else:
                    res = sc(code.PermissionDenied)
                    res.result = res.result % ip
                    return res

    # 检查参数ProtectGroup是否正确
    def checkProtectGroup(self):
        k = 'BandwithType'
        if k in self.params:
            v = self.get_argument(k)
            sql = 'select id from t_bandtype where bandtype_id=%s;'
            data = self.application.dbcur.queryall_dict(sql, (v,))
            bandtype = data[0]['id'] if data else None
        else:
            bandtype = None
        k_list = ['guaranteeProtectGroupID', 'elasticProtectGroupID', 'GuaranteeProtectGroupID',
                  'ElasticProtectGroupID']
        for k in k_list:
            if k in self.params:
                v = self.get_argument(k)
                if bandtype:
                    sql = 'select 1 from t_protect where protect_id=%s and bandtype=%s;'
                    data = self.application.dbcur.queryall_dict(sql, (v, bandtype))
                else:
                    sql = 'select 1 from t_protect where protect_id=%s;'
                    data = self.application.dbcur.queryall_dict(sql, (v,))
                if data:
                    pass
                else:
                    res = sc(code.ProtectGroupNotExit)
                    res.result = res.result % v
                    return res
        return True

    # 检查是否有权限查看该IP
    def checkIPOwner(self, ip_list, action, myAccessKey):
        action_disable = ['ModifyIPProtectGroup', 'CloseIPElasticAntiDDos', 'OpenIPElasticAntiDDos', 'CloseIPAntiDDos', 'OpenIPAntiDDos', 'DeleteProtectGroupIP']
        if 'DescribeNormalIP' in action or action == 'AddProtectGroupIP':
            return True
        if action in action_disable:
            for ip in ip_list.split(','):
                sql = 'select count(1) is_exists,user_org from t_ip_protect where ip=%s and status =TRUE group by user_org'
                data = self.application.dbcur.queryall_dict(sql, (ip,))
                if not data:
                    res = sc(code.IPNotExist)
                    res.result = res.result % ip
                    return res
                sql = 'select count(1) is_exists,user_org from t_ip_protect where ip=%s and status=TRUE AND package is null group by user_org'
                data = self.application.dbcur.queryall_dict(sql, (ip,))
                if not data:
                    res = sc(code.PermissionDenied)
                    res.result = res.result % '不允许对服务包IP进行此操作'
                    return res
                user_org = [x['user_org'] for x in data]
                if myAccessKey not in user_org:
                    res = sc(code.PermissionDenied)
                    res.result = res.result % ip
                    return res
        if 'DescribeIP' in action and action != 'DescribeIPInfo':
            for ip in ip_list.split(','):
                sql = 'select count(1) is_exists,user_org from t_ip_protect where ip=%s group by user_org'
                data = self.application.dbcur.queryall_dict(sql, (ip,))
                if not data:
                    res = sc(code.IPNotExist)
                    res.result = res.result % ip
                    return res
                user_org = [x['user_org'] for x in data]
                if myAccessKey not in user_org:
                    res = sc(code.PermissionDenied)
                    res.result = res.result % ip
                    return res
        else:
            for ip in ip_list.split(','):
                sql = 'select count(1) is_exists,user_org from t_ip_protect where ip=%s AND status=TRUE group by user_org'
                data = self.application.dbcur.queryall_dict(sql, (ip,))
                if not data:
                    res = sc(code.IPNotUsed)
                    res.result = res.result % ip
                    return res
                user_org = [x['user_org'] for x in data]
                if myAccessKey not in user_org:
                    res = sc(code.PermissionDenied)
                    res.result = res.result % ip
                    return res
        return True

    # 检查公共参数完整性
    def checkParams(self):
        for p in bgpParams.CommonParams:
            # if not self.params.has_key(p):
            if p not in self.params:
                res = sc(code.ParamAbsence)
                res.result = res.result % p
                return res
            res = self.checkParamType("CDN", p)
            if isinstance(res, sc):
                return res

        if int(self.params["Version"]) != API_VERSION:
            res = sc(code.APIVersionError)
            res.result = res.result % self.params["Version"]
            return res
        if self.params["Action"] not in bgpParams.ActionParams:
            res = sc(code.NoThisAction)
            return res
        for p in bgpParams.ActionParams[self.params["Action"]]:
            res = self.checkActionParams(self.params["Action"], p)
            if isinstance(res, sc):
                return res
        return True

    # 检查Action参数完整性
    def checkActionParams(self, Action, Param):
        isneed = True
        if Param[0:1] == '_':
            isneed = False
            Param = Param[1:]
        if isneed and Param not in self.params:
            res = sc(code.ParamAbsence)
            res.result = res.result % Param
            return res
        if Param in self.params:
            res = self.checkParamType(Action, Param)
            if isinstance(res, sc):
                return res
        return True

    # 检查参数格式是否符合要求
    def checkParamType(self, Action, Param):
        pk = "_".join([Action, Param])
        cre = ''
        clist = []
        if pk in bgpParams.ParamTrans:
            cre = bgpParams.ParamTrans[pk][2]
        elif Param in bgpParams.ParamTrans:
            cre = bgpParams.ParamTrans[Param][2]
        if cre != "" and cre.find("@") != -1:
            clist = cre.split("@")
            isRaise = False
            if clist[0] == "TIME":
                try:
                    time.strptime(self.params[Param], clist[1])
                except:
                    isRaise = True
            elif clist[0] == "RE":
                m = re.match(clist[1], self.params[Param])
                if not m:
                    isRaise = True
            elif clist[0] == 'IP':
                iplist = self.params[Param].split(',')
                for ip in iplist:
                    try:
                        ipaddress.ip_address(ip)
                    except:
                        isRaise = True
            elif clist[0] == "TYPE":
                try:
                    inmsg = self.params[Param]
                    inmsg = inmsg.replace('null', 'None')
                    inmsg = inmsg.replace('true', 'True')
                    inmsg = inmsg.replace('false', 'False')
                    inmsg = eval(inmsg)
                    if clist[1] == "list":
                        if not isinstance(inmsg, list):
                            isRaise = True
                    elif clist[1] == "dict":
                        if not isinstance(inmsg, dict):
                            isRaise = True
                except:
                    isRaise = True

            if isRaise:
                res = sc(code.ParamError)
                # res.result = res.result % Param
                res.result = res.result % '[' + Param + ':' + self.params[Param] + ']'
                return res
        return True

    # 获取加密key
    def getKey(self, AccessKeyId):
        sql = 'select ackseckey from t_users where ackid=%s;'
        data = self.application.dbcur.queryone(sql, (AccessKeyId,))
        if data is None:
            return None
        else:
            return data[0]

    # 权限验证
    def checkPermission(self):
        AccessKeySecret = self.getKey(self.params["AccessKeyId"])
        if not AccessKeySecret:
            res = sc(code.ParamError)
            res.result = res.result % "AccessKeyId"
            return res
        hmacStr = hmac.new(AccessKeySecret.encode(), self.dealparam(self.params).encode(), hashlib.sha1)
        sign = base64.b64encode(hmacStr.digest())
        if self.params["Signature"] != sign.decode('utf-8'):
            res = sc(code.ParamError)
            res.result = res.result % "Signature"
            return res
        return True

    # 处理加密串
    def dealparam(self, par):
        keys = list(par.keys())
        keys.sort()
        canonicalizedQueryString = ''
        for k in keys:
            if k == "Signature":
                continue
            canonicalizedQueryString += '&' + self.res(k) + '=' + self.res(par[k])
        stringToSign = self.httpMethod + '&/ip&' + canonicalizedQueryString[1:]
        return stringToSign

    # 特殊字符处理
    def res(self, par):
        par = par.encode("utf-8")
        par = urllib.parse.quote(par)
        par = par.replace('+', '%20')
        par = par.replace('*', '%2A')
        par = par.replace('%7E', '~')
        par = par.replace('/', '%2F')
        return par


class HeartBeat(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        self.httpMethod = "GET"
        self.write('OK')
        self.finish()
        return


class UNBan(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        self.httpMethod = "GET"
        try:
            ip = self.get_query_arguments('ip')[0] + '/32'
            line = self.get_query_arguments('line')[0]
        except Exception as exc:
            self.write('Faild')
            self.finish()
            return
        self.application.logger.warn('unban for: %s %s', ip, line)
        self.application.dbconnflow = self.application.dbpoolflow.getconn()
        self.application.dbcurflow = self.application.dbconnflow.cursor(cursor_factory=PGDBCursorFactory)
        sql = "update t_blockhole set ban_time=now()-ts,unban_type='manual' where ip=%s::inet and line=%s"
        # self.application.dbcurflow.insert_dict()
        self.application.dbcurflow.execute(sql, (ip, line))
        self.application.dbconnflow.commit()
        self.application.dbpoolflow.putconn(self.application.dbconnflow)
        self.write('OK')
        self.finish()


if __name__ == '__main__':
    par = "~!@#$%^&*()+=_-sdf sfg13\\'/"
    par = urllib.parse.quote(par)
    print(par)
    urllib.parse.unquote("%7E")
