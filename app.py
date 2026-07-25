from flask import Flask
from flask_login import LoginManager
from models import db, Cidadao, Funcionario
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-super-secreta-prefeitura-2026')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://neondb_owner:npg_9Am8zyepVdnZ@ep-young-sun-avmnkg2p-pooler.c-11.us-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    parts = user_id.split('_', 1)
    if parts[0] == 'c':
        return Cidadao.query.get(int(parts[1]))
    elif parts[0] == 'f':
        return Funcionario.query.get(int(parts[1]))
    return None

from routes.auth import auth_bp
from routes.cidadaos import cidadaos_bp
from routes.ocorrencias import ocorrencias_bp
from routes.funcionarios import funcionarios_bp
from routes.admin import admin_bp
from routes.notificacoes import notificacoes_bp
from routes.avaliacoes import avaliacoes_bp

app.register_blueprint(auth_bp)
app.register_blueprint(cidadaos_bp)
app.register_blueprint(ocorrencias_bp)
app.register_blueprint(funcionarios_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(notificacoes_bp)
app.register_blueprint(avaliacoes_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
