#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors    : Gtlions Lai <gtlions.l@qq.com>

import os
import sys
import time
import logging
import platform
import psycopg2
import psycopg2.pool
import tornado.ioloop
import tornado.web
from apscheduler.schedulers.tornado import TornadoScheduler


ROOT_PATH = os.path.dirname(__file__)

sys.path.append(ROOT_PATH)
# sys.path.append("/home/API/bgpapi/")
sys.path.append(ROOT_PATH + "/../../")
# from apps.common import tools

# tools.logready(ROOT_PATH)

import apps.API_BGP.urls as local_urls
from apps.API_BGP.config.config import logger_name, ENV, CONFIG, config_banner
from apps.includes.api_bgp.service.schedulejob import modify_ip_protectgroup, CheckProtectPackageDueTime, delete_ip_white_list
from apps.API_BGP.server_info import get_server_info


class Application(tornado.web.Application):
    def __init__(self):
        if ENV == 'PROD':
            settings = dict(
                cookie_secret="yaojh",
                login_url="/login",
                xsrf_cookies=False
            )
        else:
            settings = dict(
                cookie_secret="yaojh",
                login_url="/login",
                xsrf_cookies=False,
                debug=True,
                autoreload=True
            )
        handlers = local_urls.urlpatterns
        tornado.web.Application.__init__(self, handlers, **settings)

        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        fmt = logging.Formatter('%(name)s,%(asctime)s,%(levelname)s,%(message)s')
        handler_s = logging.StreamHandler()
        handler_s.setFormatter(fmt)
        self.logger.addHandler(handler_s)

        logdir = os.path.join(ROOT_PATH, 'logs/').replace('\\', '/')
        handler_f = logging.FileHandler(logdir + time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.log',
                                        encoding='utf8')
        handler_f.setFormatter(fmt)
        self.logger.addHandler(handler_f)

        self.logger.info('Initial BGPAPI App')
        self.logger.info(config_banner)
        try:
            self.dbpool = psycopg2.pool.ThreadedConnectionPool(3, 180, host=CONFIG.DB.host,
                                                               port=CONFIG.DB.port,
                                                               user=CONFIG.DB.user,
                                                               password=CONFIG.DB.pwd,
                                                               dbname=CONFIG.DB.dbname,
                                                               application_name='Apps@API',
                                                               connect_timeout=15)
        except Exception as exc:
            self.logger.error('Init api db failed.')
            self.logger.error(exc)
            sys.exit(1)

        try:
            self.dbpoolflow = psycopg2.pool.ThreadedConnectionPool(3, 300, host=CONFIG.FlowDB.host,
                                                                   port=CONFIG.FlowDB.port,
                                                                   user=CONFIG.FlowDB.user,
                                                                   password=CONFIG.FlowDB.pwd,
                                                                   dbname=CONFIG.FlowDB.dbname,
                                                                   application_name='Apps@API',
                                                                   connect_timeout=15)
        except Exception as exc:
            self.logger.error('Init flow db failed.')
            self.logger.error(exc)
            sys.exit(1)

        self.logger.info('Initial BGPAPI App completed')
        self.logger.removeHandler(handler_s)


def main(port, host):
    app = Application()
    app.listen(port, "0.0.0.0")
    if platform.system() == 'Linux':
        get_server_info()
    scheduler = TornadoScheduler()
    scheduler.add_job(modify_ip_protectgroup.modify_ip_protectgroup, 'interval', seconds=10)
    scheduler.add_job(modify_ip_protectgroup.modify_package, 'interval', seconds=10)
    scheduler.add_job(CheckProtectPackageDueTime.CheckProtectPackageDueTime, 'cron', hour=0, minute=0)
    scheduler.add_job(delete_ip_white_list.delete_ip_white_list, 'interval', seconds=20)
    # if CONFIG.RecordLog.record_way == 'new':
    #     scheduler.add_job(getblocklist.block_cmcc_log, 'interval', seconds=1200)
    #     scheduler.add_job(getblocklist.block_cnc_log, 'interval', seconds=1200)
    #     scheduler.add_job(getblocklist.block_ctc_log, 'interval', seconds=1200)
    # else:
    #     scheduler.add_job(getblocklist.block_cmcc_log, 'interval', seconds=60)
    #     scheduler.add_job(getblocklist.block_cnc_log, 'interval', seconds=60)
    #     scheduler.add_job(getblocklist.block_ctc_log, 'interval', seconds=60)
    scheduler.start()
    tornado.ioloop.IOLoop.instance().start()


from optparse import OptionParser

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-p", "--port",
                      dest="port",
                      default=8000,
                      help="listen port")
    parser.add_option("-i", "--host",
                      dest="host",
                      default="0.0.0.0",
                      help="listen host")

    (options, args) = parser.parse_args()

    main(options.port, options.host)
