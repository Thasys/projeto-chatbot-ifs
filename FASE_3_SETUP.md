# 🚀 FASE 3: Setup - Clonando Repositório e Configurando Ambiente

**Data Início:** 9 de abril de 2026  
**Tempo Estimado:** 1-2 horas  
**Status:** ⏳ À FAZER  
**Pré-requisito:** FASE 2 (Conta criada)

---

## 📌 Objetivo

1. Clonar repositório GitHub no PythonAnywhere
2. Criar virtualenv Python 3.12
3. Instalar dependências
4. Validar conectividade

---

## ✅ Instruções Detalhadas

### PASSO 1: Abrir Bash Console no PythonAnywhere

1. Fazer login em https://www.pythonanywhere.com
2. No dashboard, clique em **"Consoles"** (menu esquerdo)
3. Clique em **"Bash"** para abrir novo console Bash
4. Você verá:
```
15:30 ~ $
```

---

### PASSO 2: Navegar para Home e Clonar Repositório

Digite no bash:

```bash
cd /home/seu_username
```

Substituir `seu_username` pelo seu username do PythonAnywhere.

**Exemplo:** `cd /home/tharsys`

Clonar o repositório:

```bash
git clone https://github.com/Thasys/projeto-chatbot-ifs.git
```

**Output esperado:**
```
Cloning into 'projeto-chatbot-ifs'...
remote: Enumerating objects: 542, done.
...
Resolving deltas: 100% (xxx/xxx), done.
```

Isso pode levar 1-2 minutos.

---

### PASSO 3: Verificar Arquivos Clonados

```bash
cd projeto-chatbot-ifs
ls -la
```

Deve retornar:
```
total XXX
drwxr-xr-x  15 seu_username seu_username XXX Apr  9 14:50 .
drwxr-xr-x   3 seu_username seu_username XXX Apr  9 14:50 ..
-rw-r--r--   1 seu_username seu_username XXXX Apr  9 14:50 CHANGELOG.md
-rw-r--r--   1 seu_username seu_username XXXX Apr  9 14:50 CONTRIBUTING.md
-rw-r--r--   1 seu_username seu_username XXXX Apr  9 14:50 DEPLOYMENT_CHECKLIST.md
drwxr-xr-x   3 seu_username seu_username  XXX Apr  9 14:50 docs/
drwxr-xr-x   3 seu_username seu_username  XXX Apr  9 14:50 etl_scripts/
drwxr-xr-x   2 seu_username seu_username  XXX Apr  9 14:50 reports/
-rw-r--r--   1 seu_username seu_username XXXX Apr  9 14:50 app_v2.py
...
```

✅ Se viu `app_v2.py`, `requirements-pythonanywhere.txt`, etc., está correto!

---

### PASSO 4: Criar Diretórios Necessários

```bash
mkdir -p logs reports dados_brutos
chmod -R 755 logs reports
```

---

### PASSO 5: Criar Virtualenv com Python 3.12

**⚠️ IMPORTANTE:** Use exatamente este comando

```bash
mkvirtualenv --python=/usr/bin/python3.12 chatbot-env
```

**O que deve acontecer:**
```
created virtual environment CPython3.12.0 in 2.34s
Running virtualenv with interpreter /usr/bin/python3.12
command to activate the virtual env: . /home/seu_username/.virtualenvs/chatbot-env/bin/activate
```

**Seu prompt deve mudar para:**
```
(chatbot-env) 15:35 ~/projeto-chatbot-ifs $
```

✅ Se vir `(chatbot-env)` no início da linha, você está no virtualenv correto!

---

### PASSO 6: Verificar Versão do Python

```bash
python --version
```

Deve retornar:
```
Python 3.12.x
```

✅ Se retornar 3.12, perfeito!

---

### PASSO 7: Atualizar pip

```bash
pip install --upgrade pip setuptools wheel
```

Pode levar alguns segundos.

---

### PASSO 8: Instalar Dependências do Projeto

```bash
pip install -r requirements-pythonanywhere.txt
```

**⚠️ AVISO:** Isso pode levar **5-10 minutos**. Seja paciente!

**Output durante instalação:**
```
Collecting streamlit
  Downloading streamlit-1.51.0-py2.py3-none-any.whl (XXX kB)
Installing collected packages: ...
Successfully installed ...
```

**Ao final, deve ver:**
```
Successfully installed [lista de pacotes]
```

---

### PASSO 9: Verificar Instalação

```bash
python -c "import streamlit, crewai, sqlalchemy; print('✅ All core imports working')"
```

Deve retornar:
```
✅ All core imports working
```

Se vir erro, execute:
```bash
pip list | grep -E "streamlit|crewai|sqlalchemy"
```

---

### PASSO 10: Criar Arquivo .env

**⚠️ IMPORTANTE:** Este arquivo contém credenciais sensíveis

```bash
nano /home/seu_username/projeto-chatbot-ifs/.env
```

Cole o seguinte conteúdo (adaptando com suas credenciais):

```
# MySQL Configuration
MYSQL_HOST=seu_username.mysql.pythonanywhere-services.com
MYSQL_PORT=3306
MYSQL_USER=seu_username
MYSQL_PASSWORD=sua_senha_mysql
MYSQL_DATABASE=seu_username$chatbot_db

# OpenAI Configuration
OPENAI_API_KEY=sk-... (sua chave aqui)
OPENAI_MODEL=gpt-4-turbo-preview

# Application Settings
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
MAX_WORKERS=4

# Streamlit Configuration
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_PORT=8501
STREAMLIT_LOGGER_LEVEL=warning
PYTHONUNBUFFERED=1
```

**Para salvar:**
- Pressione: `Ctrl + O`
- Enter para confirmar nome
- Pressione: `Ctrl + X` para sair

