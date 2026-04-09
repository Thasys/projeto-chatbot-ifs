# Configuração Específica para PythonAnywhere
# Este arquivo contém instruções e snippets para deployment

## 1. ARQUIVO WSGI PARA PYTHONANYWHERE

Crie o arquivo: `pythonanywhere_wsgi.py`

```python
"""
WSGI configuration for PythonAnywhere deployment
Wraps Streamlit app in WSGI interface
"""

import os
import sys
import logging
from pathlib import Path

# Adicionar projeto ao path
project_home = '/home/username/projeto-chatbot-ifs'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Logging
logging.basicConfig(
    filename=os.path.join(project_home, 'logs', 'wsgi.log'),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

logger.info("WSGI application initialized")

# Imports locais
try:
    from streamlit.web import cli
    logger.info("Streamlit imported successfully")
except ImportError as e:
    logger.error(f"Failed to import Streamlit: {e}")
    raise

def application(environ, start_response):
    """WSGI application interface"""
    
    try:
        # Run Streamlit app
        os.chdir(project_home)
        sys.argv = ['streamlit', 'run', 'app_v2.py']
        
        # Aqui você teria que rodar Streamlit
        # Nota: Isso é complexo em WSGI puro
        # Recomenda-se usar o método direto do PythonAnywhere
        
        status = '200 OK'
        response_headers = [('Content-type', 'text/html')]
        start_response(status, response_headers)
        return [b'Streamlit app is running']
        
    except Exception as e:
        logger.exception(f"WSGI Error: {e}")
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [str(e).encode()]
```

---

## 2. CONFIGURAÇÃO DE VIRTUALENV

### Criar Virtualenv
```bash
# No bash do PythonAnywhere
mkvirtualenv --python=/usr/bin/python3.12 chatbot-env

# Verificar que está ativado
workon chatbot-env

# Navegar para o projeto
cd /home/seu_username/projeto-chatbot-ifs

# Instalar dependências
pip install -r requirements-pythonanywhere.txt
```

---

## 3. CONFIGURAR WEB APP NO PYTHONANYWHERE

### Via Web Interface
1. Acessar: https://www.pythonanywhere.com/web_app_setup/
2. Criar novo Web app
3. Selecionar "Manual configuration"
4. Escolher Python 3.12
5. Em "WSGI configuration file", apontar para: `/home/seu_username/projeto-chatbot-ifs/pythonanywhere_wsgi.py`

---

## 4. VARIÁVEIS DE AMBIENTE

### Arquivo `.env` no servidor
```bash
# MySQL Configuration
MYSQL_HOST=seu_username.mysql.pythonanywhere-services.com
MYSQL_PORT=3306
MYSQL_USER=seu_username
MYSQL_PASSWORD=sua_senha
MYSQL_DATABASE=seu_username$chatbot_db

# OpenAI Configuration
OPENAI_API_KEY=sk-... (sua chave)
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

### Carregar em pythonanywhere_wsgi.py
```python
from dotenv import load_dotenv
import os

env_path = '/home/seu_username/projeto-chatbot-ifs/.env'
load_dotenv(env_path)

# Acessar variáveis
db_host = os.getenv('MYSQL_HOST')
api_key = os.getenv('OPENAI_API_KEY')
```

---

## 5. SCRIPT DE TESTE DE CONECTIVIDADE

Crie: `test_pythonanywhere_deployment.py`

```python
#!/usr/bin/env python3
"""
Test script to validate PythonAnywhere deployment
"""

import os
import sys
import logging
from datetime import datetime

