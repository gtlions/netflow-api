#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''通过读取OS环境变量BGPAPI_ENV来动态加载配置文件
环境变量配置在/etc/profile
export BGPAPI_ENV='PROD'

如果有读取到该变量，则加载生产环境的配置[production]
如果没有读取到该变量，则加载开发环境的配置[development]
'''
import os

ENV = os.getenv('BGPAPPS_ENV')

# ENV = "DEBUG"

logger_name = "Apps@API"
if ENV == 'PROD':
    ENV = 'PROD'
    CONFIG_NAME = 'production'
    from .production import ProductionConfig as CONFIG
elif ENV == 'DEBUG':
    ENV = 'DEBUG'
    CONFIG_NAME = 'debug'
    from .debug import DebugConfig as CONFIG
elif ENV == 'DEV':
    ENV = 'DEV'
    CONFIG_NAME = 'development'
    from .development import DevelopmentConfig as CONFIG
else:
    ENV = 'DEV'
    CONFIG_NAME = 'development'
    from .development import DevelopmentConfig as CONFIG

config_banner = '!!!!!!!!!!  Check The ENV:[ ' + ENV + ' ]. Will Use The [ ' + CONFIG_NAME + ' ] Config.  !!!!!!!!!!'

if __name__ == "__main__":
    import os

    ENV = os.getenv('BGPAPI_ENV')
    print(ENV)
    if ENV == 'PROD':
        print('PROD')
    else:
        print('DEV')
