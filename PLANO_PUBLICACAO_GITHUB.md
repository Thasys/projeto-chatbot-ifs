# 📋 PLANO DE AÇÃO - Dockerização e Publicação no GitHub

## 🎯 Objetivo
Atualizar Docker, documentação e estrutura do projeto para publicação profissional no GitHub com suporte a FIX 4.

---

## ✅ FASE 1: PREPARAÇÃO & LIMPEZA (15 minutos)

### 1.1 Remover Arquivos Desnecessários
Arquivos que NÃO devem ir para GitHub:

```bash
# Logs de teste
- test_simples_output.txt
- test_output_comparacao.txt
- comparacao_manual_vs_automatico.txt
- test_results.txt
- test_simples_resultado.json
- debug_chatbot.log
- etl_logs.log

# Arquivos de debug/temporários
- debug_advanced.py (manter summary)
- debug_view_structure.py (manter summary)
- test_system.py
- diagnose_pipeline.py
- validate_fixes.py

# Cache Python
- __pycache__/
- venv/ (se ainda existir)
- venv_novo/ (se ainda existir)

# Logs de testes
- .pytest_cache/
```

**Ação**: Executar `.gitignore` cleanup:
```bash
git clean -fd  # Remove untracked files
git rm -r --cached __pycache__ venv/ 2>/dev/null
```

---

## 📝 FASE 2: DOCUMENTAÇÃO (30 minutos)

### 2.1 Atualizar README.md (COMPLETO)

Substituir conteúdo atual por versão profissional que inclua:
- ✅ Novo sumário com FIX 4
- ✅ Diagrama de arquitetura ASCII
- ✅ Status do projeto (Production-Ready)
- ✅ Seção de mudanças recentes
- ✅ Instruções Docker atualizadas

### 2.2 Criar CHANGELOG.md

```markdown
# Changelog

## [2.0.0] - 2026-04-09 (FIX 4 Release)

### ✨ Novo
- **Descoberta de Banco de Dados**: Mapeamento completo de todas 11 colunas em v_financas_geral
- **Intent Detection Fix**: Data Detective agora classifica corretamente TOTAL queries sem entidades
- **Logging Profissional**: Tags [SQL EXEC] e [FUZZY SEARCH] para debugging
- **Column Mapping Fix**: `ug`→`unidade_pagadora`, `pessoa_nome`→`historico_detalhado`

### 🐛 Corrigido
- Pergunta 1 retornando valores incorretos (estava buscando "IFS" como entidade)
- Falta de logging para troubleshooting
- Colunas erradas em prompts dos agentes

### 📊 Status de Testes
- Pergunta 1 (TOTAL 2024): ✅ PASS (R$ 339.539.000,00, Confiança: 95%)
- Perguntas 2-5: ⏳ Aguardando testes completos

### 🔧 Detalhes Técnicos
- CrewAI com 3 agentes otimizados
- Logging estruturado em tools.py
- Database queries validadas contra MySQL real
```

### 2.3 Criar CONTRIBUTING.md

```markdown
# 🤝 Contribuindo

## Setup Desenvolvimento

1. **Clone e instale venv:**
```bash
git clone https://github.com/seu-user/projeto-chatbot-ifs.git
cd projeto-chatbot-ifs
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure .env:**
```bash
cp .env.example .env
# Edite .env com suas credenciais
```

3. **Run testes:**
```bash
python -m pytest tests/ -v
```

## Padrões de Código
- Type hints obrigatórios
- Docstrings em portugês
- Logging com tags [MODULO]
```

### 2.4 Criar DEVELOPMENT.md

```markdown
# 🛠️ Guia de Desenvolvimento

## Arquitetura dos Agentes

### Agente 1: 🔍 Data Detective
- **Role**: Metadata Navigator
- **Função**: Extrai intent, busca entidades, retorna JSON
- **Fix 4**: Agora ignora "IFS" em queries TOTAL

### Agente 2: 🏗️ SQL Expert
- **Role**: SQL Architect
- **Função**: Gera SQL otimizado
- **Fix 4**: Usa colunas corretas (`unidade_pagadora` em vez de `ug`)

### Agente 3: 📊 Public Transparency Analyst
- **Role**: Formatter
- **Função**: Traduz SQL para português PT-BR

## Logging & Debugging

Logs incluem tags especiais:
- `[SQL EXEC]`: Queries SQL executadas
- `[FUZZY SEARCH]`: Matches de busca fuzzy encontrados
- `[DEBUG CREW RESULT]`: Resultado bruto do crew

Visualize com:
```bash
tail -f debug_chatbot.log
```

## Estrutura de Diretórios

```
projeto-chatbot-ifs/
├── app_v2.py              # Streamlit main (v2 com confidence)
├── crew_definition_v2.py   # 3 agentes com FIX 4
├── tools.py               # SQL & fuzzy search com logging
├── db_connection.py       # MySQL connector
├── etl_scripts/           # ETL pipeline
├── tests/                 # Testes unitários
├── reports/               # Relatórios CSV gerados
└── docs/                  # Documentação
```
```

---

## 🐳 FASE 3: DOCKER (20 minutos)

### 3.1 Atualizar Dockerfile

- Mudar Python 3.9 → **3.13**
- Adicionar verificação de saúde melhorada
- Otimizar layers
- Adicionar label de versão

**Arquivo**: `Dockerfile` (será modificado)

### 3.2 Atualizar docker-compose.yml

- Add servço `adminer` para debug MySQL (opcional)
- Add volumes para logs
- Melhorar healthcheck
- Add variáveis de versão

**Arquivo**: `docker-compose.yml` (será modificado)

### 3.3 Criar .dockerignore (Se não existir)

```
__pycache__
venv
venv_novo
.git
.env
.pytest_cache
*.log
__pycache__
tests/
.github/
docs/
*.md
```

---

## 🔐 FASE 4: GITHUB (15 minutos)

### 4.1 Criar .github/workflows/tests.yml

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/ -v --cov=.
      - uses: codecov/codecov-action@v3
```