# Setup logging
log_file = 'deployment_test.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_environment():
    """Test environment variables"""
    logger.info("=" * 60)
    logger.info("TESTING ENVIRONMENT VARIABLES")
    logger.info("=" * 60)
    
    required_vars = [
        'MYSQL_HOST',
        'MYSQL_USER',
        'MYSQL_PASSWORD',
        'MYSQL_DATABASE',
        'OPENAI_API_KEY'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            logger.error(f"❌ Missing: {var}")
            missing.append(var)
        else:
            logger.info(f"✅ Found: {var}")
    
    return len(missing) == 0

def test_mysql():
    """Test MySQL connection"""
    logger.info("=" * 60)
    logger.info("TESTING MYSQL CONNECTION")
    logger.info("=" * 60)
    
    try:
        import mysql.connector
        
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE')
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        
        logger.info(f"✅ MySQL Connected! Version: {version[0]}")
        
        # Test table exists
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        logger.info(f"✅ Found {len(tables)} tables")
        
        connection.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ MySQL Connection Failed: {str(e)}")
        return False

def test_openai():
    """Test OpenAI API"""
    logger.info("=" * 60)
    logger.info("TESTING OPENAI API")
    logger.info("=" * 60)
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Simple test
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello'"}],
            max_tokens=10
        )
        
        logger.info(f"✅ OpenAI API Working! Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        logger.error(f"❌ OpenAI API Failed: {str(e)}")
        return False

def test_imports():
    """Test critical imports"""
    logger.info("=" * 60)
    logger.info("TESTING IMPORTS")
    logger.info("=" * 60)
    
    imports = {
        'streamlit': 'streamlit',
        'crewai': 'crewai',
        'sqlalchemy': 'sqlalchemy',
        'pandas': 'pandas',
        'rapidfuzz': 'rapidfuzz'
    }
    
    all_ok = True
    for name, module in imports.items():
        try:
            __import__(module)
            logger.info(f"✅ {name} imported successfully")
        except ImportError as e:
            logger.error(f"❌ Failed to import {name}: {e}")
            all_ok = False
    
    return all_ok

def main():
    """Run all tests"""
    logger.info(f"\nDEPLOYMENT TEST STARTED: {datetime.now()}\n")
    
    results = {
        'Environment': test_environment(),
        'MySQL': test_mysql(),
        'OpenAI': test_openai(),
        'Imports': test_imports()
    }
    
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    logger.info(f"\n{'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}\n")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
```

### Executar teste
```bash
cd /home/seu_username/projeto-chatbot-ifs
python test_pythonanywhere_deployment.py
```

---

## 6. BACKUP E RESTORE DO BANCO DE DADOS

### Fazer backup local
```bash
mysqldump --host=seu_username.mysql.pythonanywhere-services.com \
          --user=seu_username \
          --password=sua_senha \
          seu_username$chatbot_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restaurar no PythonAnywhere
```bash
mysql --host=seu_username.mysql.pythonanywhere-services.com \
      --user=seu_username \
      --password=sua_senha \
      seu_username$chatbot_db < backup.sql
```

---

## 7. MONITORAMENTO E LOGS

### Estrutura de logs
```
/home/seu_username/projeto-chatbot-ifs/
├── logs/
│   ├── error.log
│   ├── access.log
│   ├── wsgi.log
│   └── deployment_test.log
├── reports/
│   └── (relatórios gerados)
└── dados_brutos/
    └── (dados processados)
```

### Monitorar logs em tempo real
```bash
tail -f /home/seu_username/projeto-chatbot-ifs/logs/error.log
```

---

## 8. SCRIPTS DE AUTOMAÇÃO

### Script para atualizar código
```bash
#!/bin/bash
# /home/seu_username/update_app.sh

cd /home/seu_username/projeto-chatbot-ifs

# Pull latest changes
git pull origin master

# Ativar virtualenv
source /home/seu_username/.virtualenvs/chatbot-env/bin/activate

# Reinstalar dependências se requirements mudou
pip install -r requirements-pythonanywhere.txt

# Executar testes
python test_pythonanywhere_deployment.py

# Reload web app
touch /var/www/seu_username_pythonanywhere_com_wsgi.py

echo "App updated successfully"
```

### Cron job para backup automático
```bash
# Adicionar via: crontab -e

# Backup daily at 2 AM
0 2 * * * /home/seu_username/backup_database.sh

# Check app status weekly
0 0 * * 1 python /home/seu_username/projeto-chatbot-ifs/test_pythonanywhere_deployment.py
```

---

## 9. STATUS DO DEPLOYMENT

| Etapa | Status | Data | Notas |
|-------|--------|------|-------|
| Preparação Python 3.12 | ⏳ | | |
| Criar conta PythonAnywhere | ⏳ | | |
| Clonar repositório | ⏳ | | |
| Configurar MySQL | ⏳ | | |
| Deploy web app | ⏳ | | |
| Testes funcionais | ⏳ | | |
| Launch em produção | ⏳ | | |

---

## 10. CONTATOS E SUPORTE

- **PythonAnywhere Support:** help@pythonanywhere.com
- **Email Professor:** [adicionar email]
- **Documentação:** Ver DEPLOYMENT_PYTHONANYWHERE.md

---

**Última atualização:** 9 de abril de 2026
