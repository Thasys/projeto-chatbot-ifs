# 🗄️ FASE 4: Banco de Dados Railway

**Data:** 10 de abril de 2026  
**Tempo:** 15 minutos  
**Dificuldade:** 🟢 MUITO FÁCIL (Railway faz tudo)

---

## 📌 Objetivo

Criar banco de dados PostgreSQL no Railway e configurar conexão automática.

---

## ✅ PASSO 1: Acessar Dashboard Railway

1. **Ir para:** https://railway.com/dashboard
2. **Clique em seu projeto:** `projeto-chatbot-ifs`
3. Você verá seu app rodando (ou com erro 500, normal)

---

## ✅ PASSO 2: Criar Banco de Dados

1. **Clique em "+ New Service"** (botão no topo)
2. **Selecione "Database"**
3. **Escolha um banco:**

### Opção A: PostgreSQL (RECOMENDADO)
```
✅ Mais rápido
✅ Moderno
✅ Melhor performance
✅ Grátis no Railway
```

### Opção B: MySQL
```
✅ Compatível com seu código SQL
✅ Você conhece
❌ Um pouco mais lento
```

**Escolher: PostgreSQL** (mais rápido)

---

## ✅ PASSO 3: Railway Cria Banco Automaticamente

Após escolher, Railway:

1. **Provisiona banco de dados** (2-3 minutos)
2. **Cria usuário e senha** (automaticamente)
3. **Fornece credenciais** automatically

Você verá:

```
Database: railway
Hostname: viaduct.proxy.rlwy.net
Username: postgres
Password: xxxxxxx
Port: 5432
```

✅ **Pronto!**

---

## ✅ PASSO 4: Variáveis de Ambiente Automáticas

Railway **automaticamente injeta** variáveis no seu app!

Você verá no painel do app:

```
Variables:
├── OPENAI_API_KEY = sk-... (você adicionou)
├── DATABASE_URL = postgres://user:pass@host:port/db ← AUTOMÁTICO!
├── PGHOST = viaduct.proxy.rlwy.net ← AUTOMÁTICO!
├── PGPORT = 5432 ← AUTOMÁTICO!
├── PGUSER = postgres ← AUTOMÁTICO!
├── PGPASSWORD = xxxxxxx ← AUTOMÁTICO!
└── PGDATABASE = railway ← AUTOMÁTICO!
```

**Você NÃO precisa adicionar manualmente!**

Railway faz tudo sozinho 🎉

---

## ✅ PASSO 5: Adicionar OpenAI API Key (Única Manual)

1. **No painel do projeto Railway**
2. **Vá para "Variables"** (ou "Settings")
3. **Clique em "+ Add Variable"**
4. **Preencha:**
   ```
   Variable Name: OPENAI_API_KEY
   Value: sk-... (sua chave aqui)
   ```
5. **Clique "Save"**

**Railway automaticamente reinicia o app com as novas variáveis!**

---

## ✅ PASSO 6: Conectar Banco ao App

**Boa notícia:** Railway faz isto automaticamente!

Quando você criar um banco (`+ New Service`), ele **automaticamente**:

1. Cria variáveis `DATABASE_URL`, `PGHOST`, etc
2. Inicia um novo database service
3. Conecta ao seu app

Seu código Python pode ler:

```python
import os

database_url = os.getenv('DATABASE_URL')
# Usa variável para conectar ao PostgreSQL
```

---

## ✅ PASSO 7: Verificar Conectividade

Railway oferece ferramenta de teste.

No painel do banco:

1. **Clique no serviço do banco de dados**
2. **Vá para "Connect"**
3. **Você verá opções:**
   ```
   - Connection String
   - psql CLI command
   - Python connection
   - Node.js connection
   ```

4. **Para testar, você pode usar `psql`:**
   ```bash
   psql postgres://user:pass@host:5432/railway
   ```

**Mas seu código Python já vai funcionar automaticamente!**

---

## ✅ O Que Muda no Seu Código

### Antes (com MySQL local):
```python
import mysql.connector

connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='password',
    database='chatbot'
)
```

### Depois (com Railway PostgreSQL):
```python
import os
from sqlalchemy import create_engine

# Railway fornece DATABASE_URL automaticamente
database_url = os.getenv('DATABASE_URL')

# Se for PostgreSQL, adaptar:
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

engine = create_engine(database_url)
```

**Seu código já usa SQLAlchemy, então funciona!**

---

## 📊 Comparação: Local vs Railway

### Local (desenvolvimento)
```
MySQL: localhost:3306
User: root
Database: chatbot_db
Credenciais: hardcoded ou .env
```

### Railway (produção)
```
PostgreSQL: viaduct.proxy.rlwy.net:5432
User: postgres
Database: railway
Credenciais: variáveis injetas automaticamente ✅
```

---

## 🎯 Próximas Ações

### Imediato
1. Criar banco PostgreSQL no Railway ✅
2. Adicionar OPENAI_API_KEY ✅
3. Railway reinicia app automaticamente

### Próximo (FASE 5)
1. Testar acesso à URL
2. Verificar se variáveis estão carregadas
3. Testar banco de dados

---

## 📝 Checklist FASE 4

- [ ] Banco PostgreSQL criado (ou MySQL)
- [ ] Variáveis de ambiente automáticas injetadas
- [ ] OPENAI_API_KEY adicionada manualmente
- [ ] App reiniciado com novas variáveis
- [ ] Conexão verificada

---

## ✅ Resultado Esperado

Após completar FASE 4:

```
Dashboard Railway:
├── Serviço: projeto-chatbot-ifs (APP)
│   ├── Status: ✅ Running
│   ├── URL: https://projeto-chatbot-ifs-production.up.railway.app
│   └── Variables: OPENAI_API_KEY, DATABASE_URL, PGHOST, ...
│
└── Serviço: railway (DATABASE)
    ├── Type: PostgreSQL
    ├── Status: ✅ Running
    └── Conectado ao app ✅
```

---

## 🆘 Problemas Comuns

### Problema 1: Banco não aparece no painel
**Solução:**
- Aguardar 2-3 minutos para provisionar
- Fazer refresh na página (F5)
- Pode levar até 5 minutos na primeira vez

### Problema 2: Variáveis não aparecem
**Solução:**
- Railway injeta variáveis ao reiniciar o app
- Forçar redeployment: vá em "Deployments" → "Redeploy latest"
- Logs mostram: `DATABASE_URL = postgres://...`

### Problema 3: Erro de conexão ainda existe
**Solução:**
- ESPERADO em FASE 4 (sem dados ainda)
- Vamos testar conectividade na FASE 5

---

## 💾 Backup Automático

Railway oferece snapshots automáticos:

```
Database → Backups → View snapshots
```

Seus dados são **sempre** salvos! 🎉

---

## ⏭️ Próxima Fase

## 👉 FASE 5: Testes Finais e Validação

Vá para: [FASE_5_RAILWAY_TESTES.md](FASE_5_RAILWAY_TESTES.md)

```
1. Verificar app está rodando
2. Testar conectividade ao banco
3. Testar consultas
4. Validar HTTPS
5. Pronto para produção!
```

**Tempo:** 30 minutos

---

## ✨ Conquistas Até Agora

✅ Conta Railway criada  
✅ Projeto conectado ao GitHub  
✅ Código adaptado e em produção  
✅ Banco de dados criado  
✅ Variáveis configuradas  
✅ Deploy automático ativo  

**Faltam:** Testes e validação final

---

**Status:** FASE 4 concluída  
**Próximo:** FASE 5 - Testes  
**Tempo total:** ~45 minutos (você + Railway)
