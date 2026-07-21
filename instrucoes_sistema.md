# Instruções para Criação do Sistema "Prefeitura"

## 1. Visão Geral do Projeto

Sistema digital para prefeitura municipal que permite cidadãos abrirem, acompanharem e avaliarem solicitações de serviços públicos (ocorrências). Possui painel administrativo para funcionários e administradores gerenciarem as solicitações.

**Três perfis de acesso:**
- **Cidadão** — usuário comum que abre e acompanha ocorrências
- **Funcionário** — acesso restrito ao seu setor para atendimento
- **Administrador** — gestão de usuários e sistema

---

## 2. Estrutura de Telas e Funcionalidades

### A. Portal do Cidadão (Acesso Público)

#### Tela de Login
- **Campos**: E-MAIL, SENHA
- **Botões**: "Entrar", "Esqueci minha senha", "Criar minha conta"
- **Mensagem de erro**: "E-mail ou senha inválidos"
- **Rodapé**: "Secretaria de Infraestrutura e Mobilidade Urbana"

#### Tela de Cadastro de Cidadão
- **Campos**: NOME COMPLETO, CPF, E-MAIL, SENHA (mín. 6 caracteres + dica de segurança), CONFIRMAR SENHA
- **Botões**: "Criar conta", link "Já tem conta? Entrar"
- **Validações**: senha >= 6 caracteres, CPF válido, e-mail e CPF únicos

#### Tela de Abertura de Nova Ocorrência
- **Campos obrigatórios**: TIPO DE OCORRÊNCIA (seletor), DESCRIÇÃO, LOCALIZAÇÃO (Rua, número, bairro)
- **Campos opcionais**: FOTO (upload)
- **Identificação**: identificar-se (vincula ao usuário logado) ou anônimo
- **Ação**: "Enviar ocorrência" → gera número de protocolo (PROC-XXXXX)

#### Tela de Acompanhamento de Ocorrências
- Lista de ocorrências com status: Aberta, Em andamento, Concluída
- Cada item: Título, endereço, status, última atualização
- Ocorrências concluídas: avaliação por estrelas (1 a 5)

#### Tela de Notificações
- Feed de notificações sobre ocorrências (ex: "PROC-2026-843 - equipe a caminho")
- Exibir data/hora da notificação

---

### B. Portal do Funcionário (Acesso Restrito)

#### Tela de Login Institucional
- Acesso exclusivo: e-mail @picos.pi.gov.br + senha
- Links: "Esqueci minha senha", "Problemas com acesso? Contate o setor de TI"

#### Tela de Painel do Funcionário
- Cabeçalho: nome do funcionário + setor (ex: "Jonas Leal - Setor: Infraestrutura")
- Lista de ocorrências designadas ao seu setor

#### Tela de Atendimento de Ocorrência
- Detalhes: título, endereço, nome do cidadão, foto anexada, status atual
- Campo: OBSERVAÇÃO DO ATENDIMENTO
- Botões: "Notificar cidadão", "Salvar e notificar"

---

### C. Portal do Administrador (Acesso Restrito)

#### Tela de Painel do Administrador
- Acesso via login institucional (mesmo da página 9), com permissões elevadas
- **Cadastro de funcionários**:
  - NOME COMPLETO
  - E-MAIL INSTITUCIONAL
  - SETOR
  - Regra: senha temporária gerada e enviada para o e-mail institucional

---

## 3. Requisitos Técnicos e Regras de Negócio

### Níveis de Acesso
| Perfil | Acesso |
|--------|--------|
| Cidadão | Portal público (cadastro/login próprio) |
| Funcionário | Login institucional (@picos.pi.gov.br), restrito ao setor |
| Administrador | Login institucional com permissões elevadas |

### Fluxo de Trabalho (Workflow)
1. Cidadão abre ocorrência (identificado ou anonimamente) → gera PROC-XXXXX
2. Sistema notifica o setor responsável
3. Funcionário visualiza a ocorrência em seu painel
4. Funcionário atualiza o status e adiciona observações
5. Sistema notifica o cidadão sobre a atualização
6. Ao ser concluída, o cidadão pode avaliar o serviço (1 a 5 estrelas)

### Geração de Protocolo
- Número único e sequencial: `PROC-ANO-NUMERO` (ex: `PROC-2026-841`)

### Validações
- CPF e e-mail únicos no cadastro de cidadãos
- E-mail institucional único, padrão `nome@picos.pi.gov.br`
- Senhas com mínimo de 6 caracteres
- CPF válido (validação de dígitos)

