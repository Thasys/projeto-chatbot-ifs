# 🔧 FASE 3: Adaptar Código para Railway

**Data:** 10 de abril de 2026  
**Tempo:** 20 minutos  
**Dificuldade:** 🟢 FÁCIL (editar 2 arquivos)

---

## 📌 Objetivo

Adaptar Dockerfile e criar arquivos de configuração Railway, depois fazer push para GitHub (triggers deploy automático).

---

## ✅ PASSO 1: Atualizar Dockerfile (Porta Dinâmica)

Railway fornece variável `$PORT` dinamicamente. Precisamos usar.

**Abrir arquivo:** [Dockerfile](./Dockerfile)

**Procurar por:**
```dockerfile
EXPOSE 8501

# Default command: executar Streamlit
CMD ["streamlit", "run", "app_v2.py", "--server.address=0.0.0.0", "--server.port=8501"]
```

**Substituir por:**
```dockerfile
EXPOSE $PORT

# Default command: executar Streamlit com porta dinâmica
CMD ["sh", "-c", "streamlit run app_v2.py --server.address=0.0.0.0 --server.port=${PORT:-8501}"]
```

**Explicação:**
- `$PORT`: Variável fornecida por Railway (dinamicamente atribuída)
- `${PORT:-8501}`: Se não tiver PORT, usa 8501 como padrão
- `sh -c`: Permite interpretar variáveis de ambiente

---

## ✅ PASSO 2: Criar Arquivo Procfile

**Novo arquivo:** `Procfile` (sem extensão!)

Ir para raiz do projeto e criar:

```bash
cd c:\Users\thars\Documents\THARSYS\ESTUDOS\Chatbot\ -\ IFS\04\projeto-chatbot-ifs
```

Criar arquivo vazio e adicionar conteúdo:

```
web: streamlit run app_v2.py --server.port=$PORT --server.headless=true --logger.level=warning
```

**Salvar como:** `Procfile` (sem .txt!)

---

## ✅ PASSO 3: Criar Arquivo railway.json

**Novo arquivo:** `railway.json` (no root do projeto)

Copiar conteúdo:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "dockerfile"
  },
  "deploy": {
    "startCommand": "streamlit run app_v2.py --server.headless=true --logger.level=warning"
  }
}
```

**Salvar como:** `railway.json`

---

## ✅ PASSO 4: Verificar .env.example

Abrir arquivo [.env.example](./.env.example)

Garantir que tem:

```
# OpenAI Configuration
OPENAI_API_KEY=sk-...seu_api_key... (deixar placeholder)

# Application Settings
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# Database (será preenchido automaticamente por Railway)
# DATABASE_URL=postgres://... (será preenchido aqui)
```

Salvar se fez mudanças.

---

## ✅ PASSO 5: Adicionar Arquivos ao Git

Abrir PowerShell no projeto:

```powershell
cd "c:\Users\thars\Documents\THARSYS\ESTUDOS\Chatbot - IFS\04\projeto-chatbot-ifs"
```

Verificar status:

```powershell
git status
```

Você deve ver:
```
? Procfile (untracked)
? railway.json (untracked)
M Dockerfile (modified)
M .env.example (modified se mudou)
```

---

## ✅ PASSO 6: Git Add

Adicionar os arquivos:

```powershell
git add Dockerfile Procfile railway.json .env.example
```

Verificar novamente:

```powershell
git status
```

Deve mostrar:
```
Changes to be committed:
  new file:   Procfile
  new file:   railway.json
  modified:   Dockerfile
  modified:   .env.example
```

---

## ✅ PASSO 7: Git Commit

```powershell
git commit -m "feat: adapt for Railway deployment (GitOps auto-deploy)"
```

Output:
```
[master xxxxxxx] feat: adapt for Railway deployment
 4 files changed, XX insertions(+), X deletions(-)
 create mode 100644 Procfile
 create mode 100644 railway.json
```

---

## ✅ PASSO 8: Git Push (DISPARA DEPLOY!)

```powershell
git push origin master
```

Isso dispara webhook no Railway!

```
Enumerating objects...
Compressing objects...
Writing objects...
remote: Webhook triggered
remote: Building Docker image...
```

**RAILWAY COMEÇA A FAZER DEPLOY AUTOMATICAMENTE!**

---

## 🤖 Railway Building...

Você verá no dashboard Railway:

```
Deploying...
└── Building Docker image
    ├── Installing dependencies
    └── Starting application

