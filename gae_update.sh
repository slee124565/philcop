#!/bin/bash -x

version=server

if [ -z $1 ]; then
	version=staging
else
	version=$1
fi

gcloud app deploy -v $version app.yaml
