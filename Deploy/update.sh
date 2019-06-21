#!/bin/bash
# clone last version from git, and restart api server.
export BGPAPI_HOME=/home/API/bgpapi
cd $BGPAPI_HOME
sh $BGPAPI_HOME/../stop_bgpapi.sh
cd $BGPAPI_HOME/../ && cp -r $BGPAPI_HOME $BGPAPI_HOME/../bakup/bgpapibak && tar -zcf $BGPAPI_HOME/../bakup/bgpapi_`date +%Y%m%d%H%M%S`.tar.gz $BGPAPI_HOME && rm -rf $BGPAPI_HOME && git clone -b master git@mgrser:root/bgpapi.git && rm -rf $BGPAPI_HOME/Doc $BGPAPI_HOME/Deploy $BGPAPI_HOME/apps/bgp_test.py && rm -rf $BGPAPI_HOME/../bakup/bgpapibak && sh $BGPAPI_HOME/../start_bgpapi.sh