Deployment in progress... (5 min)
```

**Aguarde completar!**

---

## 🎯 O Que Acontece Agora

1. **GitHub recebe push** ✅
2. **Rails recebe webhook** ✅
3. **Clona código atualizado** ✅
4. **Detecta Dockerfile** ✅
5. **Detecta Procfile** ✅
6. **Detecta requirements.txt** ✅
7. **Constrói imagem Docker** 🔄 (3-5 min)
8. **Inicia container** 🔄 (1-2 min)
9. **App online!** ✅

---

## 📝 Arquivos Criados/Modificados

```
ANTES:
├── Dockerfile                (porta hardcoded 8501)
├── requirements.txt          (OK)
└── app_v2.py                (OK)

DEPOIS:
├── Dockerfile                (porta dinâmica $PORT)
├── Procfile                  (NOVO!)
├── railway.json              (NOVO!)
├── requirements.txt          (OK)
└── app_v2.py                (OK)
```

---

## ✅ Checklist FASE 3

- [x] Dockerfile atualizado (porta dinâmica)
- [x] Procfile criado
- [x] railway.json criado
- [x] .env.example atualizado
- [x] Git add realizado
- [x] Git commit realizado
- [x] Git push realizado
- [x] Webhook acionado
- [x] Railway building...

---

## 🎯 Verificar Deploy

Enquanto Railway está building, você pode:

1. **Ir ao dashboard Railway:**
   ```
   https://railway.com/dashboard
   ```

2. **Ver logs em tempo real:**
   ```
   Project → Deployments → Latest → Logs
   ```

3. **Ver progresso:**
   ```
   Building...
   Installing streamlit...
   Installing crewai...
   Installing pandas...
   ...
   Container started!
   Application is running!
   ```

---

## ⏭️ Próxima Fase

## 👉 FASE 4: Banco de Dados Railway

**Após deploy completar (vire green):**

1. Vai aparecer mensagem:
   ```
   ✅ Successfully deployed!
   Application URL: https://projeto-chatbot-ifs-production.up.railway.app
   ```

2. Pode ainda ter erro 500 (falta variáveis)
3. Vamos configurar na PRÓXIMA fase

Vá para: [FASE_4_RAILWAY_DATABASE.md](FASE_4_RAILWAY_DATABASE.md)

---

## 🆘 Se Tiver Problema

### Deploy falhou?
```
1. Clique em "Logs" no projeto
2. Procure por erro (em vermelho)
3. Comum: SyntaxError no app_v2.py
4. Solução: Corrir arquivo localmente, fazer push novamente
```

### Demora muito na build?
```
Primeira build pode levar 5-10 minutos
Próximas serão mais rápidas (cache Docker)
Paciência! ☕
```

### App mostra erro 500?
```
ESPERADO! Faltam variáveis de ambiente.
Vamos adicionar na PRÓXIMA fase.
```

---

## ⏱️ Timeline

```
Antes:  Setup local (✅ concluído)
        ↓
FASE 2: Conta Railway (✅ 10 min)
        ↓
FASE 3: Adaptar código (✅ AGORA, 20 min)
        ↓
Git push → Railway webhook acionado 🔔
        ↓
Railway building (⏳ 5-10 min)
        ↓
FASE 4: Variáveis e banco (→ próximo, 20 min)
        ↓
FASE 5: Testes finais (→ depois, 30 min)
        ↓
🎉 PRONTO PARA PRODUÇÃO!
```

---

## ✨ O Que Você Conquistou

✅ Código pronto para Railway  
✅ Deploy automático com Git configurado  
✅ Container Docker em produção  
✅ URL pública obtida  
✅ HTTPS/SSL automático  
✅ Logs centralizados  

**Faltam:** Variáveis de ambiente + Banco de dados

---

**Status:** FASE 3 concluída  
**Próximo:** FASE 4 - Database  
**Tempo total:** ~30 minutos (você + Railway)
