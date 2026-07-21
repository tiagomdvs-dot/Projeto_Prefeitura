from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Ocorrencia, Avaliacao

avaliacoes_bp = Blueprint('avaliacoes', __name__)


@avaliacoes_bp.route('/ocorrencias/<int:ocorrencia_id>/avaliar', methods=['POST'])
@login_required
def avaliar(ocorrencia_id):
    ocorrencia = Ocorrencia.query.get_or_404(ocorrencia_id)
    if ocorrencia.status != 'concluida':
        flash('Só é possível avaliar ocorrências concluídas', 'erro')
        return redirect(url_for('ocorrencias.listar_ocorrencias'))
    if ocorrencia.cidadao_id != current_user.id:
        flash('Você só pode avaliar suas próprias ocorrências', 'erro')
        return redirect(url_for('ocorrencias.listar_ocorrencias'))
    if ocorrencia.avaliacao:
        flash('Você já avaliou esta ocorrência', 'erro')
        return redirect(url_for('ocorrencias.listar_ocorrencias'))
    nota = request.form.get('nota', type=int)
    if not nota or nota < 1 or nota > 5:
        flash('Nota inválida (1 a 5)', 'erro')
        return redirect(url_for('ocorrencias.listar_ocorrencias'))
    from models import db, Avaliacao
    from datetime import datetime
    avaliacao = Avaliacao(
        ocorrencia_id=ocorrencia_id,
        cidadao_id=current_user.id,
        nota=nota
    )
    db.session.add(avaliacao)
    db.session.commit()
    flash('Avaliação registrada!', 'sucesso')
    return redirect(url_for('ocorrencias.listar_ocorrencias'))
