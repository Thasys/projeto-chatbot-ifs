# ⚡ REFERÊNCIA RÁPIDA - Publicação GitHub v2.0

Guia quick-reference para consulta durante a execução.

---

## 📍 Localização Rápida

| Preciso... | Abra isto |
|-----------|-----------|
| Entender o plano | `PLANO_ACAO_RESUMO.md` |
| Detalhes completos | `PLANO_PUBLICACAO_GITHUB.md` |
| Executar as etapas | `SCRIPT_PUBLICACAO.ps1` (Windows) |
| Executar as etapas | `SCRIPT_PUBLICACAO.sh` (Linux/Mac) |
| Ver visualmente | `PLANO_VISUAL.md` |
| Navegar documentos | `INDICE_PUBLICACAO.md` |
| Começar agora | `LEIA-ME-PRIMEIRO.txt` |

---

## 🎯 As 8 Etapas em Uma Página

### **ETAPA 1: Limpeza (10 min)**
```bash
git rm test_*.txt test_results.json comparacao_*.txt debug_*.log
git rm debug_advanced.py debug_view_structure.py test_system.py diagnose_pipeline.py
git commit -m "chore: Remove test artifacts and debug files"
```

### **ETAPA 2: Validar Docker (5 min)**
```bash
docker-compose config
# Deve retornar config sem erros
```

### **ETAPA 3: Criar Documentação (25 min)**
Criar 3 arquivos:
- `CHANGELOG.md` - Release notes (template no script)
- `CONTRIBUTING.md` - Guia de contribuição (template no script)
- `LICENSE` - MIT License (template no script)

### **ETAPA 4: GitHub Actions (15 min)**
Criar estrutura:
```
.github/workflows/
  ├── tests.yml (CI/CD para testes Python)
  └── docker.yml (CI/CD para build Docker)
```

### **ETAPA 5: Organizar (10 min)**
```bash
mkdir -p docs/
mv FIX_4_COMPLETADO.md docs/
mv ANALISE_GAPS_TESTE_MANUAL.md docs/
# Atualizar .gitignore
# Criar LICENSE
```

### **ETAPA 6: Git Final (10 min)**
```bash
git add .github/ docs/ CHANGELOG.md CONTRIBUTING.md .gitignore LICENSE
git commit -m "docs: Add professional documentation for GitHub release..."
git tag -a v2.0.0 -m "Release v2.0.0 - FIX 4 Complete..."
git push origin main --tags
```

### **ETAPA 7: GitHub Settings (5 min) ⚠️ MANUAL**
- Ir para Settings > General
- Adicionar description + topics
- Ir para Settings > Branches
- Adicionar rule para `main` (require PR reviews)
- Ir para Settings > Actions
- Habilitar workflows

### **ETAPA 8: Testes (10 min)**
```bash
docker-compose config
git status
git tag -l
# Verificar em GitHub
```

---

## 💻 Comandos Git Mais Usados

```bash
# Ver status
git status

# Ver tags
git tag -l

# Ver commits recentes
git log --oneline -5

# Ver qual branch está
git branch

# Ver o que vai commit
git diff --cached

# Desfazer último commit (se errou)
git reset --soft HEAD~1

# Ver tags remotas
git ls-remote --tags origin
```

---

## 🚨 Se Algo Deu Errado

| Erro | Solução |
|------|---------|
| "Permission denied" | Use `git` com URL em vez de SSH ou adicione chave |
| "File already exists" | O arquivo já foi criado, delete ou renomeie |
| "docker-compose not found" | Instale Docker Desktop ou Docker Compose |
| "Branch conflicts" | Atualize main: `git pull origin main` |
| "Tag já existe" | Delete e recrie: `git tag -d v2.0.0` depois `git tag ...` |

Consulte `PLANO_PUBLICACAO_GITHUB.md` > Troubleshooting para mais.

---

## 📊 Checklist de Controle

```
ANTES DE COMEÇAR
  [ ] Git instalado? `git --version`
  [ ] GitHub conta? Acesse github.com
  [ ] Pasta do projeto? `cd projeto-chatbot-ifs`

DURANTE EXECUÇÃO
  [ ] Etapa 1 completa?
  [ ] Etapa 2 valida?
  [ ] Files CHANGELOG.md, CONTRIBUTING.md, LICENSE criados?
  [ ] .github/workflows/ criado com 2 arquivos?
  [ ] docs/ pasta criada e documentação movida?
  [ ] Commit profissional feito?
  [ ] Tag v2.0.0 criada?
  [ ] Push enviado para GitHub?

DEPOIS DE PUSH
  [ ] Alterações aparecem em GitHub?
  [ ] Workflows aparecem em Actions?
  [ ] Releases mostra v2.0.0?
  [ ] README atualizado?
  [ ] CHANGELOG visível?

GITHUB SETTINGS (MANUAL)
  [ ] Description preenchido?
  [ ] Topics adicionados?
  [ ] Branch protection ativo?
  [ ] Actions habilitadas?
```

