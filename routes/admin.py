import csv
from io import StringIO
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from models import db, Funcionario, Ocorrencia, AtualizacaoOcorrencia, Avaliacao
from utils import validar_email_institucional, gerar_senha_temporaria
from sqlalchemy import func, extract

TIPO_SETOR_MAP = {
    'Buraco em via': 'Infraestrutura',
    'Coleta de resíduos': 'Limpeza Urbana',
    'Iluminação pública': 'Iluminação Pública',
    'Sinalização de trânsito': 'Trânsito',
    'Limpeza urbana': 'Limpeza Urbana',
    'Poda de árvores': 'Meio Ambiente',
    'Calçamento': 'Infraestrutura',
    'Esgoto a céu aberto': 'Infraestrutura',
    'Outros': 'Infraestrutura',
}

SETORES = ['Infraestrutura', 'Limpeza Urbana', 'Iluminação Pública', 'Trânsito', 'Meio Ambiente']

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

    setor_stats = []
    for setor in SETORES:
        tipos = [t for t, s in TIPO_SETOR_MAP.items() if s == setor]
        q = Ocorrencia.query.filter(Ocorrencia.tipo.in_(tipos))
        if mes_filtro:
            ano, mes = mes_filtro.split('-')
            q = q.filter(extract('year', Ocorrencia.data_abertura) == int(ano), extract('month', Ocorrencia.data_abertura) == int(mes))
        total = q.count()
        abertas = q.filter(Ocorrencia.status == 'aberta').count()
        andamento = q.filter(Ocorrencia.status == 'em_andamento').count()
        concluidas = q.filter(Ocorrencia.status == 'concluida').count()
        ids = [r[0] for r in q.with_entities(Ocorrencia.id).all()]
        atendidas = AtualizacaoOcorrencia.query.filter(AtualizacaoOcorrencia.ocorrencia_id.in_(ids)).distinct(AtualizacaoOcorrencia.ocorrencia_id).count() if ids else 0
        media_nota = db.session.query(func.avg(Avaliacao.nota)).filter(Avaliacao.ocorrencia_id.in_(ids)).scalar() if ids else None
        setor_stats.append({
            'setor': setor,
            'total': total,
            'abertas': abertas,
            'andamento': andamento,
            'concluidas': concluidas,
            'atendidas': atendidas,
            'media_nota': round(media_nota, 1) if media_nota else None
        })

    return render_template('painel_admin.html', funcionarios=funcionarios, ocorrencias=ocorrencias, bairros=bairros, bairro_filtro=bairro_filtro, stats=stats, mes_filtro=mes_filtro, setor_stats=setor_stats)


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


@admin_bp.route('/admin/exportar/csv')
@login_required
def exportar_csv():
    if not hasattr(current_user, 'setor') or current_user.setor != 'Administrador':
        return redirect(url_for('auth.login_institucional'))
    mes_filtro = request.args.get('mes', '')
    query = db.session.query(
        Ocorrencia.protocolo,
        Ocorrencia.tipo,
        Ocorrencia.bairro,
        Ocorrencia.localizacao,
        Ocorrencia.status,
        Ocorrencia.data_abertura,
        Ocorrencia.data_conclusao
    )
    if mes_filtro:
        ano, mes = mes_filtro.split('-')
        query = query.filter(
            extract('year', Ocorrencia.data_abertura) == int(ano),
            extract('month', Ocorrencia.data_abertura) == int(mes)
        )
    rows = query.order_by(Ocorrencia.data_abertura.desc()).all()

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Protocolo', 'Tipo', 'Bairro', 'Localizacao', 'Status', 'Data Abertura', 'Data Conclusao'])
    for r in rows:
        writer.writerow([
            r.protocolo, r.tipo, r.bairro, r.localizacao, r.status,
            r.data_abertura.strftime('%d/%m/%Y %H:%M') if r.data_abertura else '',
            r.data_conclusao.strftime('%d/%m/%Y %H:%M') if r.data_conclusao else ''
        ])

    nome_arquivo = f'ocorrencias_{mes_filtro or "todas"}.csv'
    return Response(
        si.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={nome_arquivo}'}
    )