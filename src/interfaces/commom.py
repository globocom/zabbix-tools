from pyzabbix import ZabbixAPI
from os import getenv

from mongoengine import connect


def conectar_zabbix():
    zabbix_url = getenv('ZABBIX_URL')
    zabbix_user = getenv('ZABBIX_USER')
    zabbix_password = getenv('ZABBIX_PASSWORD')

    zapi = ZabbixAPI(zabbix_url, timeout=600.0)
    zapi.login(zabbix_user, zabbix_password)
    return zapi


def conectar_mongoengine():
    if getenv('DB_HOST'):
        db_name = getenv('DB_NAME')
        db_host = getenv('DB_HOST')
        db_port = getenv('DB_PORT')
        db_user = getenv('DB_USER')
        db_password = getenv('DB_PASSWORD')

        connect(db=db_name, host=db_host, port=db_port, username=db_user, password=db_password)
    else:
        connect('dev')