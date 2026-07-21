from app import app
from models import db, Cidadao, Funcionario, Ocorrencia, AtualizacaoOcorrencia, Avaliacao, Notificacao
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random


def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()

        admin = Funcionario(
            nome_completo='Administrador',
            email_institucional='admin@picos.pi.gov.br',
            senha_hash=generate_password_hash('admin123'),
            setor='Administrador',
            ativo=True
        )
        db.session.add(admin)

        func1 = Funcionario(
            nome_completo='Jonas Leal',
            email_institucional='jonas.leal@picos.pi.gov.br',
            senha_hash=generate_password_hash('func123'),
            setor='Infraestrutura',
            ativo=True
        )
        db.session.add(func1)

        func2 = Funcionario(
            nome_completo='Maria Santos',
            email_institucional='maria.santos@picos.pi.gov.br',
            senha_hash=generate_password_hash('func123'),
            setor='Limpeza Urbana',
            ativo=True
        )
        db.session.add(func2)

        func3 = Funcionario(
            nome_completo='Pedro Alves',
            email_institucional='pedro.alves@picos.pi.gov.br',
            senha_hash=generate_password_hash('func123'),
            setor='Iluminação Pública',
            ativo=True
        )
        db.session.add(func3)

        func4 = Funcionario(
            nome_completo='Clara Mendes',
            email_institucional='clara.mendes@picos.pi.gov.br',
            senha_hash=generate_password_hash('func123'),
            setor='Trânsito',
            ativo=True
        )
        db.session.add(func4)

        func5 = Funcionario(
            nome_completo='Rafael Torres',
            email_institucional='rafael.torres@picos.pi.gov.br',
            senha_hash=generate_password_hash('func123'),
            setor='Meio Ambiente',
            ativo=True
        )
        db.session.add(func5)

        cidadao1 = Cidadao( = Cidadao(
            nome_completo='Carlos Silva',
            cpf='123.456.789-09',
            email='carlos@email.com',
            senha_hash=generate_password_hash('123456')
        )
        db.session.add(cidadao1)

        cidadao2 = Cidadao(
            nome_completo='Ana Oliveira',
            cpf='987.654.321-00',
            email='ana@email.com',
            senha_hash=generate_password_hash('123456')
        )
        db.session.add(cidadao2)

        db.session.commit()

        ocorrencia1 = Ocorrencia(
            protocolo='PROC-2026-0001',
            cidadao_id=1,
            tipo='Buraco em via',
            descricao='Buraco grande na Rua das Flores, próximo ao número 150.',
            localizacao='Rua das Flores, 150',
            bairro='Centro',
            status='aberta'
        )
        db.session.add(ocorrencia1)

        ocorrencia2 = Ocorrencia(
            protocolo='PROC-2026-0002',
            cidadao_id=1,
            tipo='Coleta de resíduos',
            descricao='Coleta de resíduos não passou na Rua dos Ipês há 3 dias.',
            localizacao='Rua dos Ipês, 200',
            bairro='Jardim América',
            status='em_andamento'
        )
        db.session.add(ocorrencia2)

        ocorrencia3 = Ocorrencia(
            protocolo='PROC-2026-0003',
            cidadao_id=2,
            tipo='Iluminação pública',
            descricao='Poste com lâmpada queimada na Praça Central.',
            localizacao='Praça Central, s/n',
            bairro='Centro',
            status='concluida',
            data_conclusao=datetime.utcnow()
        )
        db.session.add(ocorrencia3)

        db.session.commit()

        atualizacao = AtualizacaoOcorrencia(
            ocorrencia_id=2,
            funcionario_id=1,
            observacao='Equipe encaminhada para verificar a situação.',
            notificar_cidadao=True
        )
        db.session.add(atualizacao)

        notificacao = Notificacao(
            cidadao_id=1,
            ocorrencia_id=2,
            mensagem='PROC-2026-0002 - Equipe encaminhada para verificar a situação.'
        )
        db.session.add(notificacao)

        avaliacao = Avaliacao(
            ocorrencia_id=3,
            cidadao_id=2,
            nota=4
        )
        db.session.add(avaliacao)

        db.session.commit()
        print('Banco de dados semeado com sucesso!')
        print('')
        print('Cidadãos:')
        print('  carlos@email.com / 123456')
        print('  ana@email.com / 123456')
        print('')
        print('Funcionários:')
        print('  admin@picos.pi.gov.br / admin123 (Administrador)')
        print('  jonas.leal@picos.pi.gov.br / func123 (Infraestrutura)')
        print('  maria.santos@picos.pi.gov.br / func123 (Limpeza Urbana)')
        print('  pedro.alves@picos.pi.gov.br / func123 (Iluminação Pública)')
        print('  clara.mendes@picos.pi.gov.br / func123 (Trânsito)')
        print('  rafael.torres@picos.pi.gov.br / func123 (Meio Ambiente)')


if __name__ == '__main__':
    seed()
