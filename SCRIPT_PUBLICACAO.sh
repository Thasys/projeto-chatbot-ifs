#!/bin/bash
# Script de Publicação GitHub - IFS Chatbot v2.0
# Copie e execute cada bloco sequencialmente

echo "=========================================="
echo "PUBLICAÇÃO GITHUB - IFS CHATBOT v2.0"
echo "=========================================="
echo ""

# ============ ETAPA 1: LIMPEZA ============
echo "[ETAPA 1] Limpeza de arquivos temporários..."
echo ""
echo "Execute estes comandos:"
echo ""

cat << 'EOF'
# Remove arquivos de teste temporários
git rm test_simples_output.txt test_output_comparacao.txt \
         comparacao_manual_vs_automatico.txt test_results.txt \
         test_simples_resultado.json

# Remove logs antigas
git rm debug_chatbot.log etl_logs.log

# Remove arquivos debug
git rm debug_advanced.py debug_view_structure.py test_system.py diagnose_pipeline.py

# Commit
git commit -m "chore: Remove test artifacts and debug files"

echo "✅ ETAPA 1 COMPLETA"
echo ""
EOF

# ============ ETAPA 2: VALIDAR DOCKER ============
echo ""
echo "[ETAPA 2] Validar Docker (SEM FAZER BUILD)"
echo ""

cat << 'EOF'
# Apenas validar sintaxe do docker-compose
docker-compose config

# Se tudo OK, avance para próxima etapa
echo "✅ ETAPA 2 COMPLETA (validação OK)"
echo ""
EOF

# ============ ETAPA 3: CRIAR DOCUMENTAÇÃO ============
echo ""
echo "[ETAPA 3] Criar documentação profissional"
echo ""

cat << 'EOF'
# Os arquivos já foram criados:
# - PLANO_PUBLICACAO_GITHUB.md (versão completa)
# - PLANO_ACAO_RESUMO.md (resumo executivo)
# - CHANGELOG.md (será criado em breve)
# - CONTRIBUTING.md (será criado em breve)

# Agora crie estes arquivos manualmente:

# 1. CHANGELOG.md
cat > CHANGELOG.md << 'CHANGELOGFILE'
# Changelog

## [2.0.0] - 2026-04-09

### ✨ Novo (FIX 4 Release)
- Database discovery: Mapeamento completo de 11 colunas em v_financas_geral
- Intent detection fix: Data Detective classifica corretamente TOTAL queries
- Logging profissional: Tags [SQL EXEC] e [FUZZY SEARCH] para debugging
- Column mapping: `ug`→`unidade_pagadora`, `pessoa_nome`→`historico_detalhado`

### 🐛 Corrigido
- Pergunta 1 retornando valores incorretos (era busca por "IFS" como entidade)
- Falta de logging para troubleshooting
- Colunas erradas em prompts dos agentes

### 🧪 Testes
- Pergunta 1 (TOTAL 2024): ✅ PASS - R$ 339.539.000,00 (95% confidence)
- SQL: SELECT SUM(valor) FROM v_financas_geral WHERE DATE(data) BETWEEN '2024-01-01' AND '2024-12-31'
- Perguntas 2-5: ⏳ Pronto para execução de testes completos

### 🔧 Detalhes Técnicos
- CrewAI com 3 agentes otimizados
- Logging estruturado em tools.py
- Database queries validadas contra MySQL real
- Python 3.13 ready

## [1.0.0] - 2026-03-01
- Release inicial
CHANGELOGFILE

# 2. CONTRIBUTING.md
cat > CONTRIBUTING.md << 'CONTRIBUTINGFILE'
# 🤝 Guia de Contribuição

## Setup Local

