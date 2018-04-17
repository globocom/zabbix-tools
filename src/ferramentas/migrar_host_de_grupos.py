from controle.gestor_controles import adicionar_host_controle
from zabbix import base
from controle import gestor_controles
from controle.models.models import *


def etapa_adicionar_grupo(zapi, processo, hosts, nome_etapa, descricao_etapa, executor_etapa, novo_grupo):
    adicionar_novo_grupo_aos_hosts(zapi, hosts, novo_grupo)

    adicionar_host_controle(hosts)

    hostnames = []
    for host in hosts:
        hostnames.append(host['name'])

    hosts_controle = Host.objects(nome__in=hostnames)
    atributo_modificado = AtributoIncluido(nome='groups', valor=novo_grupo['name'], id_atributo=novo_grupo['groupid'])

    gestor_controles.criar_etapa_faseada(processo, nome_etapa, descricao_etapa, executor_etapa, hosts_controle, atributo_modificado)


def nova_fase_adicionar_grupo(zapi, processo, hosts, nome_etapa, novo_grupo):
    adicionar_novo_grupo_aos_hosts(zapi, hosts, novo_grupo)

    hostnames = []
    for host in hosts:
        hostnames.append(host['name'])

    hosts_controle = Host.objects(nome__in=hostnames)

    etapa_faseada = None
    for etapa in processo.etapas:
        if etapa.nome == nome_etapa:
            etapa_faseada = etapa
            break

    gestor_controles.adicionar_fase(processo, etapa_faseada, objetos_afetados=hosts_controle)


def adicionar_novo_grupo_aos_hosts(zapi, hosts, novo_grupo):
    base.mass_add_groups(zapi=zapi, hosts=hosts, groups=novo_grupo)


def remover_grupo_dos_hosts(zapi, hosts, grupo_anterior):
    hostids = []
    for host in hosts:
        hostids.append(host['hostid'])

    base.mass_remove_groups(zapi=zapi, hostids=hostids, groupids=grupo_anterior['groupid'])