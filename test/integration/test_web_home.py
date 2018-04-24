# encoding=utf8
import os
from unittest import TestCase
import mock as mock
from controle.models.models import *
from interfaces.web import home
from zabbix import base


class TestWebHomeFunctionalTestCase(TestCase):

    class Scenario:

        def __init__(self, zapi):
            self.zapi = zapi
            self.groups = []

        def add_group(self, group_name):
            groupids = self.zapi.hostgroup.create({'name': group_name})
            groupids = groupids['groupids']
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
        home.app.testing = True
        home.app.config['WTF_CSRF_ENABLED'] = False
        self.app = home.app.test_client()
        mock.patch.dict(os.environ, {'ZABBIX_URL': 'http://127.0.0.1', 'ZABBIX_USER': 'Admin', 'ZABBIX_PASSWORD': 'zabbix'}).start()

        self.zapi = home.conectar_zabbix()
        self.scenario = TestWebHomeFunctionalTestCase.Scenario(zapi=self.zapi)

    def tearDown(self):
        Processo.drop_collection()
        Host.drop_collection()

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

    def test_novo_processo(self):
        nome_processo = 'processo-1'
        descricao_processo = 'descricao processo-1'
        autor_email = 'autor@processo-1.com'

        retorno = self.app.post('/inclusao/processo', data=dict(
            nome=nome_processo,
            descricao=descricao_processo,
            email=autor_email
        ), follow_redirects=True)

        self.assertTrue('Processo processo-1 criado com sucesso' in retorno.get_data())

        processo = Processo.objects.first()
        self.assertEqual('processo-1', processo.nome)
        self.assertEqual('descricao processo-1', processo.descricao)
        self.assertEqual('autor@processo-1.com', processo.autor)

    def test_novo_processo_campo_autor_deve_ser_email_valido(self):
        nome_processo = 'processo-1'
        descricao_processo = 'descricao processo-1'
        autor_email = 'autor processo-1'

        retorno = self.app.post('/inclusao/processo', data=dict(
            nome=nome_processo,
            descricao=descricao_processo,
            email=autor_email
        ), follow_redirects=True)

        self.assertFalse('Processo processo-1 criado com sucesso' in retorno.get_data())

        processo = Processo.objects.all()
        self.assertEqual(0, len(processo))

    def test_novo_processo_dois_processos_mesmo_nome_nao_deve_adicionar_segundo(self):
        nome_processo = 'processo-1'
        descricao_processo = 'descricao processo-1'
        autor_email = 'autor@processo-1.com'

        self.app.post('/inclusao/processo', data=dict(
            nome=nome_processo,
            descricao=descricao_processo,
            email=autor_email
        ), follow_redirects=True)

        retorno = self.app.post('/inclusao/processo', data=dict(
            nome=nome_processo,
            descricao=descricao_processo,
            email=autor_email
        ), follow_redirects=True)

        self.assertFalse('Processo processo-1 criado com sucesso' in retorno.get_data())
        self.assertTrue('Erro: já existe um processo com nome processo-1' in retorno.get_data())

        processos = Processo.objects.all()
        self.assertEqual(1, len(processos))

        processo = processos[0]
        self.assertEqual('processo-1', processo.nome)
        self.assertEqual('descricao processo-1', processo.descricao)
        self.assertEqual('autor@processo-1.com', processo.autor)

    def test_adicionar_grupo_hosts(self):
        group1 = self.scenario.add_group('grupo-1')
        group2 = self.scenario.add_group('grupo-2')
        self.scenario.add_host('host-1', [group1])
        self.scenario.add_host('host-2', [group1])

        nome_processo = 'processo-1'
        descricao_processo = 'descricao processo-1'
        autor_email = 'autor@processo-1.com'

        self.app.post('/inclusao/processo', data=dict(
            nome=nome_processo,
            descricao=descricao_processo,
            email=autor_email
        ), follow_redirects=True)

        nome_etapa = 'etapa-1'
        descricao_etapa = 'descricao etapa-1'
        executor_etapa = 'executor@etapa-1.com'
        novo_grupo = 'grupo-2'
        hosts = 'host-1, host-2'

        retorno = self.app.post('/inclusao/processo-1/etapa/adicionar_grupo_hosts', data=dict(
            nome=nome_etapa,
            descricao=descricao_etapa,
            email=executor_etapa,
            novo_grupo=novo_grupo,
            hosts=hosts
        ), follow_redirects=True)

        self.assertTrue('Etapa etapa-1 executada com sucesso' in retorno.get_data())

        processo = Processo.objects.first()
        self.assertEqual(1, len(processo.etapas))

        etapa = processo.etapas[0]
        self.assertEqual('etapa-1', etapa.nome)
        self.assertEqual('descricao etapa-1', etapa.descricao)
        self.assertEqual('executor@etapa-1.com', etapa.executor)

        atributo_modificado = etapa.atributo_modificado
        self.assertEqual('groups', atributo_modificado.nome)
        self.assertEqual('grupo-2', atributo_modificado.valor)

        self.assertEqual(2, len(etapa.objetos_afetados))
        objetos_afetados = [oa['nome'] for oa in etapa.objetos_afetados]
        self.assertTrue('host-1' in objetos_afetados)
        self.assertTrue('host-2' in objetos_afetados)

        zapi = home.conectar_zabbix()
        hosts = base.find_hosts_by_groupid(zapi, group2['groupid'])
        self.assertTrue(2, len(hosts))


    def test_adicionar_grupo_hosts_host_com_espaco_no_nome(self):
        group1 = self.scenario.add_group('grupo-1')
        group2 = self.scenario.add_group('grupo-2')
        self.scenario.add_host('host 1', [group1])

        nome_processo = 'processo-1'
        descricao_processo = 'descricao processo-1'
        autor_email = 'autor@processo-1.com'

        self.app.post('/inclusao/processo', data=dict(
            nome=nome_processo,
            descricao=descricao_processo,
            email=autor_email
        ), follow_redirects=True)

        nome_etapa = 'etapa-1'
        descricao_etapa = 'descricao etapa-1'
        executor_etapa = 'executor@etapa-1.com'
        novo_grupo = 'grupo-2'
        hosts = 'host 1'

        retorno = self.app.post('/inclusao/processo-1/etapa/adicionar_grupo_hosts', data=dict(
            nome=nome_etapa,
            descricao=descricao_etapa,
            email=executor_etapa,
            novo_grupo=novo_grupo,
            hosts=hosts
        ), follow_redirects=True)

        self.assertTrue('Etapa etapa-1 executada com sucesso' in retorno.get_data())

        processo = Processo.objects.first()

        etapa = processo.etapas[0]

        self.assertEqual(1, len(etapa.objetos_afetados))
        objetos_afetados = [oa['nome'] for oa in etapa.objetos_afetados]
        self.assertTrue('host 1' in objetos_afetados)

        zapi = home.conectar_zabbix()
        hosts = base.find_hosts_by_groupid(zapi, group2['groupid'])
        self.assertTrue(1, len(hosts))
        self.assertTrue('host 1', hosts[0]['name'])