---

## ⏱️ Cronograma Recomendado

**Sessão 1 (45 min):**
- Leia `PLANO_ACAO_RESUMO.md`
- Prepare-se para as etapas
- Execute ETAPAS 1-3

**Sessão 2 (45 min):**
- Execute ETAPAS 4-6
- Configure GitHub (ETAPA 7)
- Rode testes (ETAPA 8)

**Sessão 3 (30 min - OPCIONAL):**
- Refinamentos
- Documentação adicional
- Testes de integração

Total: ~2 horas em 2-3 sessões

---

## 📚 Documentos de Referência Técnica

Se precisar de mais informações sobre tópicos específicos:

- **Docker & Arquitetura**: `PLANO_PUBLICACAO_GITHUB.md` > FASE 3
- **GitHub Actions**: `PLANO_PUBLICACAO_GITHUB.md` > FASE 4
- **FIX 4 Técnico**: `docs/FIX_4_COMPLETADO.md` (será movido)
- **Database Schema**: `docs/ANALISE_GAPS_TESTE_MANUAL.md` (será movido)
- **Padrões de Código**: `CONTRIBUTING.md` (será criado)

---

## 🎁 Bônus: Comandos Úteis Pós-Publicação

Depois que tudo estiver pronto:

```bash
# Ver estatísticas do repositório
git log --oneline | wc -l

# Ver branches
git branch -a

# Ver tags e datas
git tag -l --format='%(refname:short) - %(creatordate:short)'

# Clone para testar (em outra pasta)
git clone https://github.com/seu-usuario/projeto-chatbot-ifs.git teste

# Ver histórico de um arquivo
git log --oneline -- README.md
```

---

## 🔐 Segurança: O Que NÃO Fazer

❌ **NÃO commitar:**
- `.env` com senhas reais
- `config_*.json` com chaves API
- `credentials.txt` ou similar
- `venv/` ou virtualenvs

✅ **FAÇA:**
- Use `.env.example` com valores fictícios
- Adicionen `.env` ao `.gitignore`
- Use GitHub Secrets para CI/CD

---

## 🌐 URLs Importantes Após Publicação

Depois que terminar:

- **GitHub Principal**: `https://github.com/seu-usuario/projeto-chatbot-ifs`
- **Releases**: `https://github.com/seu-usuario/projeto-chatbot-ifs/releases`
- **Actions**: `https://github.com/seu-usuario/projeto-chatbot-ifs/actions`
- **Settings**: `https://github.com/seu-usuario/projeto-chatbot-ifs/settings`
- **Issues**: `https://github.com/seu-usuario/projeto-chatbot-ifs/issues`
- **Pull Requests**: `https://github.com/seu-usuario/projeto-chatbot-ifs/pulls`

(Substitua "seu-usuario" pelo seu nome de usuário GitHub)

---

## 📞 Precisa de Ajuda?

| Situação | Ação |
|----------|------|
| "Não entendo o que fazer" | Leia `PLANO_ACAO_RESUMO.md` |
| "Qual comando executar?" | Abra `SCRIPT_PUBLICACAO.ps1` |
| "Por que fazer isso?" | Leia `PLANO_PUBLICACAO_GITHUB.md` |
| "Erro técnico" | Consulte seção "Troubleshooting" |
| "Visão geral rápida" | Abra `PLANO_VISUAL.md` |

---

## 🎯 Objetivo Final

Após completar todas as etapas:

✅ **Docker**: Dockerfile atualizado para Python 3.13
✅ **Documentação**: CHANGELOG, CONTRIBUTING, LICENSE criados
✅ **CI/CD**: GitHub Actions configurado para automação
✅ **Versionamento**: v2.0.0 publicada com tag
✅ **Qualidade**: Código organizado e pronto para produção
✅ **Comunidade**: Aberto para contribuições

---

**Versão**: 1.0 | **Atualizado**: 2026-04-09 | **Status**: ✅ Pronto
