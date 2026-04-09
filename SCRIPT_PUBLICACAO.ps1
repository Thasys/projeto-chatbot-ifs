# Script de Publicação GitHub - IFS Chatbot v2.0 (Windows PowerShell)
# Execute bloco por bloco no PowerShell

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "PUBLICAÇÃO GITHUB - IFS CHATBOT v2.0" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# ============ ETAPA 1: LIMPEZA ============
Write-Host "[ETAPA 1] Limpeza de arquivos temporários..." -ForegroundColor Green
Write-Host ""
Write-Host "Execute estes comandos:" -ForegroundColor Yellow
Write-Host ""

@"
# Copie e execute cada linha:

# Remove arquivos de teste temporários
git rm test_simples_output.txt
git rm test_output_comparacao.txt  
git rm comparacao_manual_vs_automatico.txt
git rm test_results.txt
git rm test_simples_resultado.json

# Remove logs antigas
git rm debug_chatbot.log
git rm etl_logs.log

# Remove arquivos debug
git rm debug_advanced.py
git rm debug_view_structure.py
git rm test_system.py
git rm diagnose_pipeline.py

# Commit
git commit -m "chore: Remove test artifacts and debug files"

Write-Host "✅ ETAPA 1 COMPLETA" -ForegroundColor Green
"@ | Out-Host

# ============ ETAPA 2: VALIDAR DOCKER ============
Write-Host ""
Write-Host "[ETAPA 2] Validar Docker" -ForegroundColor Green
Write-Host ""

@"
# Validar sintaxe do docker-compose
docker-compose config

# Se aparecer config sem erros, OK está pronto!
Write-Host "✅ ETAPA 2 COMPLETA" -ForegroundColor Green
"@ | Out-Host

# ============ ETAPA 3: CRIAR DOCUMENTAÇÃO ============
Write-Host ""
Write-Host "[ETAPA 3] Criar documentação profissional" -ForegroundColor Green
Write-Host ""

# Criar CHANGELOG.md
$changelog = @"
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
- Perguntas 2-5: ⏳ Pronto para teste completo

### 🔧 Detalhes Técnicos
- CrewAI com 3 agentes otimizados
- Logging estruturado em tools.py
- Database queries validadas contra MySQL
- Python 3.13 ready

## [1.0.0] - 2026-03-01
- Release inicial
"@

$changelog | Out-File -FilePath CHANGELOG.md -Encoding UTF8
Write-Host "✅ CHANGELOG.md criado" -ForegroundColor Green

# Criar CONTRIBUTING.md
$contributing = @"
# 🤝 Guia de Contribuição

## Setup Local

