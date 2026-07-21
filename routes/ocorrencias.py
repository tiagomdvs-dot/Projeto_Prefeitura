import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Ocorrencia, Notificacao
from utils import gerar_protocolo

ocorrencias_bp = Blueprint('ocorrencias', __name__)

TIPOS_OCORRENCIA = [
    'Buraco em via',
    'Coleta de resíduos',
    'Iluminação pública',
    'Sinalização de trânsito',
    'Limpeza urbana',
    'Poda de árvores',
    'Calçamento',
    'Esgoto a céu aberto',
    'Outros',
]


@ocorrencias_bp.route('/ocorrencias/nova', methods=['GET', 'POST'])
@login_required
def nova_ocorrencia():
    if request.method == 'POST':
        tipo = request.form.get('tipo', '').strip()
        descricao = request.form.get('descricao', '').strip()
        localizacao = request.form.get('localizacao', '').strip()
        anonimo = request.form.get('anonimo') == 'sim'

        if not all([tipo, descricao, localizacao]):
            flash('Preencha todos os campos obrigatórios', 'erro')
            return render_template('nova_ocorrencia.html', tipos=TIPOS_OCORRENCIA)

        foto_url = None
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto and foto.filename:
                ext = os.path.splitext(foto.filename)[1] or '.jpg'
                nome_unico = f'{uuid.uuid4().hex}{ext}'
                upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_path, exist_ok=True)
                caminho = os.path.join(upload_path, nome_unico)
                try:
                    foto.save(caminho)
                    foto_url = f'uploads/{nome_unico}'
                except Exception:
                    foto_url = None

        protocolo = gerar_protocolo()
        ocorrencia = Ocorrencia(
            protocolo=protocolo,
            cidadao_id=None if anonimo else current_user.id,
            tipo=tipo,
            descricao=descricao,
            localizacao=localizacao,
            foto_url=foto_url
        )
        db.session.add(ocorrencia)
        db.session.commit()
        flash(f'Ocorrência registrada! Protocolo: {protocolo}', 'sucesso')
        return redirect(url_for('ocorrencias.listar_ocorrencias'))
    return render_template('nova_ocorrencia.html', tipos=TIPOS_OCORRENCIA)


@ocorrencias_bp.route('/ocorrencias')
@login_required
def listar_ocorrencias():
    ocorrencias = Ocorrencia.query.filter_by(cidadao_id=current_user.id).order_by(Ocorrencia.data_abertura.desc()).all()
    return render_template('acompanhamento_ocorrencias.html', ocorrencias=ocorrencias)


@ocorrencias_bp.route('/ocorrencias/<int:ocorrencia_id>')
@login_required
def detalhe_ocorrencia(ocorrencia_id):
    ocorrencia = Ocorrencia.query.get_or_404(ocorrencia_id)
    return render_template('detalhe_ocorrencia.html', ocorrencia=ocorrencia)
