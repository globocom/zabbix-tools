from controle.models.models import *
from mongoengine import *


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
    fase = Fase(objetos_afetados=objetos_afetados)
    etapa_faseada.fases.append(fase)
    processo.etapas.append(etapa_faseada)
    processo.save()


def adicionar_fase(processo, etapa_faseada, objetos_afetados):
    fase = Fase(objetos_afetados=objetos_afetados)
    etapa_faseada.fases.append(fase)
    processo.save()
