# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for
from controle.gestor_controles import criar_processo
from controle.models.models import *
from ferramentas.migrar_hosts_de_grupos import etapa_adicionar_grupo, etapa_remover_grupo
from interfaces import *
from interfaces.web import create_app
from interfaces.web.forms import NovoProcessoForm, AdicionarGrupoHostsForm, RemoverGrupoHostsForm
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
        processo = criar_processo(form.nome.data, form.descricao.data, form.email.data)
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

        etapa_adicionar_grupo(zapi, processo, hosts, form.nome.data, form.descricao.data, form.email.data, group)

        flash('Etapa executada com sucesso'.format(processo.nome))

        return redirect(url_for('adicionar_grupo_hosts'))

    return render_template('adicionar_grupo_hosts.html', form=form)

@app.route('/inclusao/etapa/remover_grupo_hosts', methods=['GET', 'POST'])
def remover_grupo_hosts():
    form = RemoverGrupoHostsForm()

    if form.validate_on_submit():
        zapi = conectar_zabbix()
        processo = Processo.objects(nome=form.nome_processo.data).first()
        hosts = find_hosts_by_hostnames(zapi, converter_texto_lista_hosts(form.hosts.data))
        group = find_group_by_name(zapi, form.grupo_removido.data)

        etapa_remover_grupo(zapi, processo, hosts, form.nome.data, form.descricao.data, form.email.data, group)

        flash('Etapa executada com sucesso'.format(processo.nome))

        return redirect(url_for('remover_grupo_hosts'))

    return render_template('remover_grupo_hosts.html', form=form)


def converter_texto_lista_hosts(hostnames):
    hostnames = hostnames.replace(',', '')
    hostnames = hostnames.replace(';', '')
    hostnames = hostnames.splitlines()
    hostnames = [x.strip() for x in hostnames]
    return hostnames