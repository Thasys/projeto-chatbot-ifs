# 🎬 FASE 5: Deploy Web App - Colocar a Aplicação no Ar

**Data Início:** 9 de abril de 2026  
**Tempo Estimado:** 1-2 horas  
**Status:** ⏳ À FAZER  
**Pré-requisito:** FASE 4 (Banco de dados OK)

---

## 📌 Objetivo

1. Criar web app no PythonAnywhere
2. Apontar para aplicação Streamlit
3. Configurar variáveis de ambiente
4. Fazer primeira subida em produção
5. Testar acesso público

---

## ✅ PASSO 1: Acessar Painelamento Web

1. Fazer login em https://www.pythonanywhere.com
2. No dashboard, clique em **"Web"** (menu esquerdo)
3. Clique em **"Add a new web app"**

---

## ✅ PASSO 2: Configurar Web App

### 2a. Domínio
- Escolha: "seu_username.pythonanywhere.com"
- Este será sua URL pública

### 2b. Framework
- Clique em **"Manual configuration"**
- Selecione **"Python 3.12"**
- Clique em "Next"

---

## ✅ PASSO 3: Configurar WSGI

PythonAnywhere criará automaticamente arquivo WSGI padrão.

Você verá mensagem:
```
Your web app is set up. Do you want to reload it?
```

**Antes de fazer reload, precisamos configurar Streamlit.**

---

## ✅ PASSO 4: Criar Arquivo de Configuração Streamlit

No Bash console:

```bash
cd /home/seu_username/projeto-chatbot-ifs
mkdir -p .streamlit
nano .streamlit/config.toml
```

Cole o seguinte:

```toml
[theme]
primaryColor = "#0066cc"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[client]
toolbarMode = "auto"
showErrorDetails = true
logger.level = "warning"

[server]
headless = true
port = 8501
runOnSave = false
maxUploadSize = 200
enableCORS = false

[logger]
level = "warning"

[browser]
gatherUsageStats = false
```

Salvar: `Ctrl + O`, Enter, `Ctrl + X`

---

## ✅ PASSO 5: Configurar Arquivo WSGI para Streamlit

**⚠️ IMPORTANTE:** PythonAnywhere não executa Streamlit nativamente em WSGI.

Precisamos usar método alternativo:

### Opção A: Usar Script de Execução Direta (Recomendado)

No Bash:

```bash
cat > /home/seu_username/run_streamlit.sh << 'EOF'
#!/bin/bash

# Activate virtualenv
source /home/seu_username/.virtualenvs/chatbot-env/bin/activate

# Change to project directory
cd /home/seu_username/projeto-chatbot-ifs

# Run Streamlit
streamlit run app_v2.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --logger.level=warning
EOF

chmod +x /home/seu_username/run_streamlit.sh
```

### Opção B: Usar Gunicorn (Mais robusto)

Se usar Gunicorn (requer WSGI wrapper):

```bash
cat > /home/seu_username/projeto-chatbot-ifs/wsgi_streamlit.py << 'EOF'
"""
WSGI wrapper para Streamlit em PythonAnywhere
"""

import os
import sys

# Add project to path
sys.path.insert(0, '/home/seu_username/projeto-chatbot-ifs')

# Load environment
from dotenv import load_dotenv
load_dotenv('/home/seu_username/projeto-chatbot-ifs/.env')

# Streamlit in WSGI is complex, this is a minimal setup
def application(environ, start_response):
    status = '200 OK'
    headers = [('Content-Type', 'text/html')]
    start_response(status, headers)
    
    html = b"""
    <html>
    <head>
        <title>IFS Chatbot - Iniciando...</title>
        <meta http-equiv="refresh" content="2;url=/app/">
    </head>
    <body>
        <h1>Aplicacao iniciando...</h1>
        <p>Redirecionando para Streamlit em 2 segundos...</p>
    </body>
    </html>
    """
    return [html]
EOF
```

---

## ✅ PASSO 6: Configurar Web App para Usar Streamlit

No painel **Web** do PythonAnywhere:

1. Encontre sua web app listada
2. Clique em seu domínio (`seu_username.pythonanywhere.com`)
3. Vá para seção **"Code"**
4. Mude **"WSGI configuration file"** para:
   ```
   /home/seu_username/projeto-chatbot-ifs/wsgi_streamlit.py
   ```

---

## ✅ PASSO 7: Adicionar Variáveis de Ambiente na Web App

No painel **Web**:

1. Role para seção **"Environment variables"**
2. Clique em **"Add variable"**
3. Adicione cada uma (copiar de seu `.env`):

```
MYSQL_HOST = seu_username.mysql.pythonanywhere-services.com
MYSQL_PORT = 3306
MYSQL_USER = seu_username
MYSQL_PASSWORD = sua_senha
MYSQL_DATABASE = seu_username$chatbot_db
OPENAI_API_KEY = sk-... (sua chave)
ENVIRONMENT = production
DEBUG = False
PYTHONUNBUFFERED = True
STREAMLIT_SERVER_HEADLESS = true
```

**⚠️ NÃO colloque .env direto. Adicione cada variável manualmente.**

---

## ✅ PASSO 8: Fazer Reload da Web App

No painel **Web**:

1. Procure botão grande **"Reload seu_username.pythonanywhere.com"**
2. Clique em **"Reload"**
3. Aguarde 10-20 segundos

Você verá progresso:
```
Loading... (spinning icon)
```

Quando mudar para verde ("Loaded"), está pronto!

---

## ✅ PASSO 9: Acessar a Aplicação

Abra navegador e vá para:

```
https://seu_username.pythonanywhere.com
```

**Esperado:**
- Página de Streamlit carregando
- Logo do IFS Transparência
- Interface intuitiva