✅ Arquivo .env criado!

---

### PASSO 11: Validar Arquivo .env

```bash
cat /home/seu_username/projeto-chatbot-ifs/.env
```

Deve retornar o conteúdo que você colou.

---

### PASSO 12: Modificar .gitignore (IMPORTANTE!)

Certificar que .env não será commitado:

```bash
cat .gitignore | grep ".env"
```

Se não retornar `.env`, adicionar:

```bash
echo ".env" >> .gitignore
```

---

### PASSO 13: Teste de Conectividade Básico

Criar script de teste:

```bash
cat > test_pa_setup.py << 'EOF'
#!/usr/bin/env python3
import os
import sys

print("=" * 60)
print("PYTHONANYWHERE SETUP TEST")
print("=" * 60)

# Test 1: Python version
print(f"\n✅ Python: {sys.version}")

# Test 2: Virtualenv
if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    print(f"✅ Virtualenv: {sys.prefix}")
else:
    print("❌ NOT in virtualenv!")

# Test 3: Imports
imports = ['streamlit', 'crewai', 'sqlalchemy', 'pandas', 'mysql.connector']
for imp in imports:
    try:
        __import__(imp)
        print(f"✅ {imp}")
    except ImportError as e:
        print(f"❌ {imp}: {e}")

# Test 4: Environment variables
env_vars = ['MYSQL_HOST', 'OPENAI_API_KEY', 'ENVIRONMENT']
for var in env_vars:
    if var in os.environ:
        val = os.environ[var]
        # Hide API key
        if var == 'OPENAI_API_KEY':
            val = val[:10] + "..."
        print(f"✅ {var}: present")
    else:
        print(f"❌ {var}: missing")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
EOF
```

Executar teste:

```bash
python test_pa_setup.py
```

Espere por saída com todos ✅.

---

## 📊 Checklist PASSO A PASSO

### Clonagem
- [ ] `cd /home/seu_username`
- [ ] `git clone` repositório completo
- [ ] `ls -la` mostra arquivos do projeto
- [ ] `app_v2.py` existe

### Virtualenv
- [ ] `mkvirtualenv` criado com Python 3.12
- [ ] Prompt mostra `(chatbot-env)`
- [ ] `python --version` retorna 3.12.x

### Dependências
- [ ] `pip install` completou sem erros
- [ ] `import streamlit, crewai, sqlalchemy` funciona
- [ ] `pip list` mostra todos pacotes

### Configuração
- [ ] `.env` criado com variáveis corretas
- [ ] `.gitignore` contém `.env`
- [ ] `test_pa_setup.py` retorna todos ✅

---

## ✅ Resultado Esperado

Ao final da FASE 3, você deve ter:

```
/home/seu_username/
├── projeto-chatbot-ifs/              ← Repositório clonado
│   ├── app_v2.py
│   ├── .env                          ← Variáveis de ambiente
│   ├── requirements-pythonanywhere.txt
│   ├── logs/                         ← Diretório para logs
│   ├── reports/                      ← Diretório para relatórios
│   ├── docs/
│   ├── etl_scripts/
│   └── ... (outros arquivos)
└── .virtualenvs/
    └── chatbot-env/                  ← Virtualenv Python 3.12
        ├── bin/
        └── lib/
```

**E no bash:**
```bash
(chatbot-env) 15:45 ~/projeto-chatbot-ifs $
```

---

## 🆘 Problemas Comuns

### Problema 1: Clone falha (Timeout)
**Sintoma:** `fatal: unable to access repository`

**Solução:**
```bash
# Esperar um minuto
# Tentar novamente
git clone https://github.com/Thasys/projeto-chatbot-ifs.git
```

### Problema 2: Python 3.12 não encontrado
**Sintoma:** `could not find /usr/bin/python3.12`

**Solução:**
```bash
# Listar versões disponíveis
ls /usr/bin/python*

# Se tiver 3.11, usar:
mkvirtualenv --python=/usr/bin/python3.11 chatbot-env
```

### Problema 3: pip install muito lento
**Sintoma:** Instalação travada por minutos

**Normal:** Alguns pacotes grande (como pandas, crewai) podem levar 5-10 min
- **Solução:** Aguardar pacientemente

### Problema 4: Erro de permissão em .env
**Sintoma:** `Permission denied` ao criar .env

**Solução:**
```bash
touch .env
nano .env
chmod 600 .env
```

---

## ⏭️ Próximas Etapas (FASE 4)

Após FASE 3 completa:

**FASE 4: Configurar Banco de Dados MySQL**

```bash
# No PythonAnywhere:
# 1. Criar banco de dados
# 2. Executar setup_views.py
# 3. Testar conectividade
```

---

## 📝 Comando Rápido (Todos os PASSOS em Sequência)

Se preferir executar tudo de uma vez:

```bash
# 1. Navegar
cd /home/seu_username

# 2. Clonar
git clone https://github.com/Thasys/projeto-chatbot-ifs.git
cd projeto-chatbot-ifs

# 3. Criar dirs
mkdir -p logs reports dados_brutos

# 4. Virtualenv
mkvirtualenv --python=/usr/bin/python3.12 chatbot-env

# 5. Atualizar pip
pip install --upgrade pip setuptools wheel

# 6. Instalar deps
pip install -r requirements-pythonanywhere.txt

# 7. Testar
python -c "import streamlit, crewai, sqlalchemy; print('✅ OK')"

echo "✅ PHASE 3 COMPLETE!"
```

---

**Status:** ⏳ À FAZER  
**Duração estimada:** 1-2 horas (incluindo tempo de instalação)  
**Próxima fase:** FASE 4 - Banco de Dados MySQL  
**Data esperada:** Hoje (2026-04-09)
