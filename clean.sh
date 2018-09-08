#!/bin/bash

cd $(dirname ${0})
rm -rf OpsworksTool.egg-info/ build/ dist/
find . -name .ropeproject -type d | xargs rm -rf
find . -name "*.pyc" -type f | xargs rm -f
