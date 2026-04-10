# ✅ RAILWAY CHECKLIST - Passo a Passo Simplificado

**Data:** 10 de abril de 2026  
**Tempo Total:** 2-3 horas  
**Dificuldade:** 🟢 FÁCIL (muito mais que PythonAnywhere)

---

## 🎯 Que Vamos Fazer

```
1. Registrar no Railway (5 min)
2. Conectar GitHub (5 min)
3. Atualizar código (15 min)
4. Fazer push (1 min)
5. Railway faz deploy automático (5 min)
6. Configurar banco de dados (15 min)
7. Testes finais (30 min)

TOTAL: ~2-3 horas (SUPER SIMPLIFICADO!)
```

---

## ✅ FASE 2: RAILWAY SETUP (Primeira Vez)

### Passo 1: Criar Conta Railway
- [ ] Ir para https://railway.com
- [ ] Clique em "Sign Up"
- [ ] Clique em **"Continue with GitHub"** (mais fácil)
- [ ] Autorizar railway.app
- [ ] Confirmar email

**Tempo:** 5 minutos

---

### Passo 2: Conectar GitHub
- [ ] No dashboard Railway clique em **"New Project"**
- [ ] Selecione **"Deploy from GitHub repo"**
- [ ] Busque seu repositório: `projeto-chatbot-ifs`
- [ ] Clique em **"Deploy"**

**Tempo:** 5 minutos

---

## ✅ FASE 3: ATUALIZAR CÓDIGO (Local)

### Passo 3a: Atualizar Dockerfile
```dockerfile
# Mudar porta de 8501 para $PORT (dinâmica do Railway)

# De:
EXPOSE 8501
CMD ["streamlit", "run", "app_v2.py", "--server.address=0.0.0.0", "--server.port=8501"]

# Para:
EXPOSE $PORT
CMD ["streamlit", "run", "app_v2.py", "--server.address=0.0.0.0", "--server.port=${PORT:-8501}"]
```

### Passo 3b: Criar Arquivo `Procfile`
```
web: streamlit run app_v2.py --server.port=$PORT --server.headless=true
```

### Passo 3c: Criar Arquivo `railway.json`
```json
{
  "build": {
    "builder": "dockerfile"
  },
  "deploy": {
    "startCommand": "streamlit run app_v2.py --server.port=$PORT --server.headless=true"
  }
}
```

**Tempo:** 15 minutos

---

## ✅ FASE 4: FAZER PUSH (Trigger Deploy)

### Passo 4: Git Commit e Push
```bash
cd c:\Users\thars\Documents\THARSYS\ESTUDOS\Chatbot\ -\ IFS\04\projeto-chatbot-ifs

git add Dockerfile Procfile railway.json
git commit -m "chore: adapt for Railway deployment"
git push origin master
```

**Tempos:** 1 min

---

## 🤖 RAILWAY DEPLOY AUTOMÁTICO

Após `git push`:

- [ ] Railway detecta mudanças no GitHub
- [ ] Clona repositório
- [ ] Constrói Docker
- [ ] Inicia container Streamlit
- [ ] Deploy finalizado

**Tempo:** ~5 minutos de build

---

## ✅ FASE 5: CONFIGURAR VARIÁVEIS

### Passo 5: Adicionar Environment Variables

No painel Railway:

1. Clique em seu projeto
2. Vá para **"Variables"**
3. Adicione cada variável:

```
OPENAI_API_KEY = sk-... (sua chave)
ENVIRONMENT = production
DEBUG = false
```

**Se usar banco Railway (próximo passo):**
```
DATABASE_URL = [automático]
MYSQL_HOST = [automático]
MYSQL_USER = [automático]
MYSQL_PASSWORD = [automático]
```

---

## ✅ FASE 6: BANCO DE DADOS

### Passo 6a: Criar Banco no Railway

1. No projeto Railway
2. Clique em **"+ New Service"**
3. Selecione **"Database"**
4. Escolha:
   - [ ] PostgreSQL (recomendado - mais rápido)
   - [ ] MySQL (compatível com seu código)

5. Railway automaticamente fornece:
   ```
   DATABASE_URL = postgres://user:pass@host:port/db
   ```
   OU
   ```
   DATABASE_URL = mysql://user:pass@host:port/db
   ```

### Passo 6b: Conectar Banco ao App

