import base64
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
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


@ocorrencias_bp.route('/ocorrencias/nova', methods=['GET', 'POST'])
@login_required
def nova_ocorrencia():
    if request.method == 'POST':
        tipo = request.form.get('tipo', '').strip()
        descricao = request.form.get('descricao', '').strip()
        localizacao = request.form.get('localizacao', '').strip()
        bairro = request.form.get('bairro', '').strip()
        anonimo = request.form.get('anonimo') == 'sim'

        if not all([tipo, descricao, localizacao, bairro]):
            flash('Preencha todos os campos obrigatórios', 'erro')
            return render_template('nova_ocorrencia.html', tipos=TIPOS_OCORRENCIA, tipo_setor_map=TIPO_SETOR_MAP)

        foto_data = None
        foto_mime = None
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto and foto.filename:
                try:
                    mime = foto.content_type or 'image/jpeg'
                    dados = foto.read()
                    if dados:
                        encoded = base64.b64encode(dados).decode('utf-8')
                        foto_data = f'data:{mime};base64,{encoded}'
                        foto_mime = mime
                except Exception as e:
                    flash(f'Erro ao processar foto: {str(e)}', 'erro')

        protocolo = gerar_protocolo()
        ocorrencia = Ocorrencia(
            protocolo=protocolo,
            cidadao_id=None if anonimo else current_user.id,
            tipo=tipo,
            descricao=descricao,
            localizacao=localizacao,
            bairro=bairro,
            foto=foto_data,
            foto_mime=foto_mime
        )
        db.session.add(ocorrencia)
        db.session.commit()
        flash(f'Ocorrência registrada! Protocolo: {protocolo}', 'sucesso')
        return redirect(url_for('ocorrencias.listar_ocorrencias'))
    return render_template('nova_ocorrencia.html', tipos=TIPOS_OCORRENCIA, tipo_setor_map=TIPO_SETOR_MAP)


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
