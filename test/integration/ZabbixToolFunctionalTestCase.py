from unittest import TestCase
from mongoengine import connect
from pyzabbix import ZabbixAPI


def conectar_zabbix():
    zabbix_url = 'http://127.0.0.1'
    zabbix_user = 'Admin'
    zabbix_password = 'zabbix'

    zapi = ZabbixAPI(zabbix_url, timeout=600.0)
    zapi.login(zabbix_user, zabbix_password)

    return zapi


class ZabbixToolFunctionalTestCase(TestCase):
    class Scenario:
        groups = []

        def __init__(self, zapi):
            self.zapi = zapi

        def add_group(self, group_name):
            groupids = self.zapi.hostgroup.create({'name': group_name})
            groupids= groupids['groupids']
            group = self.zapi.hostgroup.get(groupids=groupids)
            group = group[0]
            self.groups.append(group)
            return group

        def add_host(self, host_name, groups):
            interface = {
                "type": 1,
                "main": 1,
                "useip": 1,
                "ip": "127.0.0.1",
                "dns": "",
                "port": "10050"
            }
            self.zapi.host.create({'host': host_name, 'groups': groups, 'interfaces': [interface]})

    def setUp(self):
        self.db = connect('integration')
        self.zapi = conectar_zabbix()
        self.scenario = ZabbixToolFunctionalTestCase.Scenario(zapi=self.zapi)

    def tearDown(self):
        self.db.drop_database('integration')
        groupids = [g['groupid'] for g in self.scenario.groups]
        hostids = [h['hostid'] for h in self.zapi.host.get(groupids=groupids)]

        if hostids:
            self.zapi.host.delete(*hostids)
        if groupids:
            self.zapi.hostgroup.delete(*groupids)

        group = self.zapi.hostgroup.get(filter={'name': 'g1'})
        self.assertEqual(0, len(group))

        hosts = self.zapi.host.get(groupids=groupids)
        self.assertEqual(0, len(hosts))

    def test_must_create(self):
        group = self.scenario.add_group(group_name='g1')
        group2 = self.scenario.add_group(group_name='g2')
        self.scenario.add_host(host_name='h1', groups=[group])
        self.scenario.add_host(host_name='h2', groups=[group])
        self.scenario.add_host(host_name='h3', groups=[group2])

        groups = self.zapi.hostgroup.get(filter={'name': ['g1', 'g2']})
        self.assertEqual(2, len(groups))
        hosts = self.zapi.host.get(groupids=[group['groupid'], group2['groupid']])
        self.assertEqual(3, len(hosts))
