#!/usr/bin/sh

docker-compose -f docker-compose-ci.yml up -d

python setup.py install
pip install -r web-requirements.txt

ZABBIX_URL=http://127.0.0.1 ZABBIX_USER=Admin ZABBIX_PASSWORD=zabbix FLASK_APP=src/interfaces/web/home.py flask run