### 4.2 Criar .github/workflows/docker-build.yml

```yaml
name: Docker Build

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: docker/setup-buildx-action@v2
      - run: docker build -t ifs-chatbot:latest .
      - run: docker run --rm ifs-chatbot:latest python -m pytest tests/ -q
```

---

## 📦 FASE 5: ESTRUTURA DE REPOSITÓRIO (10 minutos)

### 5.1 Organizar Diretórios

```
projeto-chatbot-ifs/
├── .github/
│   ├── workflows/
│   │   ├── tests.yml
│   │   └── docker-build.yml
│   └── ISSUE_TEMPLATE/
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── FIX4_DETAILS.md
│   ├── DEPLOYMENT.md
│   └── API.md
│
├── etl_scripts/
│   ├── main.py
│   ├── extractor.py
│   └── ...
│
├── tests/
│   ├── test_agents.py
│   ├── test_database.py
│   └── test_integration.py
│
├── app_v2.py
├── crew_definition_v2.py
├── tools.py
├── db_connection.py
├── requirements.txt
├── requirements_locked.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── .env.example
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
└── LICENSE
```

---

## ✨ FASE 6: LIMPEZA FINAL (10 minutos)

### 6.1 Remover Arquivos de Debug Mantendo Essenciais

Manter documentação técnica importante:
```
MANTER:
- ANALISE_GAPS_TESTE_MANUAL.md (histórico de bugs)
- FIX_4_COMPLETADO.md (documentação de fix)
- GUIA_COMPLETO_USUARIO.md (user guide)
- IMPLEMENTACAO_*.md (histórico)

REMOVER:
- test_simples_output.txt
- test_output_comparacao.txt
- debug_*.log
- test_*.txt
```

### 6.2 Git Operations

```bash
# 1. Add documentação profissional
git add docs/ CHANGELOG.md CONTRIBUTING.md

# 2. Remover arquivos não necessários
git rm test_simples_output.txt test_output_comparacao.txt comparacao_manual_vs_automatico.txt ...

# 3. Commit profissional
git commit -m "feat: Dockerization & GitHub-ready release v2.0

- Update Dockerfile to Python 3.13
- Add docker-compose with MySQL & Adminer
- Add GitHub Actions CI/CD workflows
- Add professional documentation (CHANGELOG, CONTRIBUTING, DEVELOPMENT)
- Clean up test artifacts and logs
- Fix 4: Database discovery, logging, intent detection improvements
- Pergunta 1 now passes with 95% confidence

See CHANGELOG.md for detailed release notes"

# 4. Tag versão
git tag -a v2.0.0 -m "Release v2.0.0 - FIX 4 Complete"

# 5. Push
git push origin main --tags
```

---

## 🚀 FASE 7: PUBLICAÇÃO (5 minutos)

### 7.1 GitHub Repository Setup

- [ ] Adicionar description: "IFS Chatbot - AI-powered financial transparency"
- [ ] Adicionar topics: `creawai`, `streamlit`, `chatbot`, `financial-data`, `python`
- [ ] Configurar branch protection (main)
- [ ] Enable GitHub Pages (para docs)
- [ ] Adicionar LICENSE (MIT ou Apache 2.0)

### 7.2 Testar com Docker

```bash
# Build image
docker build -t ifs-chatbot:2.0.0 .

# Run single container (without docker-compose)
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=xxx \
  -e DB_HOST=mysql.example.com \
  ifs-chatbot:2.0.0

# Run full stack (with docker-compose)
docker-compose up -d
# Acesse: http://localhost:8501
```

---

## 📋 CHECKLIST FINAL

- [ ] **Documentação**
  - [ ] README.md atualizado com FIX 4
  - [ ] CHANGELOG.md criado
  - [ ] CONTRIBUTING.md criado
  - [ ] DEVELOPMENT.md criado
  - [ ] docs/ folder criado com arquitetura

- [ ] **Docker**
  - [ ] Dockerfile atualizado (Python 3.13)
  - [ ] docker-compose.yml validado
  - [ ] .dockerignore criado/atualizado
  - [ ] Build & test localmente

- [ ] **GitHub**
  - [ ] .github/workflows/ criado
  - [ ] GitHub Actions CI/CD configurado
  - [ ] Tests passando
  - [ ] Docker build passando

- [ ] **Limpeza**
  - [ ] Arquivos temporários removidos
  - [ ] .gitignore revisado
  - [ ] Secrets (.env) não commited
  - [ ] .env.example atualizado

- [ ] **Versionamento**
  - [ ] Versão tagged (v2.0.0)
  - [ ] CHANGELOG preenchido
  - [ ] Commit mensagem profissional

---

## 📊 TEMPO ESTIMADO TOTAL
- **Fase 1**: 15 min ✅
- **Fase 2**: 30 min ✅
- **Fase 3**: 20 min ✅
- **Fase 4**: 15 min ✅
- **Fase 5**: 10 min ✅
- **Fase 6**: 10 min ✅
- **Fase 7**: 5 min ✅

**TOTAL: ~2 horas de trabalho**

---

## 🎓 Resultado Final

Projeto pronto para:
- ✅ Publicação profissional no GitHub
- ✅ Docker Hub deployment
- ✅ CI/CD automation
- ✅ Contribuições da comunidade
- ✅ Deploy em produção
