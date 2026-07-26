import requests
import json
import random
import string

BASE_URL = 'http://127.0.0.1:5000'
TESTES = 0
FALHAS = 0


def log_teste(nome, resultado, detalhe=''):
    global TESTES, FALHAS
    TESTES += 1
    status = 'PASS' if resultado else 'FAIL'
    if not resultado:
        FALHAS += 1
    print(f'  [{status}] {nome}' + (f' - {detalhe}' if detalhe else ''))


def testar_pagina_inicial():
    r = requests.get(f'{BASE_URL}/')
    log_teste('Página inicial (login)', r.status_code == 200)


def testar_cadastro_cidadao():
    import random
    email = f'teste{random.randint(1000,9999)}@email.com'
    r = requests.post(f'{BASE_URL}/cadastro', data={
        'nome': 'Teste Silva',
        'cpf': '529.982.247-25',
        'email': email,
        'senha': '123456',
        'confirmar_senha': '123456'
    })
    log_teste('Cadastro cidadão', r.status_code in (200, 302), email)


def testar_login_cidadao():
    r = requests.post(f'{BASE_URL}/login', data={
        'email': 'carlos@email.com',
        'senha': '123456'
    })
    log_teste('Login cidadão', r.status_code in (200, 302))


def testar_login_invalido():
    r = requests.post(f'{BASE_URL}/login', data={
        'email': 'invalido@email.com',
        'senha': 'errada'
    })
    log_teste('Login inválido', 'E-mail ou senha inválidos' in r.text)


def testar_login_institucional():
    r = requests.post(f'{BASE_URL}/login/institucional', data={
        'email': 'admin@picos.pi.gov.br',
        'senha': 'admin123'
    })
    log_teste('Login institucional admin', r.status_code in (200, 302))


def testar_pagina_cadastro():
    r = requests.get(f'{BASE_URL}/cadastro')
    log_teste('Página de cadastro', r.status_code == 200)


def testar_pagina_login_institucional():
    r = requests.get(f'{BASE_URL}/login/institucional')
    log_teste('Página login institucional', r.status_code == 200)


def testar_pagina_esqueci_senha():
    r = requests.get(f'{BASE_URL}/esqueci-senha')
    log_teste('Página esqueci senha', r.status_code == 200)


def testar_cpf_valido():
    from utils import validar_cpf
    assert validar_cpf('529.982.247-25') == True
    assert validar_cpf('111.111.111-11') == False
    assert validar_cpf('123') == False
    log_teste('Validação de CPF', True)


def testar_email_institucional():
    from utils import validar_email_institucional
    assert validar_email_institucional('joao@picos.pi.gov.br') == True
    assert validar_email_institucional('joao@gmail.com') == False
    assert validar_email_institucional('joao@picos.pi.gov') == False
    log_teste('Validação e-mail institucional', True)


def testar_geracao_protocolo():
    from app import app
    with app.app_context():
        from utils import gerar_protocolo
        protocolo = gerar_protocolo()
        assert protocolo.startswith('PROC-2026-')
        log_teste('Geração de protocolo', True)


def testar_geracao_senha_temporaria():
    from utils import gerar_senha_temporaria
    senha = gerar_senha_temporaria()
    assert len(senha) == 10
    log_teste('Geração senha temporária', True)


def testar_api_ocorrencias():
    s = requests.Session()
    s.post(f'{BASE_URL}/login', data={'email': 'carlos@email.com', 'senha': '123456'})
    r = s.get(f'{BASE_URL}/ocorrencias')
    log_teste('Listar ocorrências (logado)', r.status_code == 200)


def testar_api_notificacoes():
    s = requests.Session()
    s.post(f'{BASE_URL}/login', data={'email': 'carlos@email.com', 'senha': '123456'})
    r = s.get(f'{BASE_URL}/notificacoes')
    log_teste('Listar notificações (logado)', r.status_code == 200)


