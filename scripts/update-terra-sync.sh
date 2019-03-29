#!/bin/bash -e
workdir=$(mktemp -d)
git clone https://git.code.sf.net/p/flightgear/flightgear $workdir
rm -rf ./vendor
mv $workdir/scripts/python/TerraSync ./vendor
mv $workdir/{AUTHORS,COPYING,Thanks,version} ./vendor
rm -rf $workdir
touch vendor/__init__.py
