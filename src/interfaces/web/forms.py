# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, Email


class NovoProcessoForm(FlaskForm):
    nome = StringField(u'Nome', validators=[DataRequired()])
    descricao = StringField(u'Descrição', validators=[DataRequired()])
    email = StringField(u'Email', validators=[DataRequired(), Email()])
    salvar = SubmitField(u'Salvar')


class AdicionarGrupoHostsForm(FlaskForm):
    nome = StringField(u'Nome', validators=[DataRequired()])
    descricao = StringField(u'Descrição', validators=[DataRequired()])
    email = StringField(u'Email', validators=[DataRequired(), Email()])

    novo_grupo = StringField(u'Nome novo grupo', validators=[DataRequired()], id='novo_grupo_autocomplete')
    hosts = TextAreaField(validators=[DataRequired()])

    salvar = SubmitField(u'Salvar')


class NovaFaseForm(FlaskForm):
    email = StringField(u'Email', validators=[DataRequired(), Email()])
    hosts = TextAreaField(validators=[DataRequired()])

    salvar = SubmitField(u'Salvar')


class RemoverGrupoHostsForm(FlaskForm):
    nome = StringField(u'Nome', validators=[DataRequired()])
    descricao = StringField(u'Descrição', validators=[DataRequired()])
    email = StringField(u'Email', validators=[DataRequired(), Email()])

    grupo_removido = StringField('Nome do grupo a remover', validators=[DataRequired()], id='grupo_removido_autocomplete')
    hosts = TextAreaField(validators=[DataRequired()])

    salvar = SubmitField(u'Salvar')