def testar_cadastro_funcionario():
    s = requests.Session()
    s.post(f'{BASE_URL}/login/institucional', data={'email': 'admin@picos.pi.gov.br', 'senha': 'admin123'})
    import random
    email = f'teste{random.randint(1000,9999)}@picos.pi.gov.br'
    r = s.post(f'{BASE_URL}/admin/funcionarios/cadastrar', data={
        'nome': 'Funcionario Teste',
        'email': email,
        'setor': 'Infraestrutura'
    })
    log_teste('Cadastro funcionário pelo admin', r.status_code in (200, 302))


def testar_acesso_sem_login():
    r = requests.get(f'{BASE_URL}/ocorrencias')
    log_teste('Bloqueio sem login', r.status_code in (200, 302) and 'login' in r.url.lower())


def testar_atendimento_com_equipe():
    s = requests.Session()
    s.post(f'{BASE_URL}/login/institucional', data={'email': 'admin@picos.pi.gov.br', 'senha': 'admin123'})
    r = s.get(f'{BASE_URL}/funcionario/painel')
    import re
    match = re.search(r'/funcionario/ocorrencias/(\d+)/atender', r.text)
    if match:
        ocorrencia_id = match.group(1)
        r_get = s.get(f'{BASE_URL}/funcionario/ocorrencias/{ocorrencia_id}/atender')
        tem_historico = 'Histórico de Atendimentos' in r_get.text
        r_post = s.post(f'{BASE_URL}/funcionario/ocorrencias/{ocorrencia_id}/atender', data={
            'observacao': 'Teste de equipe automatizado',
            'status': 'em_andamento',
            'notificar_cidadao': 'on',
            'equipe': 'Equipe Teste Automatizado'
        })
        log_teste('Atendimento equipe salva', r_post.status_code in (200, 302))
        log_teste('Atendimento historico presente', tem_historico)
    else:
        log_teste('Atendimento equipe salva', False, 'Nenhuma ocorrência disponível')
        log_teste('Atendimento historico presente', False, 'Nenhuma ocorrência disponível')


def testar_cancelamento_ocorrencia():
    s = requests.Session()
    s.post(f'{BASE_URL}/login/institucional', data={'email': 'admin@picos.pi.gov.br', 'senha': 'admin123'})
    r = s.get(f'{BASE_URL}/funcionario/painel')
    import re
    match = re.search(r'/funcionario/ocorrencias/(\d+)/atender', r.text)
    if match:
        ocorrencia_id = match.group(1)
        r_post = s.post(f'{BASE_URL}/funcionario/ocorrencias/{ocorrencia_id}/atender', data={
            'observacao': 'Cancelamento automatizado',
            'status': 'cancelada',
            'equipe': ''
        })
        log_teste('Cancelamento ocorrencia', r_post.status_code in (200, 302))
    else:
        log_teste('Cancelamento ocorrencia', False, 'Nenhuma ocorrência disponível')


if __name__ == '__main__':
    print('=== Testes Funcionais - Sistema Prefeitura ===')
    print()

    testar_pagina_inicial()
    testar_pagina_cadastro()
    testar_pagina_login_institucional()
    testar_pagina_esqueci_senha()
    testar_cadastro_cidadao()
    testar_login_cidadao()
    testar_login_invalido()
    testar_login_institucional()
    testar_acesso_sem_login()
    testar_api_ocorrencias()
    testar_api_notificacoes()
    testar_cadastro_funcionario()
    testar_atendimento_com_equipe()
    testar_cancelamento_ocorrencia()
    testar_cpf_valido()
    testar_email_institucional()
    testar_geracao_protocolo()
    testar_geracao_senha_temporaria()

    print()
    print(f'Total: {TESTES} | Passaram: {TESTES - FALHAS} | Falharam: {FALHAS}')
    if FALHAS == 0:
        print('Todos os testes passaram!')
    else:
        print(f'Atenção: {FALHAS} teste(s) falharam.')
