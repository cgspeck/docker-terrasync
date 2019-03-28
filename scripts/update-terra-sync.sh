#!/bin/bash -e
workdir=$(mktemp -d)
git clone https://git.code.sf.net/p/flightgear/flightgear $workdir
mv $workdir/scripts/python/TerraSync ./vendor
mv $workdir/{AUTHORS,COPYING,Thanks,version} ./vendor
rm -rf $workdir
