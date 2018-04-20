#!/usr/bin/sh

sh build.sh

ZABBIX_URL=http://127.0.0.1 ZABBIX_USER=Admin ZABBIX_PASSWORD=zabbix FLASK_APP=src/interfaces/web/home.py flask run
