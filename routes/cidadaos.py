from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user
from werkzeug.security import generate_password_hash
from models import db, Cidadao
from utils import validar_cpf, formatar_cpf

cidadaos_bp = Blueprint('cidadaos', __name__)


@cidadaos_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        cpf = request.form.get('cpf', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        confirmar_senha = request.form.get('confirmar_senha', '')

        if not all([nome, cpf, email, senha, confirmar_senha]):
            flash('Todos os campos são obrigatórios', 'erro')
            return render_template('cadastro_cidadao.html')

        if senha != confirmar_senha:
            flash('As senhas não conferem', 'erro')
            return render_template('cadastro_cidadao.html')

        if len(senha) < 6:
            flash('A senha deve ter no mínimo 6 caracteres', 'erro')
            return render_template('cadastro_cidadao.html')

        if not validar_cpf(cpf):
            flash('CPF inválido', 'erro')
            return render_template('cadastro_cidadao.html')

        if Cidadao.query.filter_by(email=email).first():
            flash('E-mail já cadastrado', 'erro')
            return render_template('cadastro_cidadao.html')

        cpf_formatado = formatar_cpf(cpf)
        if Cidadao.query.filter_by(cpf=cpf_formatado).first():
            flash('CPF já cadastrado', 'erro')
            return render_template('cadastro_cidadao.html')

        novo = Cidadao(
            nome_completo=nome,
            cpf=cpf_formatado,
            email=email,
            senha_hash=generate_password_hash(senha)
        )
        db.session.add(novo)
        db.session.commit()
        login_user(novo, remember=True)
        return redirect(url_for('ocorrencias.listar_ocorrencias'))
    return render_template('cadastro_cidadao.html')
