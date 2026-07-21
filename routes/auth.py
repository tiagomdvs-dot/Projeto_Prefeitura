from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models import Cidadao, Funcionario

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    return render_template('login.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        cidadao = Cidadao.query.filter_by(email=email).first()
        if cidadao and check_password_hash(cidadao.senha_hash, senha):
            login_user(cidadao, remember=True)
            return redirect(url_for('ocorrencias.listar_ocorrencias'))
        flash('E-mail ou senha inválidos', 'erro')
    return render_template('login.html')


@auth_bp.route('/login/institucional', methods=['GET', 'POST'])
def login_institucional():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        funcionario = Funcionario.query.filter_by(email_institucional=email).first()
        if funcionario and funcionario.ativo and check_password_hash(funcionario.senha_hash, senha):
            login_user(funcionario, remember=True)
            if funcionario.setor == 'Administrador':
                return redirect(url_for('admin.painel_admin'))
            return redirect(url_for('funcionarios.painel_funcionario'))
        flash('E-mail ou senha inválidos', 'erro')
    return render_template('login_institucional.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/esqueci-senha')
def esqueci_senha():
    return render_template('esqueci_senha.html')
