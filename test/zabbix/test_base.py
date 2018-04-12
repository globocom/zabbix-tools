from unittest import TestCase

from mock import MagicMock
from pyzabbix import ZabbixAPI

from zabbix import base


class BaseTestCase(TestCase):

    def test_find_group_by_name(self):
        nome = 'grupo-1'
        ret = [{'internal': '0', 'flags': '0', 'groupid': '1', 'name': 'grupo-1'}]
        zapi = self.mock_zapi_hostgroup_get(ret)

        retorno = base.find_group_by_name(zapi, nome)

        self.assertEqual('grupo-1', retorno['name'])

    def test_find_group_by_name_deve_chamar_metodo_hostgroup_get_com_nome_grupo_como_parametro(self):
        nome = 'grupo-1'
        ret = [{'internal': '0', 'flags': '0', 'groupid': '1', 'name': 'grupo-1'}]
        zapi = self.mock_zapi_hostgroup_get(ret)

        retorno = base.find_group_by_name(zapi, nome)

        zapi.hostgroup.get.assert_called_with(filter={'name': str('grupo-1')})
        self.assertEqual('grupo-1', retorno['name'])

    def test_find_group_by_name_deve_chamar_metodo_hostgroup_get_com_nome_grupo_2_como_parametro(self):
        nome = 'grupo-2'
        ret = [{'internal': '0', 'flags': '0', 'groupid': '2', 'name': 'grupo-2'}]
        zapi = self.mock_zapi_hostgroup_get(ret)

        retorno = base.find_group_by_name(zapi, nome)

        zapi.hostgroup.get.assert_called_with(filter={'name': str('grupo-2')})
        self.assertEqual('grupo-2', retorno['name'])

    def test_find_group_by_name_grupo_nao_existe_deve_retornar_lista_de_hosts_vazia(self):
        nome = 'grupo-nao-existe'
        ret = []
        zapi = self.mock_zapi_hostgroup_get(ret)

        retorno = base.find_group_by_name(zapi, nome)

        self.assertEqual(0, len(retorno))

    def mock_zapi_hostgroup_get(self, ret):
        zapi = ZabbixAPI()
        config = {'get.return_value': ret}
        zapi.hostgroup = MagicMock(**config)
        return zapi