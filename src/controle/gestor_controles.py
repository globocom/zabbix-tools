from controle.models.models import *
from mongoengine import *
import os

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')


def adicionar_host_controle(hosts):
    host_objects = []

    for host in hosts:
        host_objects.append(Host(nome=host['name'], id_objeto=host['hostid']))

    # https://github.com/MongoEngine/mongoengine/issues/1465
    try:
        Host.objects.insert(host_objects, write_concern={'continue_on_error': True})
    except NotUniqueError:
        pass


def criar_processo(nome, descricao, autor):
    return Processo(nome=nome, descricao=descricao, autor=autor).save()


def criar_etapa_simples(processo, nome, descricao, executor, objetos_afetados, atributo_modificado=None):
    etapa_simples = EtapaSimples(nome=nome, descricao=descricao, executor=executor,
                                 objetos_afetados=objetos_afetados, atributo_modificado=atributo_modificado)
    processo.etapas.append(etapa_simples)
    processo.save()

def criar_etapa_faseada(processo, nome, descricao, executor, objetos_afetados, atributo_modificado=None):
    etapa_faseada = EtapaFaseada(nome=nome, descricao=descricao, executor=executor, atributo_modificado=atributo_modificado)
    fase = Fase(objetos_afetados=objetos_afetados, executor=executor)
    etapa_faseada.fases.append(fase)
    processo.etapas.append(etapa_faseada)
    processo.save()

def adicionar_fase(processo, etapa_faseada, executor, objetos_afetados):
    fase = Fase(executor=executor, objetos_afetados=objetos_afetados)
    etapa_faseada.fases.append(fase)
    processo.save()

if __name__ == '__main__':
    connect(db=DB_NAME, host=DB_HOST, port=DB_PORT, username=DB_USER, password=DB_PASSWORD)

    criar_processo(nome='processo-1', descricao='descricao processo 1', autor='autor processo 1')
    adicionar_host_controle([{'name': 'host-2', 'hostid': '2'}])

    nome = 'etapa-1'
    descricao = 'descricao etapa 1'
    executor = 'executor etapa 1'
    processo = Processo.objects(nome='processo-1').first()
    objetos_afetados = Host.objects()

    atributo_incluido = AtributoIncluido(nome='groups', valor='grupo-1', id_atributo='1')

    criar_etapa_simples(processo=processo, nome=nome,
                                         descricao=descricao, executor=executor, objetos_afetados=objetos_afetados, atributo_modificado=atributo_incluido)