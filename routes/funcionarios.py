from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Ocorrencia, AtualizacaoOcorrencia, Avaliacao, Notificacao
from datetime import datetime

funcionarios_bp = Blueprint('funcionarios', __name__)

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


@funcionarios_bp.route('/funcionario/painel')
@login_required
def painel_funcionario():
    if not hasattr(current_user, 'setor'):
        return redirect(url_for('auth.login_institucional'))
    tipos_do_setor = [t for t, s in TIPO_SETOR_MAP.items() if s == current_user.setor]
    busca = request.args.get('busca', '').strip()
    query = Ocorrencia.query.filter(Ocorrencia.tipo.in_(tipos_do_setor))
    if busca:
        query = query.filter(Ocorrencia.protocolo.ilike(f'%{busca}%'))
    ocorrencias = query.order_by(Ocorrencia.data_abertura.desc()).all()
    return render_template('painel_funcionario.html', ocorrencias=ocorrencias, busca=busca)


@funcionarios_bp.route('/funcionario/ocorrencias/<int:ocorrencia_id>/atender', methods=['GET', 'POST'])
@login_required
def atender_ocorrencia(ocorrencia_id):
    if not hasattr(current_user, 'setor'):
        return redirect(url_for('auth.login_institucional'))
    ocorrencia = Ocorrencia.query.get_or_404(ocorrencia_id)
    if request.method == 'POST':
        observacao = request.form.get('observacao', '').strip()
        novo_status = request.form.get('status', '').strip()
        notificar = request.form.get('notificar_cidadao') == 'on'

        if not observacao:
            flash('A observação é obrigatória', 'erro')
            return render_template('atendimento_ocorrencia.html', ocorrencia=ocorrencia)

        atualizacao = AtualizacaoOcorrencia(
            ocorrencia_id=ocorrencia.id,
            funcionario_id=current_user.id,
            observacao=observacao,
            notificar_cidadao=notificar
        )
        db.session.add(atualizacao)

        if novo_status and novo_status in ('aberta', 'em_andamento', 'concluida'):
            ocorrencia.status = novo_status
            if novo_status == 'concluida':
                ocorrencia.data_conclusao = datetime.utcnow()

        if notificar and ocorrencia.cidadao_id:
            status_label = {'aberta': 'Aberta', 'em_andamento': 'Em andamento', 'concluida': 'Concluída'}
            label = status_label.get(novo_status, ocorrencia.status)
            notificacao = Notificacao(
                cidadao_id=ocorrencia.cidadao_id,
                ocorrencia_id=ocorrencia.id,
                mensagem=f'{ocorrencia.protocolo} - Status: {label}. {observacao[:200]}'
            )
            db.session.add(notificacao)

        db.session.commit()
        flash('Ocorrência atualizada com sucesso!', 'sucesso')
        return redirect(url_for('funcionarios.painel_funcionario'))
    return render_template('atendimento_ocorrencia.html', ocorrencia=ocorrencia)


@funcionarios_bp.route('/funcionario/ocorrencias/<int:ocorrencia_id>/excluir', methods=['POST'])
@login_required
def excluir_ocorrencia(ocorrencia_id):
    if not hasattr(current_user, 'setor'):
        return redirect(url_for('auth.login_institucional'))
    ocorrencia = Ocorrencia.query.get_or_404(ocorrencia_id)
    motivo = request.form.get('motivo_exclusao', '').strip()

    if not motivo:
        flash('Informe o motivo da exclusão', 'erro')
        return redirect(url_for('funcionarios.atender_ocorrencia', ocorrencia_id=ocorrencia.id))

    if ocorrencia.cidadao_id and motivo:
        notificacao = Notificacao(
            cidadao_id=ocorrencia.cidadao_id,
            ocorrencia_id=ocorrencia.id,
            mensagem=f'{ocorrencia.protocolo} foi excluída. Motivo: {motivo}'
        )
        db.session.add(notificacao)

    AtualizacaoOcorrencia.query.filter_by(ocorrencia_id=ocorrencia.id).delete()
    Avaliacao.query.filter_by(ocorrencia_id=ocorrencia.id).delete()
    Notificacao.query.filter_by(ocorrencia_id=ocorrencia.id).delete()
    db.session.delete(ocorrencia)
    db.session.commit()
    flash(f'Ocorrência {ocorrencia.protocolo} excluída com sucesso!', 'sucesso')
    return redirect(url_for('funcionarios.painel_funcionario'))