### Segurança
- Autenticação diferenciada entre portal do cidadão e portal institucional
- Controle de sessão na área restrita
- Senhas armazenadas como hash

---

## 4. Diretrizes de Design e UI

- **Estilo minimalista**, foco em usabilidade e clareza
- **Ícones universais**: voltar, notificação, câmera, estrelas
- **Listagens limpas e informativas** com status visível
- **Responsividade mobile-first** (cidadãos acessam principalmente pelo celular)
- **Identidade visual** conforme cabeçalho do PDF de referência

### Diretrizes Mobile-First (do AGENTS.md)
- Breakpoints: celular ≤ 768px, tablet 769px–1024px, PC > 1024px
- Botões/inputs com mínimo 44x44px para toque
- Evitar hover como única interação

---

## 5. Estrutura de Dados (Modelo Conceitual)

### `Cidadaos`
| Campo | Tipo | Observação |
|-------|------|------------|
| id | INTEGER (PK) | Auto-incremento |
| nome_completo | VARCHAR(255) | Obrigatório |
| cpf | VARCHAR(14) | Único, validado |
| email | VARCHAR(255) | Único |
| senha_hash | VARCHAR(255) | Mín. 6 caracteres |
| data_cadastro | DATETIME | Auto |

### `Funcionarios`
| Campo | Tipo | Observação |
|-------|------|------------|
| id | INTEGER (PK) | Auto-incremento |
| nome_completo | VARCHAR(255) | Obrigatório |
| email_institucional | VARCHAR(255) | Único, @picos.pi.gov.br |
| senha_hash | VARCHAR(255) | Temporária gerada pelo admin |
| setor | VARCHAR(100) | Ex: Infraestrutura, Limpeza Urbana |
| ativo | BOOLEAN | True por padrão |

### `Ocorrencias`
| Campo | Tipo | Observação |
|-------|------|------------|
| id | INTEGER (PK) | Auto-incremento |
| protocolo | VARCHAR(20) | Único, ex: PROC-2026-841 |
| cidadao_id | INTEGER (FK) | Nullable (anônimo) |
| tipo | VARCHAR(100) | Buraco em via, Coleta de resíduos... |
| descricao | TEXT | Detalhamento |
| localizacao | VARCHAR(255) | Rua, número, bairro |
| foto_url | VARCHAR(500) | Nullable |
| status | VARCHAR(20) | aberta, em_andamento, concluida |
| data_abertura | DATETIME | Auto |
| data_conclusao | DATETIME | Nullable |

### `Atualizacoes_Ocorrencias`
| Campo | Tipo | Observação |
|-------|------|------------|
| id | INTEGER (PK) | Auto-incremento |
| ocorrencia_id | INTEGER (FK) | Referência Ocorrencias |
| funcionario_id | INTEGER (FK) | Referência Funcionarios |
| observacao | TEXT | Ações tomadas |
| data_hora | DATETIME | Auto |
| notificar_cidadao | BOOLEAN | Se deve notificar |

### `Avaliacoes`
| Campo | Tipo | Observação |
|-------|------|------------|
| id | INTEGER (PK) | Auto-incremento |
| ocorrencia_id | INTEGER (FK) | Referência Ocorrencias |
| cidadao_id | INTEGER (FK) | Referência Cidadaos |
| nota | INTEGER | 1 a 5 |
| data_avaliacao | DATETIME | Auto |

---

## 6. Resumo das Funcionalidades

1. **Autenticação** — dois portais: Cidadão (login próprio) e Institucional (e-mail @picos.pi.gov.br)
2. **CRUD de Cidadãos** — cadastro com validação de CPF e e-mail
3. **CRUD de Ocorrências** — abertura, listagem por status, detalhamento
4. **Sistema de Notificações** — in-app para atualizações de status
5. **Painel Administrativo** — cadastro de funcionários com senha temporária
6. **Painel do Funcionário** — visualização e atualização de ocorrências do setor
7. **Sistema de Avaliação** — estrelas (1 a 5) para ocorrências concluídas

---

## 7. Organização dos Arquivos (conforme AGENTS.md)

