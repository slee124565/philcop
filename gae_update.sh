#!/bin/bash -x

version=server

if [ -z $1 ]; then
	version=staging
else
	version=$1
fi

appcfg.py -A trusty-catbird-645 --no_cookies -V $version update . 
