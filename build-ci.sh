#!/usr/bin/sh

sh build.sh

docker-compose -f docker-compose-ci.yml up -d

python setup.py test