from flask import Blueprint, render_template, jsonify, redirect, url_for
from flask_login import login_required, current_user
from models import Notificacao

notificacoes_bp = Blueprint('notificacoes', __name__)


@notificacoes_bp.route('/notificacoes')
@login_required
def listar_notificacoes():
    notificacoes = Notificacao.query.filter_by(cidadao_id=current_user.id).order_by(Notificacao.data_hora.desc()).all()
    return render_template('notificacoes.html', notificacoes=notificacoes)


@notificacoes_bp.route('/notificacoes/marcar-lida/<int:notificacao_id>')
@login_required
def marcar_lida(notificacao_id):
    notificacao = Notificacao.query.get_or_404(notificacao_id)
    if notificacao.cidadao_id == current_user.id:
        notificacao.lida = True
        from models import db
        db.session.commit()
    return redirect(url_for('notificacoes.listar_notificacoes'))
