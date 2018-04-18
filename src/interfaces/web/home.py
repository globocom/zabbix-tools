# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for
from controle.gestor_controles import criar_processo
from controle.models.models import *
from ferramentas.migrar_hosts_de_grupos import etapa_adicionar_grupo, etapa_remover_grupo, nova_fase_adicionar_grupo, \
    nova_fase_remover_grupo
from interfaces import *
from interfaces.web import create_app
from interfaces.web.forms import NovoProcessoForm, AdicionarGrupoHostsForm, RemoverGrupoHostsForm, NovaFaseForm
from zabbix.base import find_hosts_by_hostnames, find_group_by_name

app = create_app()
app.app_context().push()

@app.before_first_request
def setup():
    conectar_mongoengine()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/processo')
def processo():
    processos = Processo.objects.all()
    return render_template('processo.html', processos=processos)


@app.route('/inclusao/processo', methods=['GET', 'POST'])
def novo_processo():
    form = NovoProcessoForm()
    if form.validate_on_submit():
        nome = form.nome.data
        descricao = form.descricao.data
        autor = form.email.data

        processo = criar_processo(nome=nome, descricao=descricao, autor=autor)

        flash('Processo {} criado com sucesso'.format(processo.nome))

        return redirect(url_for('novo_processo'))

    return render_template('novo_processo.html', form=form)


@app.route('/inclusao/etapa')
def nova_etapa():
    operacoes = ('adicionar_grupo_hosts', 'remover_grupo_hosts')
    return render_template('nova_etapa.html', operacoes=operacoes)


@app.route('/inclusao/etapa/adicionar_grupo_hosts', methods=['GET', 'POST'])
def adicionar_grupo_hosts():
    form = AdicionarGrupoHostsForm()

    if form.validate_on_submit():
        zapi = conectar_zabbix()
        processo = Processo.objects(nome=form.nome_processo.data).first()
        hosts = find_hosts_by_hostnames(zapi, converter_texto_lista_hosts(form.hosts.data))
        group = find_group_by_name(zapi, form.novo_grupo.data)

        nome_etapa = form.nome.data
        descricao = form.descricao.data
        executor_etapa = form.email.data
        novo_grupo = group

        etapa_adicionar_grupo(zapi=zapi, processo=processo, hosts=hosts, nome_etapa=nome_etapa,
                              descricao_etapa=descricao, executor_etapa=executor_etapa, novo_grupo=novo_grupo)

        flash('Etapa executada com sucesso'.format(processo.nome))

        return redirect(url_for('adicionar_grupo_hosts'))

    return render_template('etapa_adicionar_grupo_hosts.html', form=form)


@app.route('/inclusao/etapa/remover_grupo_hosts', methods=['GET', 'POST'])
def remover_grupo_hosts():
    form = RemoverGrupoHostsForm()

    if form.validate_on_submit():
        zapi = conectar_zabbix()
        processo = Processo.objects(nome=form.nome_processo.data).first()
        hosts = find_hosts_by_hostnames(zapi, converter_texto_lista_hosts(form.hosts.data))
        group = find_group_by_name(zapi, form.grupo_removido.data)

        nome_etapa = form.nome.data
        descricao = form.descricao.data
        executor = form.email.data
        grupo_removido = group

        etapa_remover_grupo(zapi=zapi, processo=processo, hosts=hosts, nome_etapa=nome_etapa, descricao_etapa=descricao,
                            executor_etapa=executor, grupo_removido=grupo_removido)

        flash('Etapa executada com sucesso'.format(processo.nome))

        return redirect(url_for('remover_grupo_hosts'))

    return render_template('etapa_remover_grupo_hosts.html', form=form)


@app.route('/processo/etapas/<nome_processo>')
def etapas(nome_processo):

    processo = Processo.objects(nome = nome_processo).first()

    return render_template('etapas.html', processo=processo, etapas=processo.etapas)


@app.route('/processo/etapas/<nome_processo>/<nome_etapa>/detalhes')
def detalhe_etapa(nome_processo, nome_etapa):
    processo = Processo.objects(nome=nome_processo).first()

    etapa = None
    for etapa in processo.etapas:
        if etapa.nome == nome_etapa:
            etapa = etapa
            break

    return render_template('detalhe_etapa.html', etapa=etapa)


@app.route('/inclusao/fase', methods=['GET', 'POST'])
def nova_fase():
    form = NovaFaseForm()

    if form.validate_on_submit():
        zapi = conectar_zabbix()
        processo = Processo.objects(nome=form.nome_processo.data).first()

        nome_etapa = form.nome_etapa.data

        hosts = find_hosts_by_hostnames(zapi, converter_texto_lista_hosts(form.hosts.data))

        executor = form.email.data

        etapa_faseada = None
        for etapa in processo.etapas:
            if etapa.nome == nome_etapa:
                etapa_faseada = etapa
                break

        if etapa.atributo_modificado._cls == 'AtributoIncluido':
            nova_fase_adicionar_grupo(zapi=zapi, processo=processo, executor=executor, hosts=hosts, etapa_faseada=etapa_faseada)

        elif etapa.atributo_modificado._cls == 'AtributoExcluido':
            nova_fase_remover_grupo(zapi=zapi, processo=processo, executor=executor, hosts=hosts,
                                      etapa_faseada=etapa_faseada)

        flash('Fase executada com sucesso'.format(processo.nome))

        return redirect(url_for('nova_fase'))

    return render_template('nova_fase.html', form=form)


def converter_texto_lista_hosts(hostnames):
    hostnames = hostnames.replace(',', '\n')
    hostnames = hostnames.splitlines()
    hostnames = [x.strip() for x in hostnames]
    return hostnames