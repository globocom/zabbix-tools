#!/bin/sh

sh build.sh

export APP_SECRET_KEY=''
export DB_HOST=''
export DB_PORT=''
export DB_NAME=''
export DB_USER=''
export DB_PASSWORD=''
export ZABBIX_URL=http://127.0.0.1
export ZABBIX_USER=Admin
export ZABBIX_PASSWORD=zabbix

FLASK_APP=src/interfaces/web/home.py flask run
