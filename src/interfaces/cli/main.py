# -*- coding: utf-8 -*-
import sys
import csv
from ferramentas.migrar_hosts_de_grupos import *
from interfaces import *


def menu():
    print ""
    print "--- Escolha uma opção do menu ---"
    print ""
    print "[0] - Listar processos"
    print "[1] - Novo processo"
    print "[2] - Nova etapa"
    print "[3] - Nova fase"
    print ""
    print "[4] - Sair"
    print ""

    menu_opcao()


def ler_arquivo(arquivo):
    arquivo = csv.reader(open(arquivo))
    lista_hosts = []

    for [host] in arquivo:
        lista_hosts.append(host)

    return lista_hosts


#def novo_processo(autor_processo, nome_processo, descricao_processo):
def novo_processo():
    print "Cadastrando um novo processo ..."
    print ""
    nome = raw_input("Nome: ")
    descricao = raw_input("Descrição: ")
    autor = raw_input("Email: ")

    processo = Processo(autor=autor)
    processo.nome = nome
    processo.descricao = descricao
    processo.save()

    print ""
    print "Processo cadastrado."
    raw_input("Pressione enter ...")
    menu()


def nova_etapa():
    print ""
    print "--- Nova etapa ---"
    print ""
    print "[0] - Adicionar novo grupo aos hosts"
    print "[1] - Remover grupo de hosts"
    print "[2] - Retornar ao menu principal"
    print ""

    opcao = raw_input("[+] - Selecione uma opção[0-1]: ")
    if opcao == '0':
        nome_processo = raw_input("Digite o nome do processo: ")
        processo = Processo.objects(nome=nome_processo).first()
        nome = raw_input("Digite o nome da etapa: ")
        descricao = raw_input("Digite a descrição da etapa: ")
        executor = raw_input("Digite o executor da etapa: ")
        grupo = raw_input("Digite o nome do novo grupo: ")
        nome_arquivo = raw_input("Digite o nome do arquivo de hosts: ")
        busca_hosts = ler_arquivo(nome_arquivo)

        hosts = base.find_hosts_by_hostnames(zapi, busca_hosts)
        group = base.find_group_by_name(zapi, grupo)
        etapa_adicionar_grupo(zapi, processo, hosts, nome, descricao, executor, group)

        raw_input("Pressione enter...")

        nova_etapa()
    elif opcao == '1':
        nome_processo = raw_input("Digite o nome do processo: ")
        processo = Processo.objects(nome=nome_processo).first()
        nome = raw_input("Digite o nome da etapa: ")
        descricao = raw_input("Digite a descrição da etapa: ")
        executor = raw_input("Digite o executor da etapa: ")
        grupo = raw_input("Digite o nome do grupo a ser removido: ")
        nome_arquivo = raw_input("Digite o nome do arquivo de hosts: ")
        busca_hosts = ler_arquivo(nome_arquivo)

        hosts = base.find_hosts_by_hostnames(zapi, busca_hosts)
        group = base.find_group_by_name(zapi, grupo)

        etapa_remover_grupo(zapi, processo, hosts, nome, descricao, executor, group)

        nova_etapa()
    elif opcao == '2':
        menu()
    else:
        sys.exit()


def listar_processos():
    processos = Processo.objects()
    print '{0:30} | {1:15} | {2:25}'.format("Data", "Nome", "Descrição")
    for processo in processos:
        print(str(processo.data_inicio), str(processo.nome), str(processo.descricao))


def menu_fase():
    nome_processo = raw_input("Digite o nome do processo: ")
    processo = Processo.objects(nome=nome_processo).firts()
    nome_etapa = raw_input("Digite o nome da etapa: ")
    etapa = Processo.objects(etapas=etapa.nome_etapa).first() #verificar essa linha na execucao
    novo_grupo = raw_input("Digite o nome do novo grupo: ")
    nome_arquivo = raw_input("Digite o nome do arquivo de hosts: ")
    busca_hosts = ler_arquivo(nome_arquivo)

    hosts = base.find_hosts_by_hostnames(zapi, busca_hosts)
    group = base.find_group_by_name(zapi, grupo)
    nova_fase_adicionar_grupo(zapi, processo, hosts, nome_etapa, group)


def menu_opcao():
    opcao = raw_input("[+] - Selecione uma opção[0-4]: ")
    if opcao == '0':
        listar_processos()
        raw_input("Pressione enter...")
        menu()
    elif opcao == '1':
        novo_processo()
    elif opcao == '2':
        nova_etapa()
    elif opcao == '3':
        menu_fase()
    elif opcao == '4':
        sys.exit()
    else:
        menu()


if __name__ == '__main__':
    conectar_mongoengine()
    zapi = conectar_zabbix()
    menu()