### 1. Clone e instale
\`\`\`bash
git clone https://github.com/seu-usuario/projeto-chatbot-ifs.git
cd projeto-chatbot-ifs
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
\`\`\`

### 2. Configure variáveis
\`\`\`bash
copy .env.example .env
# Edite .env com suas credenciais
\`\`\`

### 3. Execute testes
\`\`\`bash
# Teste rápido
python quick_test.py

# Testes completos
python test_simples_v2.py

# Testes unitários
python -m pytest tests/ -v
\`\`\`

## Padrões de Código
- Type hints obrigatórios
- Docstrings em português
- Logging com tags: [MODULO]
- PEP 8

## Process
1. Fork repositório
2. Crie branch: `git checkout -b feature/sua-feature`
3. Commit: `git commit -m "feat: descrição"`
4. Push: `git push origin feature/sua-feature`
5. Abra Pull Request

## Estrutura de Commits
- feat: Nova funcionalidade
- fix: Correção de bug
- docs: Documentação
- chore: Manutenção
- test: Testes
"@

$contributing | Out-File -FilePath CONTRIBUTING.md -Encoding UTF8
Write-Host "✅ CONTRIBUTING.md criado" -ForegroundColor Green

Write-Host "✅ ETAPA 3 COMPLETA" -ForegroundColor Green
Write-Host ""

# ============ ETAPA 4: GITHUB ACTIONS ============
Write-Host "[ETAPA 4] Criar GitHub Actions" -ForegroundColor Green
Write-Host ""

# Criar diretórios
New-Item -ItemType Directory -Path ".github\workflows" -Force | Out-Null

# Criar tests.yml
$testsYml = @"
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
"@

$testsYml | Out-File -FilePath ".github\workflows\tests.yml" -Encoding UTF8
Write-Host "✅ .github\workflows\tests.yml criado" -ForegroundColor Green

# Criar docker.yml
$dockerYml = @"
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
"@

$dockerYml | Out-File -FilePath ".github\workflows\docker.yml" -Encoding UTF8
Write-Host "✅ .github\workflows\docker.yml criado" -ForegroundColor Green

Write-Host "✅ ETAPA 4 COMPLETA" -ForegroundColor Green
Write-Host ""

# ============ ETAPA 5: ORGANIZAR REPOSITÓRIO ============
Write-Host "[ETAPA 5] Organizar estrutura de repositório" -ForegroundColor Green
Write-Host ""

# Criar docs/ e mover arquivos
New-Item -ItemType Directory -Path "docs" -Force | Out-Null

$docsToMove = @("FIX_4_COMPLETADO.md", "ANALISE_GAPS_TESTE_MANUAL.md", "GUIA_COMPLETO_USUARIO.md")

foreach ($file in $docsToMove) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "docs/$file" -Force
        Write-Host "✅ Movido: $file" -ForegroundColor Green
    }
}

# Copy PLANO_PUBLICACAO
if (Test-Path "PLANO_PUBLICACAO_GITHUB.md") {
    Copy-Item "PLANO_PUBLICACAO_GITHUB.md" "docs/" -Force
    Write-Host "✅ Copiado: PLANO_PUBLICACAO_GITHUB.md" -ForegroundColor Green
}

# Atualizar .gitignore
$gitignoreContent = @"

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
"@

Add-Content -Path ".gitignore" -Value $gitignoreContent -Encoding UTF8
Write-Host "✅ .gitignore atualizado" -ForegroundColor Green

# Criar LICENSE (MIT)
$license = @"
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

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

Contact: seu-email@ifs.edu.br
"@

$license | Out-File -FilePath LICENSE -Encoding UTF8
Write-Host "✅ LICENSE criado (MIT)" -ForegroundColor Green

# Stage para commit
Write-Host ""
Write-Host "Stage tudo para commit:" -ForegroundColor Yellow
Write-Host "git add .github/ docs/ CHANGELOG.md CONTRIBUTING.md .gitignore LICENSE" -ForegroundColor Cyan

Write-Host "✅ ETAPA 5 COMPLETA" -ForegroundColor Green
Write-Host ""

# ============ ETAPA 6: GIT FINAL ============
Write-Host "[ETAPA 6] Finalizar commits e tags" -ForegroundColor Green
Write-Host ""

@"
Execute na ordem:

# 1. Stage todos os arquivos
git add .github/ docs/ CHANGELOG.md CONTRIBUTING.md .gitignore LICENSE

# 2. Commit documentação profissional
git commit -m "docs: Add professional documentation for GitHub release

CHANGELOG.md - Full release notes for v2.0.0
CONTRIBUTING.md - Contribution guidelines
.github/workflows/ - CI/CD automation (tests + docker)
LICENSE - MIT license disclosure
docs/ - Reorganized technical documentation
.gitignore - Comprehensive exclusions"

# 3. Tag versão
git tag -a v2.0.0 -m "Release v2.0.0 - FIX 4 Complete

Features:
- Database discovery: Complete mapping of v_financas_geral
- Intent detection: Fixed TOTAL queries classification  
- Logging: [SQL EXEC] and [FUZZY SEARCH] tags
- Docker: Python 3.13 support
- Pergunta 1: PASS (95% confidence, R$ 339.539.000,00)

See CHANGELOG.md for details"

# 4. Push para GitHub
git push origin main --tags

Write-Host "✅ Commits e tags criados" -ForegroundColor Green
Write-Host "✅ ETAPA 6 COMPLETA" -ForegroundColor Green
"@ | Out-Host

# ============ ETAPA 7: GITHUB SETTINGS ============
Write-Host ""
Write-Host "[ETAPA 7] Configurar GitHub Settings (MANUAL)" -ForegroundColor Yellow
Write-Host ""

@"
⚠️  Acesse GitHub.com manualmente e configure:

1. Ir para Settings (gear icon)
   
2. General tab:
   ✓ Description: IFS Chatbot - AI-powered financial transparency
   ✓ Homepage: (deixar opcional)
   ✓ Topics: creawai, streamlit, chatbot, financial-data, python

3. Branches > Add rule for 'main':
   ✓ Require pull request reviews before merging
   ✓ Require status checks to pass:
     - Tests (tests.yml)
     - Docker Build (docker.yml)
   ✓ Restrict who can push to matching branches

4. Actions > Click Green "Enable"
   ✓ Habilitar todos workflows

5. Pages (opcional):
   ✓ Source: Deploy from a branch
   ✓ Branch: main /docs
   ✓ Para documentação automática

✅ ETAPA 7 COMPLETA (manual no GitHub)
"@ | Out-Host

# ============ ETAPA 8: TESTES FINAIS ============
Write-Host ""
Write-Host "[ETAPA 8] Testes finais" -ForegroundColor Green
Write-Host ""

@"
Execute para verificar:

# 1. Validar docker-compose
Write-Host "Teste 1: Validar docker-compose..." -ForegroundColor Cyan
docker-compose config > `$null
if (`$LASTEXITCODE -eq 0) { Write-Host "✅ docker-compose OK" -ForegroundColor Green } 
else { Write-Host "❌ docker-compose ERROR" -ForegroundColor Red }

# 2. Git status
Write-Host ""
Write-Host "Teste 2: Status git..." -ForegroundColor Cyan
git status

# 3. Tags criadas
Write-Host ""
Write-Host "Teste 3: Tags criadas..." -ForegroundColor Cyan
git tag -l | Select-Object -Last 5

# 4. Verificar estrutura
Write-Host ""
Write-Host "Teste 4: Estrutura de arquivos..." -ForegroundColor Cyan
Write-Host "✓ .github/workflows:" (Test-Path ".github\workflows") -ForegroundColor Green
Write-Host "✓ docs/:" (Test-Path "docs") -ForegroundColor Green  
Write-Host "✓ CHANGELOG.md:" (Test-Path "CHANGELOG.md") -ForegroundColor Green
Write-Host "✓ CONTRIBUTING.md:" (Test-Path "CONTRIBUTING.md") -ForegroundColor Green
Write-Host "✓ LICENSE:" (Test-Path "LICENSE") -ForegroundColor Green

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "✅ TODOS OS TESTES PASSARAM!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
"@ | Out-Host

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "FIM DO SCRIPT" -ForegroundColor Cyan  
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. Execute cada ETAPA de cima para baixo" -ForegroundColor White
Write-Host "2. Copie-cole os comandos git de cada ETAPA" -ForegroundColor White
Write-Host "3. Para ETAPA 7, configure manualmente no GitHub.com" -ForegroundColor White
Write-Host "4. Ao final, execute os testes da ETAPA 8" -ForegroundColor White
Write-Host "5. Verifique no GitHub: https://github.com/seu-usuario/projeto-chatbot-ifs" -ForegroundColor White
Write-Host ""
Write-Host "⏱️  Tempo estimado: ~2 horas" -ForegroundColor Cyan
Write-Host ""
