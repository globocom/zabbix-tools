def find_group_by_name(zabbix_api, nome):
    grupos = zabbix_api.hostgroup.get(filter={'name': str(nome)})

    if len(grupos) == 0:
        return []

    return grupos[0]


if __name__ == '__main__':
    from pyzabbix import ZabbixAPI
    zapi = ZabbixAPI(server='https://zabbix.staging.globoi.com', timeout=600)
    zapi.login('zbx','globocom')
    find_group_by_name(zapi, '1-zabbix-support-test')