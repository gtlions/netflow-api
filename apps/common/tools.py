#!/usr/bin/env python
#  -*- coding: gbk -*-
import datetime
import logging
import os
import sys
import time

from apps.API_BGP.config.config import logger_name


pclist = []

if sys.version >= '3.2.':
    localtimezone = datetime.timezone(datetime.timedelta(seconds=-time.timezone), time.tzname[0])
    utctimezone = datetime.timezone.utc
else:
    from dateutil import tz

    localtimezone = tz.tzlocal()
    utctimezone = tz.gettz('UTC')


def parsedatetime(dt, fmt="%Y-%m-%dT%H:%M:%SZ"):
    """parse local datetime string as utc datetime object"""
    # print datetime.datetime.strptime(dt, fmt).replace(tzinfo=localtimezone).astimezone(utctimezone)
    return datetime.datetime.strptime(dt, fmt).replace(tzinfo=localtimezone).astimezone(utctimezone).strftime(fmt)


def formatdatetime(dt, fmt="%Y-%m-%dT%H:%M:%SZ"):
    """format utc datetime object as local datetime string"""
    # print dt.replace(tzinfo=utctimezone).astimezone(localtimezone).strftime(fmt)
    return dt.replace(tzinfo=utctimezone).astimezone(localtimezone).strftime(fmt)


def front5min(dt):
    """
    low catch 5 minutes"""
    dtime = int(dt[15])
    if dtime == 0 or dtime < 5:
        dtimex = '0'
    elif dtime >= 5:
        dtimex = '5'
    return dt[:15] + "%s:00" % (dtimex)


def front1hour(dt):
    return dt[:14] + "%s:00Z" % ("00")


def front1day(dt):
    return dt[:11] + "00:00:00"

logger = logging.getLogger(logger_name)
logger.setLevel(logging.DEBUG)
def logready(ROOT_PATH):
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(name)s,%(asctime)s,%(levelname)s,%(message)s')
    handler_s = logging.StreamHandler()
    handler_s.setFormatter(fmt)
    logger.addHandler(handler_s)

    logdir = os.path.join(ROOT_PATH, 'logs/').replace('\\', '/')
    handler_f = logging.FileHandler(logdir + time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.log',
                                    encoding='utf8')
    handler_f.setFormatter(fmt)
    logger.addHandler(handler_f)


def mkjs(ROOT_PATH, key, pclist=pclist):
    logger.info('make js file ...')
    pcdic = {}
    for pc in pclist:
        for jsname in list(pc.__dict__.keys()):
            if '_' in jsname:
                continue
            jd = getattr(pc, jsname)
            if jsname in pcdic:
                res = adddic(pcdic[jsname], jd)
                if isinstance(res, list):
                    logger.info('repetition:' + pc.__name__ + '.' + jsname)
                    logger.info('repetition_data:' + str(res))
                    raise Exception('params config have repetition data')
            else:
                pcdic[jsname] = jd
    checkData(pcdic)
    for k in pcdic:
        mkjsfile(k, pcdic[k], ROOT_PATH, key)
    logger.info('make js file end')


def checkData(pcdic):
    vlist = []
    missList = []
    if 'Divide' in pcdic:
        divide = pcdic['Divide']
        for k in range(len(divide) - 1):
            if divide[k] in pcdic and divide[k + 1] in pcdic:
                for v in pcdic[divide[k]]:
                    vlist.append(v)
                    for cv in pcdic[divide[k]][v]:
                        if cv[0:1] == '_':
                            cv = cv[1:]
                        if cv == '':
                            break
                        vlist.append(cv)
                        if cv not in pcdic[divide[k + 1]]:
                            missList.append((divide[k + 1], cv))
            else:
                raise Exception('params config miss divide key')
        if divide[-1] in pcdic:
            for v in pcdic[divide[-1]]:
                for cv in pcdic[divide[-1]][v]:
                    if cv[0:1] == '_':
                        cv = cv[1:]
                    if cv == '':
                        break
                    vlist.append(cv)
        vlist = list(set(vlist))
        vlist.sort()
        for v in vlist:
            if v not in pcdic['ParamTrans']:
                missList.append(('ParamTrans', v))
        group = ''
        israise = False

        for mv in missList:
            if mv[0] == 'ParamTrans':
                israise = True
            if group != mv[0]:
                group = mv[0]
                print(group)
            print(("'" + mv[1] + "':['',''],"))
        if israise:
            raise Exception('params config miss ParamTrans key')

    else:
        raise Exception('params config miss divide')


def adddic(odic, tdic):
    repetition = []
    for k in tdic:
        if k in odic:
            repetition.append(k)
        else:
            odic[k] = tdic[k]
    if len(repetition) > 0:
        return repetition
    return True


def mkjsfile(jsname, data, ROOT_PATH, key):
    jspath = os.path.join(ROOT_PATH, 'static/apicall/js/' + jsname + '_' + key + '.js').replace('\\', '/')
    try:
        actions_file = open(jspath, 'w')
        actions_file.write('var ' + jsname + ' = ' + prf(data) + ';')
        actions_file.close()
        logger.info('make ' + jsname + ' success')
    except Exception as ex:
        logger.info('make js error ' + ex.message)


def prf(res, num=0, ):
    tab = '    '
    resu = ''
    if isinstance(res, dict):
        keys = list(res.keys())
        keys.sort()
        resu += '\n' + tab * num + '{'
        for k in keys:
            resu += '\n' + tab * (num + 1) + prf(k, num + 1) + ':' + prf(res[k], num + 1)
            if k == keys[-1]:
                break
            resu += ','
        resu += '\n' + tab * num + '}'
    if isinstance(res, list):
        resu += '\n' + tab * num + '['
        for k in res:
            resu += '\n' + tab * (num + 1) + prf(k, num + 1)
            if k == res[-1]:
                break
            resu += ','
        resu += '\n' + tab * num + ']'
    if isinstance(res, str):
        if str:
            resu += '"' + res.replace('"', "'") + '"'  # .decode('raw_unicode_escape')
        else:
            resu += '"' + res.replace('"', "'") + '"'
    if isinstance(res, int):
        resu += str(res)
    if isinstance(res, float):
        resu += str(res)
    return resu


def printlist(self, datalist):
    datastr = ''
    datastr += '['
    for index in range(len(datalist)):
        if type(datalist[index]) == type('1'):
            datastr += "'" + datalist[index] + "'"
        elif type(datalist[index]) == type([]):
            datastr += printlist(datalist[index])
        else:
            datastr += str(datalist[index])
        if index == len(datalist) - 1:
            break

        datastr += ', '
    datastr += ']'
    return datastr


if __name__ == '__main__':
    #    logready()
    #    mkjs()
    a = '1+\\u6b63\\u786e\\u5bc6\\u6587\\u5bc6\\u7801'
    #    a = '1+nimei'
    print((a.decode('raw_unicode_escape')))
