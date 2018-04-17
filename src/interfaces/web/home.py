# -*- coding: utf-8 -*-
from os import getenv

from flask import render_template, flash, redirect, url_for
from pyzabbix import ZabbixAPI
from controle.gestor_controles import criar_processo
from controle.models.models import *
from ferramentas.migrar_host_de_grupos import etapa_adicionar_grupo
from interfaces.web import create_app
from interfaces.web.forms import NovoProcessoForm, AdicionarGrupoHostsForm
from zabbix.base import find_hosts_by_hostnames, find_group_by_name

app = create_app()
app.app_context().push()

def conectar_zabbix():
    zabbix_url = getenv('ZABBIX_URL')
    zabbix_user = getenv('ZABBIX_USER') #'zbx'
    zabbix_password = getenv('ZABBIX_PASSWORD')

    zapi = ZabbixAPI(zabbix_url, timeout=600.0)
    zapi.login(zabbix_user, zabbix_password)
    return zapi


def conectar_mongoengine():
    if getenv('DB_HOST'):
        db_name = getenv('DB_NAME')
        db_host = getenv('DB_HOST')
        db_port = getenv('DB_PORT')
        db_user = getenv('DB_USER')
        db_password = getenv('DB_PASSWORD')

        connect(db=db_name, host=db_host, port=db_port, username=db_user, password=db_password)
    connect('dev')


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
        hostnames = form.hosts.data.splitlines()
        hostnames = [x.strip() for x in hostnames]
        hosts = find_hosts_by_hostnames(zapi, hostnames)

        group = find_group_by_name(zapi, form.novo_grupo.data)

        etapa_adicionar_grupo(zapi, processo, hosts, form.nome.data, form.descricao.data, form.email.data, group)
        flash('Etapa executada com sucesso'.format(processo.nome))
        return redirect(url_for('adicionar_grupo_hosts'))

    return render_template('adicionar_grupo_hosts.html', form=form)