# 🎯 PLANO DE AÇÃO - RESUMO EXECUTIVO

## Objetivo Final
Atualizar Docker do projeto IFS Chatbot para Python 3.13, criar documentação profissional e publicar no GitHub em formato pronto para produção.

---

## 📑 ETAPAS (Em Ordem)

### **ETAPA 1: Limpeza (10 minutos)**
```bash
# 1. Remover arquivos de teste temporários
git rm test_simples_output.txt test_output_comparacao.txt \
         comparacao_manual_vs_automatico.txt test_results.txt \
         test_simples_resultado.json

# 2. Remover logs antigas
git rm debug_chatbot.log etl_logs.log

# 3. Remover arquivos debug
git rm debug_advanced.py debug_view_structure.py test_system.py diagnose_pipeline.py

# 4. Commit limpeza
git commit -m "chore: Remove test artifacts and debug files"
```

---

### **ETAPA 2: Atualizar Docker (15 minutos)**

#### 2.1 **Novo Dockerfile** (Python 3.9 → 3.13)
```dockerfile
# Multi-stage: builder + production
FROM python:3.13-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.13-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_HEADLESS=true STREAMLIT_SERVER_PORT=8501
RUN mkdir -p reports dados_brutos etl_scripts .streamlit
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY . .
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501').read()"
RUN chmod -R 755 /app
EXPOSE 8501
LABEL version="2.0.0" description="IFS Chatbot - AI-powered Financial Transparency"
CMD ["streamlit", "run", "app_v2.py", "--server.address=0.0.0.0"]
```

#### 2.2 **Verificar docker-compose.yml**
```bash
# Validar sintaxe
docker-compose config

# Testar build
docker-compose build

# Testar run
docker-compose up -d
docker-compose logs -f
docker-compose down
```

---

### **ETAPA 3: Criar Documentação Profissional (25 minutos)**

#### 3.1 **Atualizar README.md**

Adicionar seções:
```markdown
# IFS Transparência Inteligente - v2.0

[Banner/Logo ASCII art]

## Status do Projeto
✅ **Production Ready** - FIX 4: Intent Detection & Database Optimizations

## Mudanças Recentes (v2.0)
- Pergunta 1 (TOTAL 2024): ✅ PASS (R$ 339.539.000,00)
- Database Discovery: Todas 11 colunas mapeadas
- Logging: [SQL EXEC] e [FUZZY SEARCH] tags adicionadas
- Intent Fix: Data Detective classifica corretamente TOTAL queries

## Quick Start (Docker)
\`\`\`bash
docker-compose up
# Acesse http://localhost:8501
\`\`\`

[resto do README...]
```

#### 3.2 **Criar CHANGELOG.md**
```markdown
# Changelog

## [2.0.0] - 2026-04-09

### ✨ Novo (FIX 4)
- Database discovery completa de v_financas_geral
- Intent detection fix para TOTAL queries
- Logging profissional [SQL EXEC] e [FUZZY SEARCH]

### 🐛 Corrigido
- Pergunta 1 retornando valores incorretos
- Colunas wrong (ug→unidade_pagadora, pessoa_nome→historico_detalhado)
- Falta de logging para debug

### 🧪 Testes
- Pergunta 1: ✅ PASS (95% confidence)
- Perguntas 2-5: ⏳ Pronto para teste
```

#### 3.3 **Criar CONTRIBUTING.md**
```markdown
# 🤝 Contribuindo

## Setup Local
\`\`\`bash
git clone <repo>
cd projeto-chatbot-ifs
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
\`\`\`

## Testes
\`\`\`bash
python -m pytest tests/ -v
python quick_test.py  # Single question test
python test_simples_v2.py  # Full 5-question test
\`\`\`
```

#### 3.4 **Criar docs/FIX4_DETAILS.md**
Documento técnico detalhando:
- Root causes identificadas
- Soluções implementadas
- Arquivos modificados
- Testes validados

---

### **ETAPA 4: GitHub Actions CI/CD (15 minutos)**

#### 4.1 **Criar `.github/workflows/tests.yml`**
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
      - run: python -m pytest tests/ --tb=short
