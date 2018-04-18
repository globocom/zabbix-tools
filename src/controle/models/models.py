import datetime

from mongoengine import *


class AtributoModificado(EmbeddedDocument):
    nome = StringField(required=True, choices=('groups'))

    meta = {'allow_inheritance': True}


class AtributoIncluido(AtributoModificado):
    valor = StringField(required=True)
    id_atributo = StringField()


class AtributoExcluido(AtributoModificado):
    valor_anterior = StringField(required=True)
    id_atributo = StringField()


class AtributoAtualizado(AtributoModificado):
    valor_anterior = StringField(required=True)
    id_atributo_anterior = StringField()
    novo_valor = StringField(required=True)
    id_novo_atributo = StringField()


class Objeto(Document):
    nome = StringField(required=True)
    id_objeto = StringField(required=True, unique=True)

    meta = {'allow_inheritance': True}


class Etapa(EmbeddedDocument):
    TIPOS_OPERACAO = ('ADICIONAR_GRUPO_HOSTS', 'REMOVER_GRUPO_HOSTS')


    executor = StringField(required=True)
    data_execucao = DateTimeField(default=datetime.datetime.now())
    nome = StringField(required=True)
    descricao = StringField(required=True)
    atributo_modificado = EmbeddedDocumentField(AtributoModificado)
    executado = BooleanField(default=False)
    operacao = StringField(choices=TIPOS_OPERACAO)

    meta = {'ordering': ['data_execucao'], 'allow_inheritance': True}


class EtapaSimples(Etapa):
    objetos_afetados = ListField(ReferenceField(Objeto), required=True)


class Fase(EmbeddedDocument):
    objetos_afetados = ListField(ReferenceField(Objeto), required=True)
    data_execucao = DateTimeField(default=datetime.datetime.now())
    executor = StringField(required=True)

class EtapaFaseada(Etapa):
    fases = EmbeddedDocumentListField(Fase)

    @property
    def objetos_afetados(self):
        objetos_afetados = []
        for fase in self.fases:
            objetos_afetados.extend(fase.objetos_afetados)
        return objetos_afetados


class Host(Objeto):
    pass


class Processo(Document):
    autor = StringField(required=True)
    data_inicio = DateTimeField(default=datetime.datetime.now())
    nome = StringField(required=True, unique=True)
    descricao = StringField(required=True)
    etapas = EmbeddedDocumentListField(Etapa)

    meta = {'ordering': ['-data_inicio']}