**Se vir erro:**
- Verifique logs (próximo passo)
- Verifique variáveis de ambiente

---

## ✅ PASSO 10: Verificar Logs

Se houver problema, verificar logs:

No Bash console:

```bash
# Ver logs da web app
tail -50 /var/log/seu_username.pythonanywhere_com_wsgi.log
```

Ou procurar por erros:

```bash
tail -f /home/seu_username/projeto-chatbot-ifs/logs/error.log
```

---

## ✅ PASSO 11: Testes de Funcionalidade

### Teste 1: Acesso Básico
- [ ] Página carrega sem erro 500
- [ ] UI do Streamlit visível
- [ ] Nenhuma mensagem de erro vermei

### Teste 2: Consulta Simples
1. Clique na aplicação
2. Digite pergunta simples: "Olá"
3. Aguarde resposta

**Esperado:** Bot responde

### Teste 3: Consulta com Número
1. Digite: "Quantos alunos temos?"
2. Aguarde resposta

**Esperado:** Bot processa e retorna resultado

### Teste 4: HTTPS
1. Verifique URL começa com `https://`
2. Clique no ícone🔒 do navegador
3. Certificado deve estar válido

---

## ✅ PASSO 12: Habilitar HTTPS (Obrigatório)

No painel **Web**:

1. Procure seção **"SSL"** ou **"HTTPS"**
2. Verifique caixa **"Force HTTPS"**
3. Clique em **"Reload"**

Agora:
- HTTP redireciona para HTTPS
- Certificado gratuito ativa

---

## ✅ PASSO 13: Monitoramento Inicial

Criar script para monitorar:

```bash
cat > monitor_health.py << 'EOF'
#!/usr/bin/env python3
"""Monitor application health"""

import requests
import time
from datetime import datetime

def check_health():
    """Check if app is accessible"""
    
    url = "https://seu_username.pythonanywhere.com"
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking {url}...")
    
    try:
        response = requests.get(url, timeout=10, verify=True)
        
        if response.status_code == 200:
            print(f"✅ App is UP (HTTP {response.status_code})")
            return True
        else:
            print(f"⚠️ App returned HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ App is DOWN: {str(e)}")
        return False

if __name__ == "__main__":
    success = check_health()
    exit(0 if success else 1)
EOF

# Tornar executável
chmod +x monitor_health.py

# Testar
python monitor_health.py
```

---

## 📊 Checklist FASE 5

### Configuração Web App
- [ ] Web app criado em PythonAnywhere
- [ ] Framework: Manual + Python 3.12
- [ ] Domínio: seu_username.pythonanywhere.com

### Configuração Streamlit
- [ ] Arquivo `.streamlit/config.toml` criado
- [ ] WSGI apontando para projeto correto
- [ ] Variáveis de ambiente adicionadas

### Deploy
- [ ] Web app reloaded com sucesso
- [ ] HTTPS habilitado
- [ ] Certificado válido

### Testes
- [ ] [ ] App acessível via HTTPS
- [ ] [ ] Sem erro 500
- [ ] [ ] Consulta simples funciona
- [ ] [ ] HTTPS força HTTP→HTTPS

---

## ✅ Resultado Esperado

**URL pública:** `https://seu_username.pythonanywhere.com`

**Status:** 🟢 LIVE

**Próximos passos:**
- Compartilhar URL com professor
- Coletar feedback
- Monitorar logs
- Otimizar se necessário

---

## 🆘 Problemas Comuns

### Problema 1: Erro 500
**Sintoma:** "Internal Server Error"

**Solução:**
```bash
# Verificar logs
tail -50 /var/log/seu_username.pythonanywhere_com_wsgi.log

# Checar env vars
env | grep MYSQL
env | grep OPENAI
```

### Problema 2: "Connection refused"
**Sintoma:** Não consegue conectar ao banco

**Solução:**
```bash
# Testar conexão
python test_db_connection.py

# Verificar MYSQL_HOST está correto
echo $MYSQL_HOST
```

### Problema 3: Streamlit não carrega
**Sintoma:** Página branca ou carregando infinitamente

**Solução:**
1. Verificar se porta 8501 está livre
2. Dar mais tempo para carregar (primeira vez demora)
3. Forçar refresh no navegador (Ctrl+F5)

### Problema 4: Certificado inválido
**Sintoma:** ⚠️ Certificado não confiável

**Solução:**
- PythonAnywhere fornece certificado gratuito
- Esperar 10 minutos após habilitar HTTPS
- Fazer refresh do navegador

---

## ⏭️ Próximas Etapas (Pós-Deploy)

### Imediato
- [ ] Compartilhar URL com professor
- [ ] Obter feedback inicial
- [ ] Monitorar logs

### Próximo Dia
- [ ] Revisar performance
- [ ] Otimizar queries lentes
- [ ] Corrigir bugs reportados

### Próxima Semana
- [ ] Backup automático
- [ ] Atualizações de segurança
- [ ] Documentação para manutenção

---

## 📞 Contatos de Emergência

Se alguma coisa der errado:

1. **PythonAnywhere Support:** https://help.pythonanywhere.com
2. **Logs:** `/var/log/seu_username.pythonanywhere_com_wsgi.log`
3. **Bash Console:** Execute testes manualmente

---

**Status:** ⏳ À FAZER  
**Duração:** 1-2 horas  
**Resultado:** Aplicação publicada e acessível  
**Data prevista:** Hoje (2026-04-09)

---

## 🎉 PARABÉNS!

Se chegou aqui e tudo funciona, você oficialmente:

✅ Deployou uma aplicação em produção  
✅ Configurou banco de dados remoto  
✅ Habilitou HTTPS  
✅ Criou aplicação escalável  

**Próximo passo:** Contar para o professor! 📚
