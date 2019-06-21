#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import uuid

from apps.common import tools

API_VERSION = 2


class code():
    APIVersionError = 'APIVersionError'
    Success = 'Success'
    Fail = 'Fail'
    DuplicateRequest = 'DuplicateRequest'
    NoThisAction = 'NoThisAction'
    ParamAbsence = 'ParamAbsence'
    ParamError = 'ParamError'
    CnameError = 'CnameError'
    CnameNotExist = 'CnameNotExist'
    TimeError = 'TimeError'
    IPTooMuch = 'IPTooMuch'
    StartTimeTooEarly = 'StartTimeTooEarly'
    IPError = 'IPError'
    DomainError = 'DomainError'
    IPNotExist = 'IPNotExist'
    IPFormatError = 'IPFormatError'
    DomainNotExist = 'DomainNotExit'
    ProtectGroupNotExit = 'ProtectGroupNotExit'
    IPConflict = 'IPConflict'
    IPAddFail = 'IPAddFail'
    ProtectGroupUnusable = 'ProtectGroupUnusable'
    IPDeleteFail = 'IPDeleteFail'
    CommitFail = 'CommitFail'
    ChangeFail = 'ChangeFail'
    QueryFail = 'QueryFail'
    IPNoProtectGroup = 'IPNoProtectGroup'
    InternalError = 'InternalError'
    ServiceUnavailable = 'ServiceUnavailable'
    RegionNotExist = 'RegionNotExist'
    ZoneNotExist = 'ZoneNotExist'
    BandwithTypeNotExist = 'BandwithTypeNotExist'
    IPNotUsed = 'IPNotUsed'
    IPNotProtect = 'IPNotProtect'
    DataNotConform = 'DataNotConform'
    IPNotElasticprotectProtect = 'IPNotElasticprotectProtect'
    NotInCorrectStatus = 'NotInCorrectStatus'
    NotCorrectStatus = 'NotCorrectStatus'

    RemoteSerConnFaile = 'RemoteSerConnFaile'
    RemoteSerConnTimeout = 'RemoteSerConnTimeout'
    RemoteSerAuthFaile = 'RemoteSerAuthFaile'
    RemoteSerIOErr = 'RemoteServerIOError'
    RemoteSerExecCMDErr = 'RemoteSerExecCMDErr'
    FirewallConnFail = 'FirewallConnFail'
    SLBConfTcpNoSingle = 'SLBConfTcpNoSingle'
    SLBConfDuplicate = 'SLBConfDuplicate'
    SLBConfCheckFaile = 'SLBConfCheckFaile'
    SLBConfNotExist = 'SLBConfNotExist'
    ParamNotPair = 'ParamNotPair'
    TimeIntervalTooLong = 'TimeIntervalTooLong'  # longest
    # ProxyConfPortErr='Proxy Config Port Error'
    # ProxyConfSoureIPErr='Proxy Config SoureIP Error'
    PermissionDenied = 'PermissionDenied'
    SysPackageNotExist = 'SysPackageNotExist'
    PackageNotExist = 'PackageNotExist'
    PackageError = 'PackageError'
    IPNumsError = 'IPNumsError'
    PackageStatusError = 'PackageStatusError'
    PackageIPError = 'PackageIPError'
    ProetctLevelNotExist = 'ProetctLevelNotExist'
    MaxWhiteList = 'MaxWhiteList'


