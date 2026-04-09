# ETAPA 7: GitHub Settings (Manual)

## 🔐 Pré-requisito: Fazer Push do Código

Antes de configurar no GitHub.com, faça push:

```powershell
cd "c:\Users\thars\Documents\THARSYS\ESTUDOS\Chatbot - IFS\04\projeto-chatbot-ifs"
git push origin main --tags
# ou se usar 'master' como branch principal:
git push origin master --tags
```

---

## ✅ Checklist de Configuração GitHub.com

### 1️⃣ Repository Settings → General
- [ ] **Repository name**: `projeto-chatbot-ifs`
- [ ] **Description**: 
  ```
  🤖 IFS Chatbot v2.0 - AI-powered financial transparency system for public budget analysis
  ```
- [ ] **Website**: (deixar em branco por enquanto)
- [ ] **Visibility**: `Public` (se deseja compartilhar) ou `Private` (se apenas uso pessoal)

### 2️⃣ Repository Settings → Topics
Adicione estes tópicos (clicando em "Add topics"):
- [ ] `chatbot`
- [ ] `crewai`
- [ ] `python`
- [ ] `financial-transparency`
- [ ] `mysql`
- [ ] `streamlit`
- [ ] `ai`
- [ ] `public-budget`

### 3️⃣ Repository Settings → Manage Access
- [ ] Você é o proprietário (se for conta pessoal)
- [ ] Adicione colaboradores se necessário (opcional)

### 4️⃣ Repository Settings → Branches
**Default branch**: 
- [ ] Confirme que é `main` ou `master` (seu padrão atual)

**Branch Protection Rules**:
1. Clique em **"Add rule"**
2. **Branch name pattern**: `main` (ou `master`)
3. Marque:
   - [ ] Require a pull request before merging
   - [ ] Require status checks to pass before merging
   - [ ] Require branches to be up to date before merging
   - [ ] Dismiss stale pull request approvals
   - [ ] Require code reviews before merging (quantidade: 1)
   - [ ] Include administrators

### 5️⃣ Repository Settings → Environments (Opcional)
- [ ] Production environment (para deployments futuros)
- [ ] Staging environment (para testes)

### 6️⃣ Actions Settings
**Enable GitHub Actions**:
- [ ] Clique em **Settings** → **Actions** → **"General"**
- [ ] Enable **"Actions"** (deve estar habilitado)
- [ ] **Workflow permissions**: 
  - [ ] Selecione **"Read and write permissions"**
  - [ ] Marque **"Allow GitHub Actions to create and approve pull requests"**

### 7️⃣ Code Security Settings
**Dependabot**:
- [ ] **Settings** → **Code security** → **Dependabot**
  - [ ] Enable: **Dependabot alerts**
  - [ ] Enable: **Dependabot security updates** (auto-update dependencies)
  - [ ] Enable: **Dependabot version updates**

**Code scanning**:
- [ ] **Settings** → **Code security and analysis**
  - [ ] Enable: **Code scanning** (Trivy está configurado em docker.yml)

### 8️⃣ Pages (Documentação estática - Opcional)
- [ ] Clique em **Settings** → **Pages**
- [ ] **Source**: `Deploy from a branch`
- [ ] **Branch**: `main` (ou `master`)
- [ ] **Directory**: `/ (root)`
- [ ] GitHub Pages irá servir seu README.md

---

## 🎯 Verificação Final (Execute no Terminal)

Após configurar no GitHub, execute:

```powershell
# Verificar que os commits estão no GitHub
git log --oneline -3

# Verificar que a tag v2.0.0 está visible
git tag -l | Select-Object -Last 3

# Visualizar release no GitHub (abrir no navegador)
# https://github.com/seu-usuario/projeto-chatbot-ifs/releases/tag/v2.0.0
```

---

## 📊 Resultados Esperados

Após completar ETAPA 7, você terá:

✅ `main`/`master` branch atualizado com:
- 2 commits recentes (FIX 4 + v2.0.0)
- Tag `v2.0.0` visível em Releases

✅ GitHub Actions workflows:
- `.github/workflows/tests.yml` executando
- `.github/workflows/docker.yml` executando

✅ Documentação visível:
- README.md
- CHANGELOG.md
- CONTRIBUTING.md
- LICENSE

✅ Branch protection active:
- PRs obrigatórias para merge
- Status checks required

---

## ⚠️ Troubleshooting

### Branch local é `master` mas GitHub espera `main`
```powershell
# Se seu branch local é 'master' no local mas 'main' no remote:
git branch -m master main
git push -u origin main
```

### Workflows não aparecem em GitHub
1. Verifique se `.github/workflows/` foi pushado
2. Verifique se você habilitou Actions em Settings
3. Aguarde 1-2 minutos para GitHub processar

### Tag v2.0.0 não aparece em Releases
1. Confirme que pushou as tags:
```powershell
git push origin v2.0.0
```
2. Acesse: https://github.com/seu-usuario/projeto-chatbot-ifs/releases

### Proteção de branch está muito restritiva
- Você é o admin, pode fazer bypass
- Para colaboradores, reduza requerimentos se necessário

---

## ✨ Próximos Passos (Depois do Push)

1. Crie a primeira **Release** (v2.0.0) no GitHub
   - Clique em **"Create a new release"**
   - Use a tag `v2.0.0`
   - Descrição = conteúdo do CHANGELOG.md

2. Configure **About** (lado direito da página principal)
   - Descrição: `IFS Chatbot v2.0`
   - Website: seu site pessoal (opcional)
   - Topics: adicione os tópicos listados acima

3. Aguarde os workflows rodar:
   - tests.yml deve passar em ~5 minutos
   - docker.yml deve passar em ~10 minutos

4. Verifique o **Status Badge** e copie para o README:
   - `[![Tests](https://github.com/seu-usuario/projeto-chatbot-ifs/workflows/Tests/badge.svg)]()`

---

**✅ ETAPA 7 Completa: GitHub está pronto para receber código profissional!**
