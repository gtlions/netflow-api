#!/usr/bin/env python
# -*- coding: utf-8 -*-


class bgpParams(object):
    CommonParams = [
        'Timestamp',
        'AccessKeyId',
        'Signature',
        'Version',
        'SignatureNonce',
        'Action',
    ]

    ActionParams = {
        'DescribeSysProtectPackage': [],
        'CreateProtectPackage': ['IPUserID', 'PackageName', 'IPNums', 'GuaranteeProtectGroupID',
                                 'ElasticProtectGroupID', 'LifeDay', 'BandwithType'],
        'DescribeProtectPackage': ['_IPUserID', '_PackageID'],
        'AddProtectPackageIP': ['PackageID', 'IP', 'IPUserID', ],
        'DeleteProtectPackageIP': ['PackageID', 'IP', '_IPUserID', ],
        'DeleteProtectPackage': ['PackageID', 'IPUserID', ],

        'DescribeProtectGroup': ['_Region', '_Zone', '_BandwithType'],
        'AddProtectGroupIP': ['IP', '_IPUserID', 'guaranteeProtectGroupID', 'elasticProtectGroupID', 'Region', 'Zone',
                              'BandwithType'],
        'DescribeIPInfo': ['_IP', '_IPUserID'],
        'DescribeIPStatus': ['_IP', '_IPUserID'],
        'ModifyIPProtectGroup': ['IP', '_IPUserID', '_GuaranteeProtectGroupID', '_GuaranteeEnableTime',
                                 '_ElasticProtectGroupID',
                                 '_ElasticEnableTime',
                                 'Region', 'Zone', 'BandwithType'],
        'CloseIPElasticAntiDDos': ['IP', '_IPUserID'],
        'OpenIPElasticAntiDDos': ['IP', '_IPUserID'],
        'CloseIPAntiDDos': ['IP', '_IPUserID'],
        'OpenIPAntiDDos': ['IP', '_IPUserID', 'ElasticEnable'],
        'DescribeIPMonitorData': ['IP', '_IPUserID', '_PackageID', 'StartTime', 'EndTime', '_Region', '_Zone', '_BandwithType'],
        'DescribeIPMaxMonitorData': ['IP', '_IPUserID', '_PackageID', 'StartTime', 'EndTime', '_Region', '_Zone', '_BandwithType'],
        'DescribeIPLineMonitorData': ['IP', '_IPUserID',  '_PackageID', 'StartTime', 'EndTime', '_Region', '_Zone', '_BandwithType'],
        'DeleteProtectGroupIP': ['IP', '_IPUserID'],
        'CreateIPFourLayerAntiConfig': ['IP', '_IPUserID', 'Configs'],
        'UpdateIPFourLayerAntiConfig': ['IP', '_IPUserID', 'UUID', 'Configs'],
        'DeleteIPFourLayerAntiConfig': ['IP', '_IPUserID', 'UUID'],
        'CreateIPSevenLayerAntiConfig': ['IP', '_IPUserID', 'Configs'],
        'UpdateIPSevenLayerAntiConfig': ['IP', '_IPUserID', 'UUID', 'Configs'],
        'DeleteIPSevenLayerAntiConfig': ['IP', '_IPUserID', 'UUID'],
        'GetIPMetricInfo': ['_IP', '_IPUserID', '_StartTime', '_EndTime'],
        'DescribeIPFirewallList': ['Hostname', 'Operator', '_IPUserID', '_IP'],
        'DescribeDomainFirewallList': ['Hostname', 'Operator', '_IPUserID'],
        'AddIPWhiteList': ['Hostname', 'Operator', 'IPUserID', '_IP', '_PackageID'],
        'AddDomainWhiteList': ['Hostname', 'Operator', 'IPUserID', '_IP', '_PackageID'],
        'DeleteDomainWhiteList': ['Hostname', 'Operator', 'IPUserID', '_IP', '_PackageID'],
        'DeleteIPWhiteList': ['Hostname', 'Operator', 'IPUserID', '_IP', '_PackageID'],
        'DescribeBlockList': ['SourceIP', 'Operator', '_IPUserID'],
        'ResetBlockIP': ['SourceIP', 'RemoteIP', 'Operator', 'IPUserID'],
        'DescribeIPFirewallProtect': ['IP', '_IPUserID'],
        'SetIPFirewallProtect': ['IP', 'IPUserID', '_GlobalProtectLevel', '_WebProtectLevel'],
        'ModifyProtectPackage': ['PackageID', '_GuaranteeProtectGroupID', '_ElasticProtectGroupID',
                                 '_GuaranteeEnableTime', '_ElasticEnableTime', '_IPNums'],
        'DescribeBlackHoleInfo': ['_IP', '_IPUserID', 'StartTime', 'EndTime'],
        'ExtendProtectPackageDueTime': ['PackageID', 'LifeDay', 'IPUserID'],
        'ClosePackageElasticAntiDDos': ['PackageID',  'IPUserID'],
        'OpenPackageElasticAntiDDos': ['PackageID', 'IPUserID'],
        'DescribeNormalIPData': ['IP', 'StartTime', 'EndTime'],
        'DescribeNormalIPMaxData': ['IP', 'StartTime', 'EndTime'],

        'DescribeUserFirewallWhiteList': ['IPUserID', '_PackageID', '_IP', '_Domain'],
        'DescribeNormalIPBlackHoleInfo': ['IP'],
        'AttackBehaviorAnalysis': ['IP'],

    }

    # [名称、格式说明、数据类型、子属性、]
    ParamTrans = {
        'Timestamp': ['时间戳', '要使用UTC时间', 'TIME@%Y-%m-%dT%H:%M:%SZ'],
        'AccessKeyId': ['密钥ID', '', ''],
        'Signature': ['签名串', '', ''],
        'Version': ['API版本', '整形', 'RE@\\b(1|2|3|4|5)\\b'],
        'SignatureNonce': ['防并发随机数', '', ''],
        'DescribeIPMonitorData': ['获取BGP监控数据', '', ''],
        'DescribeIPStatus': ['获取BGPIP状态', '', ''],
        'DescribeProtectGroup': ['获取可用的防护组', '', ''],
        'AddProtectGroupIP': ['添加IP到指定防护组', '', ''],
        'DeleteProtectGroupIP': ['删除IP的防护组', '', ''],
        'DescribeIpInfo': ['获取IP的防护组信息', '', ''],
        'IP': ['IP地址', 'IP地址', 'IP@ipv4'],
        'StartTime': ['开始时间', '要使用UTC时间', 'TIME@%Y-%m-%dT%H:%M:%SZ'],
        'EndTime': ['结束时间', '要使用UTC时间', 'TIME@%Y-%m-%dT%H:%M:%SZ'],
        'ElasticEnableTime': ['结束时间', '要使用UTC时间', 'TIME@%Y-%m-%dT%H:%M:%SZ'],
        'InstanceId': ['服务器ID', '', '']
    }