No Railway:
1. Clique no banco de dados criado
2. Vá para **"Connect"**
3. Copie a URL
4. Adicione como variável no app

---

## ✅ FASE 7: TESTES

### Passo 7a: Verificar Deploy
- [ ] Ir para https://seu-app.up.railway.app
- [ ] Página carrega sem erro
- [ ] Streamlit UI visível

### Passo 7b: Verificar Conectividade
- [ ] Teste consulta simples
- [ ] Verifique logs (Railway > Deployments > Logs)

### Passo 7c: Testar HTTPS
- [ ] Certificado SSL automático
- [ ] URL começando com `https://`
- [ ] 🔒 cadeado verde no navegador

---

## 📊 CHECKLIST FASE POR FASE

### FASE 1: ✅ JÁ COMPLETA (PYTHON 3.12)
- [x] Python local testado
- [x] Dependências instaladas
- [x] Tests passaram

### FASE 2: Railway Setup (FAZER AGORA)
- [ ] Conta Railway criada
- [ ] GitHub conectado
- [ ] Repositório selecionado

### FASE 3: Atualizar Código
- [ ] Dockerfile atualizado (porta dinâmica)
- [ ] Procfile criado
- [ ] railway.json criado
- [ ] Commit feito
- [ ] Push para GitHub

### FASE 4: Deploy Automático
- [ ] Railway detectou push
- [ ] Build iniciado
- [ ] Container rodando
- [ ] App acessível via URL

### FASE 5: Variáveis e Banco
- [ ] OPENAI_API_KEY adicionada
- [ ] Banco de dados criado
- [ ] Conectado ao app
- [ ] Variáveis configuradas

### FASE 6: Testes Finais
- [ ] App carregando sem erro
- [ ] Consultas funcionando
- [ ] HTTPS ativo
- [ ] Logs sem erros

---

## 🚀 COMANDOS RÁPIDOS (Copiar e Colar)

Abrir PowerShell e executar em sequência:

```powershell
# 1. Navegar para projeto
cd "c:\Users\thars\Documents\THARSYS\ESTUDOS\Chatbot - IFS\04\projeto-chatbot-ifs"

# 2. Verificar status
git status

# 3. Adicionar arquivos
git add Dockerfile Procfile railway.json

# 4. Commit
git commit -m "chore: adapt for Railway deployment (GitOps)"

# 5. Push para GitHub (dispara Railway deploy)
git push origin master

# Pronto! Railway faz o resto automaticamente 🚀
```

---

## 🎯 URLs Importantes

| Recurso | URL |
|---------|-----|
| **Railway Dashboard** | https://railway.com/dashboard |
| **Seu Projeto** | https://railway.com/project/[project-id] |
| **App em Produção** | https://seu-app.up.railway.app |
| **GitHub Repo** | https://github.com/Thasys/projeto-chatbot-ifs |

---

## ⏱️ Timeline

```
Agora:           Cadastro Railway (5 min)
    ↓
+5 min:          Conectar GitHub (5 min)
    ↓
+10 min:         Atualizar código local (15 min)
    ↓
+25 min:         Push para GitHub (1 min)
    ↓
+26 min:         Railway building... (5 min)
    ↓
+31 min:         App online! 🎉
    ↓
+45 min:         Variáveis + Banco (15 min)
    ↓
+60 min:         Testes finais (30 min)
    ↓
~2-3 HORAS:      PRONTO PARA PRODUÇÃO ✅
```

---

## 🟢 STATUS

| Item | Status | Tempo |
|------|--------|-------|
| FASE 1: Python 3.12 | ✅ COMPLETA | Concluído |
| FASE 2: Railway Setup | ⏳ PRÓXIMO | 5 min |
| FASE 3: Código | ⏳ DEPOIS | 15 min |
| FASE 4: Deploy | ⏳ AUTOMÁTICO | 5 min |
| FASE 5: Variáveis | ⏳ FINAL | 15 min |
| FASE 6: Testes | ⏳ FINAL | 30 min |

---

## 📝 Próximo Passo

👉 Vá para: **FASE_2_RAILWAY_SETUP.md**

```
1. Criar conta Railway
2. Conectar com GitHub
3. Permitir acesso ao repositório
4. Voltar aqui para próxima fase
```

**Tempo:** 10 minutos

---

**Você está pronto? Vamos começar! 🚀**