class statusconfig(object):
    Results = {
        code.Success: [200, 'Success'],
        # code.Fail: [9400, 'Fail'],
        code.DuplicateRequest: [9304, '修改前后数据没有变化：%s'],
        code.APIVersionError: [9400, 'API版本参数错误,应该为: ' + str(API_VERSION) + ',您提交: %s'],
        code.ParamAbsence: [9400, '该参数是必须提交的: %s'],
        code.TimeError: [9400, '时间参数有错'],
        code.ParamNotPair: [9400, '参数必须配对使用: %s %s'],
        code.NoThisAction: [9400, '不存在该操作: %s'],
        code.PackageError: [9402, '服务包IP余量不足：%s'],
        code.PermissionDenied: [9401, '您没有权限进行该操作: %s'],

        # code.CnameError: [9400, 'This domain cname is error : %s'],
        # code.CnameNotExist: [9400, 'This domain cname is not exist : %s'],
        # code.StartTimeTooEarly: [9400, '指定的开始时间参数有误'],

        code.IPNumsError: [9400, 'IP数量超过限制:%s'],
        code.ProtectGroupNotExit: [9402, '防护组id参数不存在: %s'],
        code.IPFormatError: [9402, 'IP数据错误: %s'],
        # code.DomainNotExist: [9402, '域名不存在: %s'],
        code.RegionNotExist: [9402, '指定地域不存在: %s'],
        code.ZoneNotExist: [9402, '指定区域不存在: %s'],
        code.BandwithTypeNotExist: [9402, '指定带宽类型不存在: %s'],
        code.SysPackageNotExist:[9402, '指定系统服务包不存在: %s'],
        code.PackageNotExist: [9402, '指定服务包不存在或关闭: %s'],
        code.PackageIPError: [9403, '请先删除包内所有IP:%s'],
        code.PackageStatusError: [9405, '服务包状态不允许该操作:%s'],
        code.DataNotConform: [9403, '未找到符合状态的数据：%s'],
        code.IPNotExist: [9403, 'IP不存在: %s'],
        code.IPError: [9403, "此IP已被他人配置: %s"],
        code.DomainError: [9403, "此域名已被他人配置: %s"],
        code.IPConflict: [9403, '指定的IP地址冲突:%s'],
        # code.IPNotElasticprotectProtect: [409, 9403, '指定的IP未处于弹性防护状态:%s'],
        code.NotInCorrectStatus: [9403, '未处于正确的状态:%s'],
        code.NotCorrectStatus: [9403, 'IP已加入高仿包或防护组:%s'],

        # code.IpNoProtectGroup: [9400, '该IP不属于任何防护组: %s'],
        code.IPNotUsed: [9403, 'IP未在使用中: %s'],
        # code.IPNotProtect: [404, 9403, 'IP未启用弹性防护: %s'],
        code.ParamError: [9405, '您提交的参数错误: %s'],

        code.SLBConfCheckFaile: [9407, '代理配置信息验证失败：%s'],
        code.SLBConfNotExist: [9407, '代理配置信息不存在：%s'],
        code.SLBConfTcpNoSingle: [9407, '代理配置TCP协议只能拥有一个源站信息'],
        code.SLBConfDuplicate: [9407, '代理配置重复：%s'],

        # code.IPDeleteFail: [9408, 'IP解除防护组失败: %s'],
        code.IPAddFail: [9408, 'IP添加防护组失败: %s'],
        code.MaxWhiteList: [9408, '添加白名单数量已达上线'],
        code.CommitFail: [9408, '提交修改失败, 请联系运维人员线下修改: %s'],
        code.ChangeFail: [9408, '修改失败: %s'],
        code.QueryFail: [9408, '查询失败: %s'],
        code.FirewallConnFail: [9408, '防火墙连接失败: %s'],
        code.TimeIntervalTooLong: [9408, '时间间隔太长,不得超过: %s'],

        # code.ProtectGroupUnusable: [9500, '部署失败，请联系开发人员'],
        # code.IpAddFaild:[503,'添加失败，正在处理其他请求，请稍后重试'],
        # code.InternalError: [500, 9500, '远程服务器错误，请联系我们: %s'],
        # code.ServiceUnavailable: [9500, '由于暂时的服务器问题，请求失败: %s'],
        code.RemoteSerConnFaile: [9502, '远程服务器连接失败: %s'],
        code.RemoteSerConnTimeout: [9504, '远程服务器连接超时: %s'],
        code.RemoteSerAuthFaile: [9504, '远程服务器认证失败: %s'],
        code.RemoteSerIOErr: [9504, '远程服务器IO错误: %s'],
        # code.RemoteSerExecCMDErr: [400, 9504, '远程服务器执行命令错误: %s'],
        # code.ProxyConfPortErr: [9500, '代理配置端口错误：%s'],
        # code.ProxyConfSoureIPErr: [9500, '代理配置源站信息错误：%s'],

        code.ProetctLevelNotExist: [9403, '防护策略不存在: %s'],

    }

    def __init__(self, status_code, id=-99, result='ERROR', ispack=True):
        self.status = status_code
        self.ispack = ispack
        self.redata = {}
        if status_code in self.Results:
            self.id = id if id != -99 else self.Results[status_code][0]
            # self.code = code if code != -99 else self.Results[status_code][0]
            self.result = result if result != 'ERROR' else self.Results[status_code][-1]
        else:
            self.id = id
            self.result = result
        self.mkjson()

    def mkjson(self):
        self.json = {}
        self.json['id'] = self.id
        # self.json['code'] = self.code
        self.json['status'] = self.status
        self.json['result'] = self.result
        self.json['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() + 8 * 60 * 60))

    def getjsonstr(self):
        if self.ispack:
            self.mkjson()
            self.jsonstr = tools.prf(self.json, str=False)
            return self.jsonstr
        else:
            return tools.prf(self.result, str=False)

    def getresult(self):
        return tools.prf(self.result)

    def getOApiResult(self):
        json = {}
        uid = uuid.uuid4()
        json['RequestId'] = str(uid)
        json['Code'] = self.id
        json['Status'] = self.status
        json['Message'] = self.result
        json['Timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() + 8 * 60 * 60))
        for k in list(self.redata.keys()):
            json[k] = self.redata[k]
        return tools.prf(json)


if __name__ == '__main__':
    s = statusconfig(200)
    print((s.getjsonstr()))