```
/
├── app.py                    # App principal Flask
├── models.py                 # Modelos de BD (SQLAlchemy)
├── utils.py                  # Utilitários (validação CPF, geração protocolo, etc.)
├── requirements.txt          # Dependências
├── vercel.json               # Configuração de deploy
├── seed_completo.py          # Semeador de dados para testes
├── test_funcional.py         # Testes automatizados
├── atualizacoes.txt          # Registro de alterações
│
├── templates/                # HTML (snake_case)
│   ├── login.html
│   ├── cadastro_cidadao.html
│   ├── nova_ocorrencia.html
│   ├── acompanhamento_ocorrencias.html
│   ├── notificacoes.html
│   ├── login_institucional.html
│   ├── painel_funcionario.html
│   ├── atendimento_ocorrencia.html
│   └── painel_admin.html
│
├── static/
│   ├── css/
│   │   ├── estilo_global.css
│   │   ├── login.css
│   │   ├── cadastro.css
│   │   ├── ocorrencias.css
│   │   ├── painel.css
│   │   └── notificacoes.css
│   │
│   └── js/
│       ├── validacoes.js
│       ├── ocorrencias.js
│       ├── notificacoes.js
│       └── avaliacao.js
│
└── routes/
    ├── auth.py               # Rotas de autenticação (cidadão e institucional)
    ├── cidadaos.py            # CRUD de cidadãos
    ├── ocorrencias.py         # CRUD de ocorrências
    ├── funcionarios.py        # Painel e atendimento do funcionário
    ├── admin.py               # Painel administrativo
    ├── notificacoes.py        # Sistema de notificações
    └── avaliacoes.py          # Sistema de avaliação
```

---

## 8. Regras de Negócio Detalhadas

### Autenticação
- **Cidadão**: login via e-mail + senha comuns. Sessão separada do portal institucional.
- **Funcionário/Admin**: login via e-mail institucional (@picos.pi.gov.br). Sessão isolada.
- Recuperação de senha para ambos os portais.

### Ocorrências
- Qualquer cidadão pode abrir ocorrência (identificado ou anonimamente)
- Ocorrências anônimas não têm vínculo com cidadão (`cidadao_id = NULL`)
- Ao abrir, o sistema gera protocolo único no formato `PROC-ANO-NUMERO_SEQUENCIAL`
- Status possíveis: `aberta` → `em_andamento` → `concluida`
- Apenas funcionários do setor correspondente ao tipo da ocorrência podem atendê-la

### Notificações
- Geradas automaticamente quando um funcionário atualiza o status
- Visíveis no feed de notificações do cidadão
- Contêm: protocolo, mensagem descritiva, data/hora

### Avaliação
- Disponível apenas para ocorrências com status `concluida`
- Apenas o cidadão que abriu a ocorrência pode avaliar
- Nota de 1 a 5 estrelas
- Uma única avaliação por ocorrência

---

## 9. Padrões de Código (conforme AGENTS.md)

### Nomenclatura
- HTML: `snake_case.html`
- CSS: `snake_case.css`
- JS: `snake_case.js`
- Rotas Python: `snake_case.py`

### Commits
- Prefixos: `feat:`, `chore:`, `fix:`, `redeploy:`
- Git config: `tiago.m.dvs@gmail.com` / `tiagomdvs-dot`
- Nunca commitar sem solicitação explícita

### Testes
- Arquivo: `test_funcional.py`
- Dinâmicos (descobrir dados via API, sem IDs fixos)
- Cobertura: fluxo principal, casos de borda, resposta HTTP
- Rodar com servidor Flask ativo + `python seed_completo.py` (se DB vazio)

### Registro de Atualizações
- Toda alteração registrada em `atualizacoes.txt`
- Formato: `DD/MM/AAAA - descrição das mudanças`
- Incluir hash do commit quando houver

---

## 10. Tecnologias e Dependências

| Tecnologia | Versão | Finalidade |
|------------|--------|------------|
| Python | 3.10+ | Runtime |
| Flask | 3.x | Framework web |
| Flask-SQLAlchemy | 3.x | ORM |
| Flask-Login | 0.6+ | Autenticação |
| Werkzeug | 2.x | Hash de senhas |
| SQLite | — | Banco de dados (dev) |
| Pillow | 10.x | Processamento de imagens |
| python-dotenv | 1.x | Variáveis de ambiente |
| email-validator | 2.x | Validação de e-mail |

---

## 10. Cronograma Sugerido de Implementação

| Fase | Módulo | Prioridade |
|------|--------|------------|
| 1 | Models + DB + app.py base | Alta |
| 2 | Autenticação Cidadão (login/cadastro) | Alta |
| 3 | CRUD de Ocorrências + Protocolo | Alta |
| 4 | Portal do Funcionário (painel + atendimento) | Alta |
| 5 | Portal do Administrador (cadastro de funcionários) | Alta |
| 6 | Sistema de Notificações | Média |
| 7 | Sistema de Avaliação (estrelas) | Média |
| 8 | Testes automatizados (test_funcional.py) | Alta |
| 9 | Responsividade e refinamento UI | Média |
| 10 | Deploy (Vercel) | Baixa |
