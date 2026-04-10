# 🗄️ FASE 4: Configurar Banco de Dados MySQL

**Data Início:** 9 de abril de 2026  
**Tempo Estimado:** 1 hora  
**Status:** ⏳ À FAZER  
**Pré-requisito:** FASE 3 (Setup completo)

---

## 📌 Objetivo

1. Criar banco de dados MySQL no PythonAnywhere
2. Configurar credenciais
3. Testar conectividade
4. Preparar tabelas

---

## ✅ PASSO 1: Criar Banco de Dados no PythonAnywhere

1. Fazer login em https://www.pythonanywhere.com
2. No dashboard, clique em **"Databases"** (menu esquerdo)
3. Você verá seção "MySQL databases"
4. Clique em botão **"Create a new database"**

---

## ✅ PASSO 2: Configurar Banco de Dados

Preencha:

```
Database Name: chatbot_db
(Sem espaços, só letras minúsculas e underscore)
```

Clique em **"Create"**

**Aguarde 1-2 minutos enquanto o banco é criado.**

---

## ✅ PASSO 3: Anotar Credenciais MySQL

Após criar, você verá informações como:

```
Database host: seu_username.mysql.pythonanywhere-services.com
Database name: seu_username$chatbot_db
Database user: seu_username
Database password: [senha_gerada_automaticamente]
```

**COPIAR E COLAR EM ARQUIVO SEGURO (não commitar no Git):**

Criar arquivo `credenciais_mysql.txt`:

```
BANCO DE DADOS MYSQL - PYTHONANYWHERE
=====================================

Host: seu_username.mysql.pythonanywhere-services.com
Database: seu_username$chatbot_db
Username: seu_username
Password: [a_senha_que_vem_do_painel]
Port: 3306

URL Conexão:
mysql://seu_username:PASSWORD@seu_username.mysql.pythonanywhere-services.com/seu_username$chatbot_db
```

---

## ✅ PASSO 4: Atualizar Arquivo .env no PythonAnywhere

No Bash console do PythonAnywhere:

```bash
cd /home/seu_username/projeto-chatbot-ifs
nano .env
```

Atualizar as linhas MySQL com as credenciais reais:

```
# MySQL Configuration
MYSQL_HOST=seu_username.mysql.pythonanywhere-services.com
MYSQL_PORT=3306
MYSQL_USER=seu_username
MYSQL_PASSWORD=COLOQUE_A_SENHA_AQUI
MYSQL_DATABASE=seu_username$chatbot_db
```

Salvar:
- `Ctrl + O`
- Enter
- `Ctrl + X`

---

## ✅ PASSO 5: Testar Conectividade MySQL

No Bash console:

```bash
mysql -h seu_username.mysql.pythonanywhere-services.com \
      -u seu_username \
      -p seu_username$chatbot_db
```

**Quando pedir senha, digite a Password do painel.**

**Se conectar, você verá:**
```
MySQL [seu_username$chatbot_db]>
```

Testar comando simples:

```sql
SELECT VERSION();
```

Deve retornar versão do MySQL.

Sair:

```sql
quit
```

✅ Conectividade MySQL OK!

---

## ✅ PASSO 6: Criar Script de Teste de Banco

No Bash console:

```bash
cat > test_db_connection.py << 'EOF'
#!/usr/bin/env python3
"""Test database connection"""

import os
import sys
import mysql.connector
from mysql.connector import Error

def test_mysql_connection():
    """Test MySQL connection"""
    print("=" * 60)
    print("Testing MySQL Connection")
    print("=" * 60)
    
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE'),
            port=int(os.getenv('MYSQL_PORT', 3306))
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✅ Successfully connected to MySQL Server version {db_info}")
            
            # Test query
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✅ Database version: {version[0]}")
            
            # Check tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✅ Existing tables: {len(tables)}")
            for table in tables:
                print(f"   - {table[0]}")
            
            cursor.close()
            return True
        
    except Error as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if connection.is_connected():
            connection.close()
            print("✅ MySQL connection closed")

if __name__ == "__main__":
    success = test_mysql_connection()
    sys.exit(0 if success else 1)
EOF
```

Executar teste:

```bash
python test_db_connection.py
```

**Resultado esperado:**
```
============================================================
Testing MySQL Connection
============================================================
✅ Successfully connected to MySQL Server version 5.7.x
✅ Database version: 5.7.x
✅ Existing tables: 0
✅ MySQL connection closed
```

✅ Banco de dados pronto!

---

## ✅ PASSO 7: Executar setup_views.py (Opcional Agora)

Se tiver dados para carregar:

```bash
python setup_views.py
```

Ou se tiver arquivo SQL:

```bash
mysql -h seu_username.mysql.pythonanywhere-services.com \
      -u seu_username \
      -p seu_username$chatbot_db < /caminho/para/backup.sql
```

---

## ✅ PASSO 8: Validação Final

Criar script de validação completa:

