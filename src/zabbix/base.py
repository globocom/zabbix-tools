def find_group_by_name(zabbix_api, name):
    groups = zabbix_api.hostgroup.get(filter={'name': str(name)})

    if len(groups) == 0:
        return []

    return groups[0]


def find_hosts_by_groupid(zapi, groupids):
    hosts = zapi.host.get(output=['hostid', 'name'], groupids=groupids)

    return hosts