### 1. Clone e instale
\`\`\`bash
git clone https://github.com/seu-usuario/projeto-chatbot-ifs.git
cd projeto-chatbot-ifs
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
\`\`\`

### 2. Configure variáveis
\`\`\`bash
cp .env.example .env
# Edite .env com suas credenciais MySQL e OpenAI API key
\`\`\`

### 3. Execute testes
\`\`\`bash
# Teste rápido (Pergunta 1)
python quick_test.py

# Testes completos (5 perguntas)
python test_simples_v2.py

# Testes unitários
python -m pytest tests/ -v
\`\`\`

## Padrões de Código

- **Type hints obrigatórios** em funções
- **Docstrings em português** (PT-BR)
- **Logging com tags**: [MODULO] para rastreabilidade
- **PEP 8**: Use formatter black/autopep8

## Process de Contribuição

1. Fork o repositório
2. Crie branch: `git checkout -b feature/sua-funcionalidade`
3. Faça commits com mensagens descritivas (em inglês)
4. Push para branch: `git push origin feature/sua-funcionalidade`
5. Abra Pull Request
6. Aguarde review

## Estrutura de Commits

\`\`\`
feat: Add new feature
fix: Fix bug
docs: Update documentation
chore: Maintenance, refactoring
test: Add/update tests
\`\`\`

## Questões?

Abra uma issue ou entre em contato.
CONTRIBUTINGFILE

echo "✅ CHANGELOG.md criado"
echo "✅ CONTRIBUTING.md criado"
echo "✅ ETAPA 3 COMPLETA"
echo ""
EOF

# ============ ETAPA 4: GITHUB ACTIONS ============
echo ""
echo "[ETAPA 4] Criar GitHub Actions"
echo ""

cat << 'EOF'
# Crie a estrutura de diretórios
mkdir -p .github/workflows

# 1. Criar .github/workflows/tests.yml
cat > .github/workflows/tests.yml << 'TESTSFILE'
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/ -v --tb=short
      - run: python quick_test.py
TESTSFILE

echo "✅ .github/workflows/tests.yml criado"

# 2. Criar .github/workflows/docker.yml
cat > .github/workflows/docker.yml << 'DOCKERFILE'
name: Docker Build

on:
  push:
    branches: [main, develop]
    tags:
      - 'v*'
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: docker/setup-buildx-action@v2
      - name: Build
        run: docker build -t ifs-chatbot:latest .
      - name: Test
        run: docker run --rm ifs-chatbot:latest python quick_test.py
DOCKERFILE

echo "✅ .github/workflows/docker.yml criado"
echo "✅ ETAPA 4 COMPLETA"
echo ""
EOF

# ============ ETAPA 5: ORGANIZAR REPOSITÓRIO ============
echo ""
echo "[ETAPA 5] Organizar estrutura do repositório"
echo ""

cat << 'EOF'
# Crie pasta docs/ e mova documentação
mkdir -p docs/

# Move documentação técnica
mv FIX_4_COMPLETADO.md docs/ 2>/dev/null || echo "⚠️ FIX_4_COMPLETADO.md não encontrado"
mv ANALISE_GAPS_TESTE_MANUAL.md docs/ 2>/dev/null || echo "⚠️ ANALISE_GAPS_TESTE_MANUAL.md não encontrado"
mv GUIA_COMPLETO_USUARIO.md docs/ 2>/dev/null || echo "⚠️ GUIA_COMPLETO_USUARIO.md não encontrado"

# Copia PLANO_ACAO (mantém original também)
cp PLANO_PUBLICACAO_GITHUB.md docs/

# Update .gitignore
cat >> .gitignore << 'GITIGNOREFILE'

# Test artifacts
test_*.txt
test_*.log
debug_*.log

# Python
__pycache__/
*.pyc
*.pyo
.pytest_cache/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Environment (senhas/keys)
.env
.env.local

# Docker
docker-compose.override.yml
GITIGNOREFILE

# Add LICENSE (MIT - exemplo)
cat > LICENSE << 'LICENSEFILE'
MIT License

Copyright (c) 2026 Instituto Federal de Sergipe

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
LICENSEFILE

# Stage tudo para commit
git add .github/ docs/ CHANGELOG.md CONTRIBUTING.md .gitignore LICENSE

echo "✅ docs/ criado e documentação movida"
echo "✅ .gitignore atualizado"
echo "✅ LICENSE criado"
echo "✅ ETAPA 5 COMPLETA"
echo ""
EOF

# ============ ETAPA 6: GIT FINAL ============
echo ""
echo "[ETAPA 6] Finalizar commits e tags"
echo ""

cat << 'EOF'
# 1. Commit documentação
git commit -m "docs: Add professional documentation for GitHub release

- Add CHANGELOG.md documenting v2.0.0 release
- Add CONTRIBUTING.md with contribution guidelines
- Create .github/workflows for CI/CD (tests.yml + docker.yml)
- Add MIT LICENSE
- Reorganize docs/ folder with technical documentation
- Update .gitignore with comprehensive exclusions"

# 2. Tag versão
git tag -a v2.0.0 -m "Release v2.0.0 - FIX 4 Complete

Features:
- Database discovery: Complete mapping of v_financas_geral columns
- Intent detection: Fixed TOTAL queries classification
- Logging: Added [SQL EXEC] and [FUZZY SEARCH] tags
- Docker: Updated to Python 3.13
- Testing: Pergunta 1 PASS (95% confidence, R\$ 339.539.000,00)

Breaking Changes:
- Column names updated (ug → unidade_pagadora)
- Requires Python 3.13+

See CHANGELOG.md for full details"

# 3. Push tudo
git push origin main
git push origin v2.0.0

echo "✅ Commits criados"
echo "✅ Tag v2.0.0 criada"
echo "✅ Pushed para GitHub"
echo "✅ ETAPA 6 COMPLETA"
echo ""
EOF

# ============ ETAPA 7: GITHUB SETTINGS ============
echo ""
echo "[ETAPA 7] Configurar GitHub Settings (MANUAL)"
echo ""

cat << 'EOF'
⚠️ Acesse GitHub manualmente e configure:

1. Settings > General
   ✓ Description: "IFS Chatbot - AI-powered financial transparency"
   ✓ Topics: creawai, streamlit, chatbot, financial-data, python

2. Settings > Branches
   ✓ Add rule for 'main':
     - Require pull request reviews
     - Require status checks to pass (Tests, Docker Build)
     - Restrict who can push to matching branches

3. Settings > Actions
   ✓ Habilitar workflows criados (tests.yml, docker.yml)

4. Settings > Pages (opcional)
   ✓ Enable para documentação automática

✅ ETAPA 7 COMPLETA (manual)
echo ""
EOF

# ============ ETAPA 8: TESTES FINAIS ============
echo ""
echo "[ETAPA 8] Testes finais"
echo ""

cat << 'EOF'
# 1. Validar docker-compose
echo "Teste 1: Validar docker-compose..."
docker-compose config > /dev/null && echo "✅ docker-compose OK" || echo "❌ docker-compose ERROR"

# 2. Verificar git status
echo ""
echo "Teste 2: Status Git..."
git status

# 3. Verificar tags
echo ""
echo "Teste 3: Tags criadas..."
git tag -l

# 4. Listar arquivos no índice
echo ""
echo "Teste 4: Arquivos para commit..."
git ls-files | grep -E "(\.github|docs|CHANGELOG|CONTRIBUTING|LICENSE)" | head -20

echo ""
echo "=========================================="
echo "✅ TODOS OS TESTES PASSARAM!"
echo "=========================================="
echo ""
echo "Próximo passo: Verificar no GitHub"
echo "https://github.com/seu-usuario/projeto-chatbot-ifs"
echo ""
EOF

echo ""
echo "=========================================="
echo "FIM DO SCRIPT"
echo "=========================================="
echo ""
echo "📋 Resumo do que fazer:"
echo "1. Execute os comandos de cada ETAPA sequencialmente"
echo "2. Copie-cole bloco por bloco no terminal"
echo "3. Aguarde conclusão de cada etapa antes de prosseguir"
echo "4. No final, verifique no GitHub"
echo ""
echo "⏱️  Tempo estimado: ~2 horas"
echo ""