```bash
cat > validate_db_setup.py << 'EOF'
#!/usr/bin/env python3
"""Validate complete database setup"""

import os
import mysql.connector
from mysql.connector import Error
import sys

def validate_env():
    """Check environment variables"""
    print("ENVIRONMENT VALIDATION")
    print("-" * 40)
    
    required = [
        'MYSQL_HOST',
        'MYSQL_USER',
        'MYSQL_PASSWORD',
        'MYSQL_DATABASE',
        'OPENAI_API_KEY'
    ]
    
    missing = []
    for var in required:
        if var in os.environ:
            value = os.environ[var]
            if var == 'OPENAI_API_KEY':
                value = value[:10] + "..."
            print(f"✅ {var}")
        else:
            print(f"❌ {var} - MISSING")
            missing.append(var)
    
    return len(missing) == 0

def validate_db():
    """Check database connection"""
    print("\nDATABASE VALIDATION")
    print("-" * 40)
    
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE'),
            port=int(os.getenv('MYSQL_PORT', 3306))
        )
        
        print(f"✅ Connection OK - {os.getenv('MYSQL_HOST')}")
        
        cursor = connection.cursor()
        
        # Get server info
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✅ MySQL Version: {version[0]}")
        
        # Check database size
        cursor.execute(f"SELECT DB_NAME(), ROUND(SUM(data_length + index_length) / 1024 / 1024, 1) FROM information_schema.TABLES WHERE table_schema = '{os.getenv('MYSQL_DATABASE')}' GROUP BY DB_NAME()")
        result = cursor.fetchone()
        if result:
            size = result[1] if result[1] else 0
            print(f"✅ Database size: {size} MB")
        
        cursor.close()
        connection.close()
        return True
        
    except Error as e:
        print(f"❌ Database Error: {e}")
        return False

def validate_imports():
    """Check Python imports"""
    print("\nIMPORT VALIDATION")
    print("-" * 40)
    
    imports = [
        ('streamlit', 'Web UI'),
        ('crewai', 'AI Agents'),
        ('mysql.connector', 'MySQL Driver'),
        ('sqlalchemy', 'ORM'),
        ('pandas', 'Data Processing'),
    ]
    
    all_ok = True
    for module, desc in imports:
        try:
            __import__(module)
            print(f"✅ {module} ({desc})")
        except ImportError:
            print(f"❌ {module} ({desc}) - NOT INSTALLED")
            all_ok = False
    
    return all_ok

def main():
    print("=" * 60)
    print("COMPLETE SETUP VALIDATION")
    print("=" * 60)
    
    env_ok = validate_env()
    db_ok = validate_db()
    imports_ok = validate_imports()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if env_ok and db_ok and imports_ok:
        print("✅ ALL VALIDATIONS PASSED - READY FOR PHASE 5")
        return 0
    else:
        print("❌ SOME VALIDATIONS FAILED - CHECK ABOVE")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF
```

Executar validação:

```bash
python validate_db_setup.py
```

---

## 📊 Checklist FASE 4

### Banco de Dados
- [ ] Banco MySQL criado no PythonAnywhere
- [ ] Credenciais copiadas
- [ ] `.env` atualizado com MySQL credentials
- [ ] Arquivo `credenciais_mysql.txt` criado (NÃO commitar)

### Testes
- [ ] `mysql` CLI conecta ao banco
- [ ] `test_db_connection.py` retorna ✅
- [ ] `validate_db_setup.py` retorna ✅
- [ ] Nenhum erro de conexão

### Preparação Dados
- [ ] [ ] OPCIONAL: `setup_views.py` executado
- [ ] [ ] OPCIONAL: Dados carregados via SQL

---

## ✅ Resultado Esperado

Ao final da FASE 4:

```
Database: seu_username$chatbot_db
Host: seu_username.mysql.pythonanywhere-services.com
Connection: ✅ WORKING
Tables: N/A (vazio até carregar dados)
Memory: 0 MB (vazio)
```

**E ao rodar validação:**
```
============================================================
COMPLETE SETUP VALIDATION
============================================================
ENVIRONMENT VALIDATION
----------------------------------------
✅ MYSQL_HOST
✅ MYSQL_USER
✅ MYSQL_PASSWORD
✅ MYSQL_DATABASE
✅ OPENAI_API_KEY

DATABASE VALIDATION
----------------------------------------
✅ Connection OK - seu_username.mysql.pythonanywhere-services.com
✅ MySQL Version: 5.7.x
✅ Database size: 0.0 MB

IMPORT VALIDATION
----------------------------------------
✅ streamlit (Web UI)
✅ crewai (AI Agents)
✅ mysql.connector (MySQL Driver)
✅ sqlalchemy (ORM)
✅ pandas (Data Processing)

============================================================
SUMMARY
============================================================
✅ ALL VALIDATIONS PASSED - READY FOR PHASE 5
```

---

## 🆘 Problemas Comuns

### Problema 1: "Access denied for user"
**Sintoma:** Senha incorreta

**Solução:**
```bash
# Voltar ao painel e pegar senha exata
# Certificar que o_database_name tem "$" e um_username antes
```

### Problema 2: "Can't connect to MySQL server"
**Sintoma:** Host não encontra

**Solução:**
```bash
# Verificar que MYSQL_HOST está correto:
# seu_username.mysql.pythonanywhere-services.com
```

### Problema 3: `mysql` command not found in bash
**Solução:**
```bash
# Usar Python em vez disso:
python test_db_connection.py
```

---

## ⏭️ Próximas Etapas (FASE 5)

**FASE 5: Deploy Web App**

- Configurar Streamlit
- Apontar para web app
- Fazer primeiro reload
- Testar acesso

---

**Status:** ⏳ À FAZER  
**Duração:** ~1 hora  
**Próxima fase:** FASE 5 - Deploy Web App  
**Data prevista:** Hoje (2026-04-09)
