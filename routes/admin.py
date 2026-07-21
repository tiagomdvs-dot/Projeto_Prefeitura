from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from models import db, Funcionario, Ocorrencia
from utils import validar_email_institucional, gerar_senha_temporaria
from sqlalchemy import func, extract

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/painel')
@login_required
def painel_admin():
    if not hasattr(current_user, 'setor') or current_user.setor != 'Administrador':
        return redirect(url_for('auth.login_institucional'))
    funcionarios = Funcionario.query.all()
    bairro_filtro = request.args.get('bairro', '').strip()
    mes_filtro = request.args.get('mes', '')
    ocorrencias_query = Ocorrencia.query
    if bairro_filtro:
        ocorrencias_query = ocorrencias_query.filter(Ocorrencia.bairro.ilike(f'%{bairro_filtro}%'))
    if mes_filtro:
        ano, mes = mes_filtro.split('-')
        ocorrencias_query = ocorrencias_query.filter(
            extract('year', Ocorrencia.data_abertura) == int(ano),
            extract('month', Ocorrencia.data_abertura) == int(mes)
        )
    ocorrencias = ocorrencias_query.order_by(Ocorrencia.data_abertura.desc()).all()
    bairros = db.session.query(Ocorrencia.bairro).distinct().order_by(Ocorrencia.bairro).all()
    bairros = [b[0] for b in bairros]

    stats_query = db.session.query(
        Ocorrencia.bairro,
        Ocorrencia.tipo,
        func.count(Ocorrencia.id).label('total')
    )
    if mes_filtro:
        ano, mes = mes_filtro.split('-')
        stats_query = stats_query.filter(
            extract('year', Ocorrencia.data_abertura) == int(ano),
            extract('month', Ocorrencia.data_abertura) == int(mes)
        )
    stats = stats_query.group_by(Ocorrencia.bairro, Ocorrencia.tipo).order_by(func.count(Ocorrencia.id).desc()).all()

    return render_template('painel_admin.html', funcionarios=funcionarios, ocorrencias=ocorrencias, bairros=bairros, bairro_filtro=bairro_filtro, stats=stats, mes_filtro=mes_filtro)


@admin_bp.route('/admin/funcionarios/cadastrar', methods=['POST'])
@login_required
def cadastrar_funcionario():
    if not hasattr(current_user, 'setor') or current_user.setor != 'Administrador':
        return redirect(url_for('auth.login_institucional'))
    nome = request.form.get('nome', '').strip()
    email = request.form.get('email', '').strip()
    setor = request.form.get('setor', '').strip()

    if not all([nome, email, setor]):
        flash('Todos os campos são obrigatórios', 'erro')
        return redirect(url_for('admin.painel_admin'))

    from utils import validar_email_institucional
    if not validar_email_institucional(email):
        flash('E-mail institucional inválido. Use o formato nome@picos.pi.gov.br', 'erro')
        return redirect(url_for('admin.painel_admin'))

    if Funcionario.query.filter_by(email_institucional=email).first():
        flash('E-mail institucional já cadastrado', 'erro')
        return redirect(url_for('admin.painel_admin'))

    from utils import gerar_senha_temporaria
    from werkzeug.security import generate_password_hash
    senha_temp = gerar_senha_temporaria()
    funcionario = Funcionario(
        nome_completo=nome,
        email_institucional=email,
        senha_hash=generate_password_hash(senha_temp),
        setor=setor
    )
    db.session.add(funcionario)
    db.session.commit()

    flash(f'Funcionário cadastrado! Senha temporária: {senha_temp} (enviar para {email})', 'sucesso')
    return redirect(url_for('admin.painel_admin'))


@admin_bp.route('/admin/funcionarios/<int:funcionario_id>/editar', methods=['POST'])
@login_required
def editar_funcionario(funcionario_id):
    if not hasattr(current_user, 'setor') or current_user.setor != 'Administrador':
        return redirect(url_for('auth.login_institucional'))
    funcionario = Funcionario.query.get_or_404(funcionario_id)
    nome = request.form.get('nome', '').strip()
    email = request.form.get('email', '').strip()
    setor = request.form.get('setor', '').strip()
    nova_senha = request.form.get('senha', '').strip()

    if not all([nome, email, setor]):
        flash('Todos os campos são obrigatórios', 'erro')
        return redirect(url_for('admin.painel_admin'))

    if not validar_email_institucional(email):
        flash('E-mail institucional inválido. Use o formato nome@picos.pi.gov.br', 'erro')
        return redirect(url_for('admin.painel_admin'))

    existente = Funcionario.query.filter_by(email_institucional=email).first()
    if existente and existente.id != funcionario_id:
        flash('E-mail institucional já cadastrado por outro funcionário', 'erro')
        return redirect(url_for('admin.painel_admin'))

    funcionario.nome_completo = nome
    funcionario.email_institucional = email
    funcionario.setor = setor

    if nova_senha:
        if len(nova_senha) < 6:
            flash('A senha deve ter no mínimo 6 caracteres', 'erro')
            return redirect(url_for('admin.painel_admin'))
        funcionario.senha_hash = generate_password_hash(nova_senha)

    db.session.commit()
    flash('Funcionário atualizado com sucesso!', 'sucesso')
    return redirect(url_for('admin.painel_admin'))


@admin_bp.route('/admin/funcionarios/<int:funcionario_id>/excluir', methods=['POST'])
@login_required
def excluir_funcionario(funcionario_id):
    if not hasattr(current_user, 'setor') or current_user.setor != 'Administrador':
        return redirect(url_for('auth.login_institucional'))
    funcionario = Funcionario.query.get_or_404(funcionario_id)
    if funcionario.id == current_user.id:
        flash('Você não pode excluir a si mesmo', 'erro')
        return redirect(url_for('admin.painel_admin'))
    db.session.delete(funcionario)
    db.session.commit()
    flash('Funcionário excluído com sucesso!', 'sucesso')
    return redirect(url_for('admin.painel_admin'))