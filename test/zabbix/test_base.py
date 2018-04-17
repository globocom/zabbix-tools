from unittest import TestCase

from mock import MagicMock

from zabbix import base


class BaseTestCase(TestCase):

    class Scenario:

        def __init__(self):
            self.zapi = MagicMock()
            self.name_groups = dict()
            self.groupid_groups = dict()
            self.group_hosts = dict()

        def group_side_effect(self, filter):
            if filter['name'] not in self.name_groups:
                return []
            return self.name_groups[filter['name']]

        def host_side_effect(self, output, groupids, filter=None):
            if filter:
                hosts = self.host_side_effect_with_filter(filter, groupids)
            else:
                hosts = self.host_side_effect_without_filter(groupids)

            return hosts

        def host_side_effect_with_filter(self, filter, groupids):
            hosts = []
            hostnames = filter['host']
            if type(groupids) is list:
                for groupid in groupids:
                    if groupids in self.group_hosts:
                        for host in self.group_hosts[groupid]:
                            if host['name'] in hostnames:
                                hosts.append(host)
            else:
                if groupids in self.group_hosts:
                    for host in self.group_hosts[groupids]:
                        if host['name'] in hostnames:
                            hosts.append(host)

            return hosts

        def host_side_effect_without_filter(self, groupids):
            hosts = []
            if type(groupids) is list:
                for groupid in groupids:
                    if groupids in self.group_hosts:
                        hosts.extend(self.group_hosts[groupid])
            else:
                if groupids in self.group_hosts:
                    hosts.extend(self.group_hosts[groupids])

            return hosts

        def add_group(self, groupid, name):
            self.name_groups[name] = [{'groupid': str(groupid), 'name': name}]
            self.groupid_groups[groupid] = [{'groupid': groupid, 'name': name}]
            config = {'get.side_effect': self.group_side_effect}
            self.zapi.hostgroup = MagicMock(**config)

        def add_host(self, hostid, name, groups):
            host = {'hostid': str(hostid), 'name': name}
            for group in groups:
                if group not in self.groupid_groups.keys():
                    raise KeyError('Inconsistent scenario: group {} not exists'.format(group))

                if group not in self.group_hosts:
                    self.group_hosts[group] = []

                self.group_hosts[group].append(host)

            config = {'get.side_effect': self.host_side_effect}
            self.zapi.host = MagicMock(**config)

    def __init__(self, *args, **kwargs):
        super(BaseTestCase, self).__init__(*args, **kwargs)
        self.scenario = self.Scenario()

    def test_find_group_by_name(self):
        self.scenario.add_group(groupid=1, name='grupo_1')

        nome = 'grupo_1'
        zapi = self.scenario.zapi

        retorno = base.find_group_by_name(zapi, nome)

        self.assertEqual('grupo_1', retorno['name'])

    def test_find_group_by_name_deve_chamar_metodo_hostgroup_get_com_nome_grupo_como_parametro(self):
        self.scenario.add_group(groupid=1, name='grupo_1')

        nome = 'grupo_1'
        zapi = self.scenario.zapi

        retorno = base.find_group_by_name(zapi, nome)

        zapi.hostgroup.get.assert_called_with(filter={'name': str('grupo_1')})
        self.assertEqual('grupo_1', retorno['name'])

    def test_find_group_by_name_deve_chamar_metodo_hostgroup_get_com_nome_grupo_2_como_parametro(self):
        self.scenario.add_group(groupid=2, name='grupo_2')

        zapi = self.scenario.zapi
        nome = 'grupo_2'

        retorno = base.find_group_by_name(zapi, nome)

        zapi.hostgroup.get.assert_called_with(filter={'name': str('grupo_2')})
        self.assertEqual('grupo_2', retorno['name'])

    def test_find_group_by_name_grupo_nao_existe_deve_retornar_lista_de_hosts_vazia(self):
        self.scenario.add_group(groupid=1, name='grupo_1')

        nome = 'grupo-nao-existe'
        zapi = self.scenario.zapi

        retorno = base.find_group_by_name(zapi, nome)

        self.assertEqual(0, len(retorno))

    def test_find_hosts_by_group_id_deve_chamar_metodo_host_get_com_id_grupo_como_parametro(self):
        self.scenario.add_group(groupid=629, name='grupo_629')
        self.scenario.add_host(hostid=1, name='host-1', groups=[629])

        id_grupo = 629
        zapi = self.scenario.zapi

        base.find_hosts_by_groupid(zapi, id_grupo)

        zapi.host.get.assert_called_with(output=['hostid', 'name'], groupids=629)

    def test_find_hosts_by_group_id_deve_chamar_metodo_host_get_com_id_grupo_como_parametro_2(self):
        self.scenario.add_group(groupid=300, name='grupo_300')
        self.scenario.add_host(hostid=2, name='host-2', groups=[300])

        id_grupo = 300
        zapi = self.scenario.zapi

        base.find_hosts_by_groupid(zapi, id_grupo)

        zapi.host.get.assert_called_with(output=['hostid', 'name'], groupids=300)

    def test_find_hosts_by_group_id_deve_chamar_metodo_host_get_com_id_grupo_como_parametro_3(self):
        self.scenario.add_group(groupid=500, name='grupo_500')
        self.scenario.add_host(hostid=3, name='host-3', groups=[500])

        id_grupo = 500
        zapi = self.scenario.zapi

        base.find_hosts_by_groupid(zapi, id_grupo)

        zapi.host.get.assert_called_with(output=['hostid', 'name'], groupids=500)

    def test_find_hosts_by_group_deve_retornar_hosts(self):
        self.scenario.add_group(groupid=1, name='grupo_1')
        self.scenario.add_host(hostid=4, name='host-4', groups=[1])

        id_grupo = 1
        zapi = self.scenario.zapi

        retorno = base.find_hosts_by_groupid(zapi, id_grupo)

        self.assertEqual([{'name': 'host-4', 'hostid': '4'}], retorno)

    def test_find_hosts_by_group_e_nome(self):
        self.scenario.add_group(groupid=1, name='grupo_1')
        self.scenario.add_host(hostid=4, name='host-4', groups=[1])
        self.scenario.add_host(hostid=5, name='host-5', groups=[1])

        id_grupo = 1
        zapi = self.scenario.zapi

        retorno = base.find_hosts_by_groupid(zapi, id_grupo, ['host-4'])

        self.assertEqual([{'name': 'host-4', 'hostid': '4'}], retorno)
        zapi.host.get.assert_called_with(output=['hostid', 'name'], groupids=1, filter={'host': ['host-4']})

    def test_find_hosts_by_group_nenhum_host_no_grupo(self):
        self.scenario.add_group(groupid=1, name='grupo_1')
        self.scenario.add_group(groupid=2, name='grupo_2')
        self.scenario.add_host(hostid='1', name='host-1', groups=[1])

        id_grupo = 2
        zapi = self.scenario.zapi

        retorno = base.find_hosts_by_groupid(zapi, id_grupo)

        self.assertEqual([], retorno)
