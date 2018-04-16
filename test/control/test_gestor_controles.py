from unittest import TestCase
import pytest

from controle.models.models import *
from controle import gestor_controles


class OpControlTestCase(TestCase):

    def setUp(self):
        self.client = connect('testdb', host='mongomock://localhost')

    def tearDown(self):
        #preciso dropar cada colecao por nao poder dropar o database, bug:
        #https: // github.com / mongomock / mongomock / issues / 233
        Processo.drop_collection()
        Host.drop_collection()

    def test_adicionar_host_controle(self):
        hosts = [{'name': 'host-1', 'hostid': '1'}]

        gestor_controles.adicionar_host_controle(hosts)

        host_retornado_bd = Host.objects.first()
        self.assertEqual('host-1', host_retornado_bd.nome)
        self.assertEqual('1', host_retornado_bd.id_objeto)

    def test_adicionar_host_controle_dois_hosts_mesmo_id(self):
        hosts = [{'name': 'host-2', 'hostid': '2'}]

        gestor_controles.adicionar_host_controle(hosts)
        gestor_controles.adicionar_host_controle(hosts)

        self.assertEqual(1, Host.objects.count())
        host_retornado_bd = Host.objects.first()
        self.assertEqual('host-2', host_retornado_bd.nome)
        self.assertEqual('2', host_retornado_bd.id_objeto)

    def test_criar_processo(self):
        nome = 'processo-1'
        descricao = 'descricao processo 1'
        autor = 'autor processo 1'

        gestor_controles.criar_processo(nome, descricao, autor)

        processo = Processo.objects(nome='processo-1').first()
        self.assertEqual('descricao processo 1', processo.descricao)
        self.assertEqual('autor processo 1', processo.autor)
        self.assertGreater(datetime.datetime.now(), processo.data_inicio)

    def test_criar_processo_dois_processos_mesmo_nome(self):
        nome = 'processo-1'
        descricao = 'descricao processo 1'
        autor = 'autor processo 1'

        gestor_controles.criar_processo(nome, descricao, autor)

        with pytest.raises(NotUniqueError):
            gestor_controles.criar_processo(nome, descricao, autor)

    def test_criar_etapa_simples(self):
        gestor_controles.criar_processo('processo-1', 'descricao processo 1', 'autor processo 1')
        gestor_controles.adicionar_host_controle([{'name': 'host-2', 'hostid': '2'}])

        nome = 'etapa-1'
        descricao = 'descricao etapa 1'
        executor = 'executor etapa 1'
        processo = Processo.objects.first()
        objetos_afetados = Host.objects()

        atributo_incluido = AtributoIncluido(nome='groups', valor='grupo-1', id_atributo='1')
        gestor_controles.criar_etapa_simples(processo=processo, nome=nome,
                                     descricao=descricao, executor=executor, objetos_afetados=objetos_afetados, atributo_modificado=atributo_incluido)

        processo_db = Processo.objects.first()
        self.assertEqual(1, processo_db.etapas.count())
        self.assertEqual('etapa-1', processo_db.etapas[0].nome)
        self.assertEqual('groups', processo_db.etapas[0].atributo_modificado.nome)

    def test_criar_etapa_faseada(self):
        gestor_controles.criar_processo('processo-1', 'descricao processo 1', 'autor processo 1')
        gestor_controles.adicionar_host_controle([{'name': 'host-2', 'hostid': '2'}])

        nome = 'etapa-1'
        descricao = 'descricao etapa 1'
        executor = 'executor etapa 1'
        processo = Processo.objects.first()

        objetos_afetados = Host.objects()
        atributo_incluido = AtributoIncluido(nome='groups', valor='grupo-1', id_atributo='1')
        gestor_controles.criar_etapa_faseada(processo=processo, nome=nome,
                                     descricao=descricao, executor=executor, objetos_afetados=objetos_afetados, atributo_modificado=atributo_incluido)

        processo_db = Processo.objects.first()
        self.assertEqual(1, processo_db.etapas.count())
        self.assertEqual('etapa-1', processo_db.etapas[0].nome)
        self.assertEqual('groups', processo_db.etapas[0].atributo_modificado.nome)
        todos_objetos_afetados_etapa = processo_db.etapas.first().objetos_afetados
        self.assertEqual(1, len(todos_objetos_afetados_etapa))

    def test_adicionar_fase(self):
        gestor_controles.criar_processo('processo-1', 'descricao processo 1', 'autor processo 1')
        gestor_controles.adicionar_host_controle([{'name': 'host-1', 'hostid': '1'}])
        gestor_controles.adicionar_host_controle([{'name': 'host-2', 'hostid': '2'}])

        nome = 'etapa-1'
        descricao = 'descricao etapa 1'
        executor = 'executor etapa 1'
        processo = Processo.objects.first()

        objetos_afetados = Host.objects(nome='host-1')
        objetos_afetados_etapa_2 = Host.objects(nome='host-2')

        gestor_controles.criar_etapa_faseada(processo=processo, nome=nome,
                                     descricao=descricao, executor=executor, objetos_afetados=objetos_afetados)

        processo = Processo.objects.first()
        etapa_faseada = processo.etapas.first()
        gestor_controles.adicionar_fase(processo, etapa_faseada, objetos_afetados_etapa_2)

        processo_db = Processo.objects.first()
        self.assertEqual(1, processo_db.etapas.count())
        todos_objetos_afetados_etapa = processo_db.etapas.first().objetos_afetados
        self.assertEqual(2, len(todos_objetos_afetados_etapa))