```

#### 4.2 **Criar `.github/workflows/docker.yml`**
```yaml
name: Docker Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: docker/setup-buildx-action@v2
      - run: docker build -t ifs-chatbot:latest .
      - run: docker run --rm ifs-chatbot:latest python quick_test.py
```

---

### **ETAPA 5: Organizar Repositório (10 minutos)**

```bash
# Criar estrutura
mkdir -p docs/

# Mover documentação técnica
mv FIX_4_COMPLETADO.md docs/
mv ANALISE_GAPS_TESTE_MANUAL.md docs/
mv GUIA_COMPLETO_USUARIO.md docs/

# Atualizar .gitignore (adicionar)
echo "*.log" >> .gitignore
echo "test_*.txt" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore

git add docs/ .gitignore CHANGELOG.md CONTRIBUTING.md PLANO_PUBLICACAO_GITHUB.md
git commit -m "docs: Add professional documentation for GitHub"
```

---

### **ETAPA 6: Git Final (10 minutos)**

```bash
# 1. Verify tudo está em ordem
git status

# 2. Tag versão
git tag -a v2.0.0 -m "Release v2.0.0 - FIX 4 Complete, Docker Update, Production Ready"

# 3. Push com tags
git push origin main --tags

# 4. Verificar no GitHub
# https://github.com/seu-user/projeto-chatbot-ifs/releases
```

---

### **ETAPA 7: GitHub Repository Settings (5 minutos)**

No GitHub, ir para `Settings`:

- [ ] **General**
  - Description: "IFS Chatbot - AI-powered financial transparency"
  - Homepage: (se houver url)
  - Topics: `creawai`, `streamlit`, `chatbot`, `financial-data`, `python`

- [ ] **Branch Protection** (main)
  - Require PR reviews
  - Require status checks (Tests)

- [ ] **Secrets** (não necessário para este projeto público)

- [ ] **Actions**: Habilitar workflows criados

---

### **ETAPA 8: Testar Tudo (10 minutos)**

```bash
# Teste 1: Build Docker
docker build -t ifs-chatbot:2.0.0 .

# Teste 2: Run com docker-compose
docker-compose up -d mysql app1
docker-compose ps
docker-compose logs -f app1
# Acesse http://localhost:8501
docker-compose down

# Teste 3: Verificar arquivo layout
git ls-files | head -20

# Teste 4: Verificar tags
git tag -l
```

---

## ✅ CHECKLIST FINAL

**Antes de publicar:**

- [ ] Dockerfile atualizado para Python 3.13
- [ ] docker-compose.yml validado
- [ ] README.md atualizado com FIX 4 info
- [ ] CHANGELOG.md criado
- [ ] CONTRIBUTING.md criado
- [ ] .github/workflows criado (tests.yml + docker.yml)
- [ ] Arquivos temporários removidos
- [ ] .gitignore atualizado
- [ ] .env.example tem todas variáveis necessárias
- [ ] Versão tagada (v2.0.0)
- [ ] Commit mensagem profissional
- [ ] Push para main com tags
- [ ] GitHub repo settings atualizado
- [ ] License arquivo adicionado (MIT/Apache)

---

## 📊 TEMPO TOTAL
- Etapa 1 (Limpeza): **10 min**
- Etapa 2 (Docker): **15 min**
- Etapa 3 (Documentação): **25 min**
- Etapa 4 (GitHub Actions): **15 min**
- Etapa 5 (Organizar): **10 min**
- Etapa 6 (Git): **10 min**
- Etapa 7 (GitHub Settings): **5 min**
- Etapa 8 (Testes): **10 min**

**⏱️ TEMPO TOTAL: ~2 HORAS**

---

## 🚀 Resultado Final

✅ Projeto pronto para:
- Publicação profissional no GitHub
- Deployment em Docker
- Contribuições da comunidade
- Ci/CD automation
- Produção

---

## 📞 Dúvidas?

Consulte:
- `PLANO_PUBLICACAO_GITHUB.md` - Versão detalhada com exemplos
- `docs/FIX4_DETAILS.md` - Detalhes técnicos do FIX 4
- `CONTRIBUTING.md` - Como contribuir
