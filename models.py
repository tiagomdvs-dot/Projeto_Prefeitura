from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import re

db = SQLAlchemy()

class Cidadao(UserMixin, db.Model):
    __tablename__ = 'cidadaos'
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    ocorrencias = db.relationship('Ocorrencia', backref='cidadao', lazy=True)
    avaliacoes = db.relationship('Avaliacao', backref='cidadao', lazy=True)
    notificacoes = db.relationship('Notificacao', backref='cidadao', lazy=True)

    def get_id(self):
        return f'c_{self.id}'


class Funcionario(UserMixin, db.Model):
    __tablename__ = 'funcionarios'
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(255), nullable=False)
    email_institucional = db.Column(db.String(255), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    setor = db.Column(db.String(100), nullable=False)
    ativo = db.Column(db.Boolean, default=True)

    atualizacoes = db.relationship('AtualizacaoOcorrencia', backref='funcionario', lazy=True, cascade='all, delete-orphan')

    def get_id(self):
        return f'f_{self.id}'


class Ocorrencia(db.Model):
    __tablename__ = 'ocorrencias'
    id = db.Column(db.Integer, primary_key=True)
    protocolo = db.Column(db.String(20), unique=True, nullable=False)
    cidadao_id = db.Column(db.Integer, db.ForeignKey('cidadaos.id'), nullable=True)
    tipo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    localizacao = db.Column(db.String(255), nullable=False)
    bairro = db.Column(db.String(100), nullable=False, default='Centro')
    foto = db.Column(db.Text, nullable=True)
    foto_mime = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='aberta')
    data_abertura = db.Column(db.DateTime, default=datetime.utcnow)
    data_conclusao = db.Column(db.DateTime, nullable=True)
    equipe = db.Column(db.String(100), nullable=True)

    atualizacoes = db.relationship('AtualizacaoOcorrencia', backref='ocorrencia', lazy=True, cascade='all, delete-orphan')
    avaliacao = db.relationship('Avaliacao', backref='ocorrencia', uselist=False, lazy=True, cascade='all, delete-orphan')


class AtualizacaoOcorrencia(db.Model):
    __tablename__ = 'atualizacoes_ocorrencias'
    id = db.Column(db.Integer, primary_key=True)
    ocorrencia_id = db.Column(db.Integer, db.ForeignKey('ocorrencias.id'), nullable=False)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'), nullable=False)
    observacao = db.Column(db.Text, nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)
    notificar_cidadao = db.Column(db.Boolean, default=True)


class Avaliacao(db.Model):
    __tablename__ = 'avaliacoes'
    id = db.Column(db.Integer, primary_key=True)
    ocorrencia_id = db.Column(db.Integer, db.ForeignKey('ocorrencias.id'), nullable=False)
    cidadao_id = db.Column(db.Integer, db.ForeignKey('cidadaos.id'), nullable=False)
    nota = db.Column(db.Integer, nullable=False)
    data_avaliacao = db.Column(db.DateTime, default=datetime.utcnow)


class Notificacao(db.Model):
    __tablename__ = 'notificacoes'
    id = db.Column(db.Integer, primary_key=True)
    cidadao_id = db.Column(db.Integer, db.ForeignKey('cidadaos.id'), nullable=True)
    ocorrencia_id = db.Column(db.Integer, db.ForeignKey('ocorrencias.id'), nullable=True)
    mensagem = db.Column(db.Text, nullable=False)
    lida = db.Column(db.Boolean, default=False)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)
