import re
from models import Ocorrencia, db


def validar_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for i in range(9, 11):
        soma = sum(int(cpf[j]) * (i + 1 - j) for j in range(i))
        digito = (soma * 10 % 11) % 10
        if int(cpf[i]) != digito:
            return False
    return True


def formatar_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)
    return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'


def validar_email_institucional(email):
    return bool(re.match(r'^[\w\.-]+@picos\.pi\.gov\.br$', email))


def gerar_protocolo():
    from datetime import datetime
    ano = datetime.now().year
    ultima = Ocorrencia.query.filter(
        Ocorrencia.protocolo.like(f'PROC-{ano}-%')
    ).order_by(Ocorrencia.id.desc()).first()
    if ultima:
        numero = int(ultima.protocolo.split('-')[-1]) + 1
    else:
        numero = 1
    return f'PROC-{ano}-{numero:04d}'


def gerar_senha_temporaria():
    import secrets
    import string
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
