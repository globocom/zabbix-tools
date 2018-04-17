def find_group_by_name(zabbix_api, name):
    groups = zabbix_api.hostgroup.get(filter={'name': str(name)})

    if len(groups) == 0:
        return []

    return groups[0]


def find_hosts_by_groupid(zapi, groupids, hostnames=None):
    if hostnames:
        hosts = zapi.host.get(output=['hostid', 'name'], groupids=groupids, filter={'host': hostnames})
    else:
        hosts = zapi.host.get(output=['hostid', 'name'], groupids=groupids)

    return hosts


def find_hosts_by_hostnames(zapi, hostnames):
    hosts = zapi.host.get(output=['hostid', 'name'], filter={'host': hostnames})

    return hosts


def mass_add_groups(zapi, groups, hosts):
    zapi.hostgroup.massadd(groups=groups, hosts=hosts)


def mass_remove_groups(zapi, groupids, hostids):
    zapi.hostgroup.massremove(groupids=groupids, hostids=hostids)