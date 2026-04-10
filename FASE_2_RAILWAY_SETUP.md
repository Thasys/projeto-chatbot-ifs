# 🚂 FASE 2: Setup Railway - Configuração Inicial

**Data:** 10 de abril de 2026  
**Tempo:** 10 minutos  
**Dificuldade:** 🟢 MUITO FÁCIL (só cliques no navegador)

---

## 📌 Objetivo

Registrar em Railway e conectar seu repositório GitHub para deploy automático.

---

## ✅ PASSO 1: Registrar no Railway

1. **Abrir navegador** e ir para:
   ```
   https://railway.com
   ```

2. **Clique em "Sign Up"** (canto superior direito)

3. **Escolha "Continue with GitHub"**
   - Mais fácil (usa sua conta GitHub existente)
   - Autoriza Railway a acessar seus repositórios

4. **Você verá tela de autorização GitHub:**
   - Clique em "Authorize railwayapp"

5. **Preencha dados básicos** (se solicitado):
   ```
   Username: seu_username_railway
   Email: seu@email.com
   ```

6. **Confirme email** (se necessário)
   - Verifique inbox
   - Clique no link enviado por Railway

✅ **Conta criada!**

---

## ✅ PASSO 2: Dashboard Railway

Após login, você verá:

```
┌─────────────────────────────────────┐
│  Welcome to Railway                 │
│  ─────────────────────────────────  │
│  Your Projects    | Documentation   │
│  ─────────────────────────────────  │
│  [+ New Project]                    │
│                                     │
│  No projects yet                    │
└─────────────────────────────────────┘
```

---

## ✅ PASSO 3: Criar Novo Projeto

1. **Clique em "+ New Project"** (botão grande)

2. **Selecione "Deploy from GitHub repo"**
   - Opção mais comum
   - Conecta direto ao GitHub

3. **Você verá lista de seus repositórios GitHub**

4. **Procure por:** `projeto-chatbot-ifs`
   - Se não aparecer, clique em "Refresh" e aguarde

5. **Clique no repositório** para selecioná-lo

---

## ✅ PASSO 4: Autorizar Acesso ao Repositório

Railway pedirá permissão ao GitHub:

1. **Clique "Authorize railwayapp"** novamente
   - Desta vez autoriza acesso ao repositório específico

2. **Confirme as permissões:**
   - Ler código do repositório
   - Criar webhooks (para deploy automático)

✅ **GitHub conectado!**

---

## ✅ PASSO 5: Configuração Inicial do Projeto

Railway mostra tela de configuração inicial:

```
Project Name: projeto-chatbot-ifs
Runtime: Auto-detect (Python)
```

**Não mude nada por enquanto!** Railway vai auto-detectar:

- ✅ Dockerfile (se existir)
- ✅ requirements.txt
- ✅ Python version

1. **Clique em "Deploy"** ou **"Continue"**

2. **Railway inicia build:**
   ```
   Building Docker image...
   Installing dependencies...
   Starting container...
   ```

   Pode levar **3-5 minutos** na primeira vez.

---

## ✅ PASSO 6: Aguardar Build

Você verá uma barra de progresso:

```
┌─────────────────────────────────────┐
│         Building                    │
├─────────────────────────────────────┤
│ ████████████░░░░░░░░░░░░░░░░░░░░░ │
│                                     │
│  Step 1: Cloning from GitHub        │
│  Step 2: Building Docker image      │
│  Step 3: Pushing to registry        │
│  Step 4: Deploying container        │
│                                     │
│              [DETAILS]              │
└─────────────────────────────────────┘
```

**Paciência:** Leva 3-5 minutos

---

## ✅ PASSO 7: Primeira Execução (Esperado: ERRO)

Após build, você verá uma URL como:

```
https://projeto-chatbot-ifs-production.up.railway.app
```

**Pode aparecer erro 500** - isto é NORMAL!

Porquê?
- Variáveis de ambiente ainda não configuradas
- Arquivo `Procfile` ainda não existe

Vamos corrigir isso!

---

## ✅ PASSO 8: Dashboard do Projeto

No dashboard você verá:

```
Project: projeto-chatbot-ifs
├── [Deploys]
│   └── Latest: Just now (Building/Deployed)
├── [Settings]
│   ├── Variables
│   ├── Domains
│   ├── Webhooks
│   └── ...
└── [+ New Service]
    ├── Database
    ├── Redis
    └── ...
```

**Anotar URL do app:**
```
https://projeto-chatbot-ifs-production.up.railway.app
```

(Exato será diferente, baseado no seu username)

---

## 📝 O Que Anotei

```
RAILWAY PROJECT INFO
===================
Dashboard: https://railway.com/dashboard
Project: projeto-chatbot-ifs
App URL: https://projeto-chatbot-ifs-production.up.railway.app

Status: Build iniciado (pode ter erro 500, é normal)
```

---

## 🆘 Problemas Nesta Fase

### Problema 1: "Repository not found"
**Solução:**
- Verifique que está logado em GitHub
- Clique "Refresh" para atualizar lista
- Ou vá direto no painel GitHub Settings → Applications

### Problema 2: "Build failed"
**Normal na primeira vez!** Porque:
- Arquivo Procfile não existe
- Variáveis não configuradas

Resolvemos na PRÓXIMA fase.

### Problema 3: App mostra erro 500
**ESPERADO!** Não tem variáveis de ambiente ainda.

Vamos adicionar na PRÓXIMA fase.

---

## ✅ Checklist FASE 2

- [x] Conta Railway criada
- [x] GitHub conectado
- [x] Projeto criado em Railway
- [x] Repositório selecionado
- [x] Build iniciado
- [x] URL do app obtida
- [x] Erro 500 esperado (normal)

---

## ⏭️ Próxima Fase

## 👉 FASE 3: Atualizar Código para Railway

**Vá para:** [FASE_3_RAILWAY_ADAPTAR.md](FASE_3_RAILWAY_ADAPTAR.md)

```
1. Atualizar Dockerfile (porta dinâmica)
2. Criar Procfile
3. Criar railway.json
4. Fazer push para GitHub
5. Railway faz deploy automático!
```

**Tempo:** 15 minutos

---

## 🎉 Parabéns!

Você agora tem:
- ✅ Conta Railway ativa
- ✅ Projeto criado
- ✅ GitHub conectado
- ✅ Webhook para deploy automático

**Próximo:** Adaptar código e fazer push!

---

**Status:** Fase 2 95% concluída  
**Próximo:** FASE_3_RAILWAY_ADAPTAR.md  
**Tempo total até agora:** ~10 minutos
