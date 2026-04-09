# Python 3.12 Compatibility Guide

**Objetivo:** Garantir compatibilidade do projeto com Python 3.12 (requisito para PythonAnywhere)

**Data:** 9 de abril de 2026

---

## 📋 Status Atual

- **Versão Atual:** Python 3.13-slim (Dockerfile)
- **Versão Alvo:** Python 3.12.x (PythonAnywhere suporta)
- **Versão Mínima Requerida:** Python 3.10

---

## 🔄 Mudanças Necessárias

### 1. Atualizar Dockerfile

**Alterar de:**
```dockerfile
FROM python:3.13-slim AS builder
```

**Para:**
```dockerfile
FROM python:3.12-slim AS builder
```

**Razão:** PythonAnywhere não suporta Python 3.13 no momento (2026).

---

### 2. Atualizar python-requires no setup.py (se existir)

Se há setup.py, adicionar ou atualizar:
```python
python_requires='>=3.10,<4.0'
```

---

### 3. Dependências Compatíveis com Python 3.12

#### ✅ Seguro (Totalmente compatível)
```
streamlit>=1.28.0
crewai>=0.20.0
pandas>=2.0.0
sqlalchemy>=2.0.0
python-dotenv>=1.0.0
rapidfuzz>=3.5.0
unidecode>=1.3.0
```

#### ⚠️ Requer Atenção
```
mysql-connector-python>=8.1.0  # Pode exigir compilação C
```

**Solução:** Se houver problemas, usar `PyMySQL` como alternativa:
```python
# Em vez de mysql-connector-python, usar:
PyMySQL>=1.1.0
```

#### ❌ Evitar
- Python 2.7 only packages
- Python 3.8 or older only compatible packages

---

## 🧪 Testes de Compatibilidade

### Local (Seu Computador)

#### 1. Instalar Python 3.12
```bash
# Windows
# Baixar de https://www.python.org/downloads/release/python-3120/

# macOS
brew install python@3.12

# Linux
sudo apt-get install python3.12 python3.12-venv
```

#### 2. Criar Virtualenv com Python 3.12
```bash
# Windows
python -m venv venv_py312

# macOS/Linux
python3.12 -m venv venv_py312

# Ativar
# Windows
venv_py312\Scripts\activate

# macOS/Linux
source venv_py312/bin/activate
```

#### 3. Instalar Dependências
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements-pythonanywhere.txt
```

#### 4. Executar Testes
```bash
# Testes unitários
pytest tests/ -v

# Teste de import
python -c "import streamlit, crewai, sqlalchemy; print('✅ All imports OK')"

# Teste da app
streamlit run app_v2.py
```

#### 5. Verificar Versões
```bash
python --version
pip show streamlit crewai sqlalchemy
```

### PythonAnywhere

1. Na conta, entrar em Bash console
2. Executar:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.12 chatbot-env-test
   pip install -r requirements-pythonanywhere.txt
   python test_pythonanywhere_deployment.py
   ```

---

## 📝 Checklist de Verificação

- [ ] Python 3.12 instalado localmente
- [ ] Virtualmente isolado criado com sucesso
- [ ] requirements-pythonanywhere.txt instala sem erros
- [ ] Nenhum erro de incompatibilidade de versão
- [ ] Todos os imports funcionam
- [ ] app_v2.py executa sem erros
- [ ] Testes unitários passam
- [ ] Dockerfile atualizado para Python 3.12
- [ ] Nenhuma warning sobre deprecated features

---

## ⚠️ Problemas Comuns e Soluções

### Problema 1: ImportError com mysql-connector-python
```
ImportError: No module named 'mysql.connector'
```

**Solução:**
```bash
pip uninstall mysql-connector-python
pip install PyMySQL
```

E atualizar código:
```python
# De:
import mysql.connector

# Para:
import pymysql
pymysql.install_as_MySQLdb()
```

### Problema 2: Erro de compilação C
```
ERROR: Could not build wheels for some packages
```

**Razão:** Pacote requer compilação nativa (gcc, g++).

**Soluções:**
1. Atualizar para versão mais recente (binária disponível)
2. Usar wheel pré-compilado
3. Ou usar pacote alternativo

### Problema 3: Deprecation Warnings
```
DeprecationWarning: ...
```

**Ação:** Verificar se versão mais recente do pacote resolve.

---

## 🔗 Recursos Úteis

- [Python 3.12 Release Notes](https://docs.python.org/3/whatsnew/3.12.html)
- [PythonAnywhere Python Versions](https://help.pythonanywhere.com/pages/PythonVersions/)
- [Migrate code to Python 3.12](https://docs.python.org/3/library/2to3.html)

---

## 📊 Matriz de Compatibilidade

| Componente | Python 3.11 | Python 3.12 | Python 3.13 | Nota |
|-----------|-------------|------------|------------|------|
| streamlit | ✅ | ✅ | ✅ | Totalmente suportado |
| crewai | ✅ | ✅ | ✅ | Versão >= 0.20 |
| sqlalchemy | ✅ | ✅ | ✅ | Versão >= 2.0 |
| pandas | ✅ | ✅ | ✅ | Versão >= 2.0 |
| mysql-connector | ✅ | ✅ | ✅ | Pode ter problemas de compilação |
| PyMySQL | ✅ | ✅ | ✅ | Alternativa mais leve |
| **PythonAnywhere** | ✅ | ✅ | ❌ | Suporte limitado em 2026 |

---

## 🚀 Próximos Passos

1. **Hoje:** Atualizar Dockerfile para Python 3.12
2. **Amanhã:** Testar localmente com Python 3.12
3. **Esta semana:** Atualizar requirements-pythonanywhere.txt
4. **Próxima semana:** Testar em PythonAnywhere

---

**Criado:** 9 de abril de 2026  
**Última atualização:** (atualizar conforme progresso)  
**Status:** 🔄 Em andamento
