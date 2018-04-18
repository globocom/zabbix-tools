from controle.gestor_controles import adicionar_host_controle
from zabbix import base
from controle import gestor_controles
from controle.models.models import *
from zabbix.base import find_group_by_name


def etapa_adicionar_grupo(zapi, processo, hosts, nome_etapa, descricao_etapa, executor_etapa, novo_grupo):
    adicionar_novo_grupo_aos_hosts(zapi, hosts, novo_grupo)

    adicionar_host_controle(hosts)

    hostnames = []
    for host in hosts:
        hostnames.append(host['name'])

    hosts_controle = Host.objects(nome__in=hostnames)
    atributo_modificado = AtributoIncluido(nome='groups', valor=novo_grupo['name'], id_atributo=novo_grupo['groupid'])

    gestor_controles.criar_etapa_faseada(processo, nome_etapa, descricao_etapa, executor_etapa, hosts_controle, atributo_modificado)

def etapa_remover_grupo(zapi, processo, hosts, nome_etapa, descricao_etapa, executor_etapa, grupo_removido):
    remover_grupo_dos_hosts(zapi, hosts, grupo_removido)

    adicionar_host_controle(hosts)

    hostnames = []
    for host in hosts:
        hostnames.append(host['name'])

    hosts_controle = Host.objects(nome__in=hostnames)
    atributo_modificado = AtributoExcluido(nome='groups', valor_anterior=grupo_removido['name'], id_atributo=grupo_removido['groupid'])

    gestor_controles.criar_etapa_faseada(processo, nome_etapa, descricao_etapa, executor_etapa, hosts_controle, atributo_modificado)


def nova_fase_adicionar_grupo(zapi, processo, etapa_faseada, executor, hosts):
    hostnames = []
    for host in hosts:
        hostnames.append(host['name'])

    adicionar_host_controle(hosts)
    hosts_controle = Host.objects(nome__in=hostnames)

    nome_novo_grupo = etapa_faseada.atributo_modificado.valor

    group = find_group_by_name(zapi, nome_novo_grupo)

    adicionar_novo_grupo_aos_hosts(zapi, hosts, group)

    gestor_controles.adicionar_fase(processo, etapa_faseada, executor=executor, objetos_afetados=hosts_controle)


def nova_fase_remover_grupo(zapi, processo, etapa_faseada, executor, hosts):
    hostnames = []
    for host in hosts:
        hostnames.append(host['name'])

    hosts_controle = Host.objects(nome__in=hostnames)

    nome_grupo_removido = etapa_faseada.atributo_modificado.valor_anterior

    group = find_group_by_name(zapi, nome_grupo_removido)

    remover_grupo_dos_hosts(zapi, hosts, group)

    gestor_controles.adicionar_fase(processo, etapa_faseada, executor=executor, objetos_afetados=hosts_controle)


def adicionar_novo_grupo_aos_hosts(zapi, hosts, novo_grupo):
    base.mass_add_groups(zapi=zapi, hosts=hosts, groups=novo_grupo)


def remover_grupo_dos_hosts(zapi, hosts, grupo_anterior):
    hostids = []
    for host in hosts:
        hostids.append(host['hostid'])

    base.mass_remove_groups(zapi=zapi, hostids=hostids, groupids=grupo_anterior['groupid'])