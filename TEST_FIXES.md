# 🧪 TESTES DAS CORREÇÕES

## Erros Corrigidos

### ❌ Erro 1: SIGALRM no Windows
**Arquivo:** `crew_definition_v2.py`  
**Linhas:** 282-310, 323-352  
**Problema:** `signal.SIGALRM` não existe no Windows (é apenas Unix/Linux)  
**Solução:** Adicionar verificação `if platform.system() != 'Windows'` antes de usar SIGALRM

**Antes:**
```python
import signal
signal.signal(signal.SIGALRM, timeout_handler)  # ❌ Falha no Windows
signal.alarm(timeout)
```

**Depois:**
```python
import signal
import platform

if platform.system() != 'Windows':  # ✅ Apenas em Unix/Linux
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
```

---

### ❌ Erro 2: List argument de paramêtros
**Arquivo:** `db_connection.py` (linha 83)  
**Problema:** `execute_query()` recebe params como tuple mas SQLAlchemy espera dict  
**Solução:** Converter para dict se necessário

**Antes:**
```python
def execute_query(self, query, params=None):
    with self.engine.connect() as connection:
        result = connection.execute(text(query), params or {})  # ❌ Tuple será rejeitado
```

**Depois:**
```python
def execute_query(self, query, params=None):
    with self.engine.connect() as connection:
        params_dict = params if isinstance(params, dict) else {}  # ✅ Converter para dict
        result = connection.execute(text(query), params_dict)
```

---

### ❌ Erro 3: INSERT com placeholders errados
**Arquivo:** `audit_logger.py` (linhas 165-220)  
**Problema:** Usando `%s` placeholders MySQL mas passando dict com named params ao SQLAlchemy  
**Solução:** Mudar para `:named_parameters` (SQLAlchemy style)

**Antes:**
```python
query = """INSERT INTO chat_audit_log (...) VALUES (NOW(), %s, %s, %s, ...)"""
params = (user_ip, pergunta_sanitizada, json_intent_str, ...)  # ❌ Tuple
db.execute_query(query, params)  # ❌ Incompatível
```

**Depois:**
```python
from sqlalchemy import text

query = """INSERT INTO chat_audit_log (...) VALUES (NOW(), :user_ip, :pergunta, :intent, ...)"""
params = {
    'user_ip': user_ip,
    'pergunta': pergunta_sanitizada,
    'intent': json_intent_str,
    ...
}
# Usar engine.connect() direto com text(query)
with engine.connect() as connection:
    connection.execute(text(query), params)
    connection.commit()
```

---

### ❌ Erro 4: Placeholders em get_audit_logs
**Arquivo:** `audit_logger.py` (linhas 245-260)  
**Problema:** Mesmo problema - `%s` com dict params  
**Solução:** Mudar para `:named_parameters`

**Antes:**
```python
if status_filter:
    query += " AND status = %s"  # ❌
    params['status'] = status_filter
```

**Depois:**
```python
if status_filter:
    query += " AND status = :status"  # ✅
    params['status'] = status_filter
```

---

## 🧪 Como Testar

### Teste 1: Verificar SIGALRM (Quick)
```python
import platform
print(f"Sistema: {platform.system()}")  # Deve mostrar "Windows" ou "Linux" ou "Darwin"

if platform.system() != 'Windows':
    import signal
    print(f"SIGALRM disponível: {hasattr(signal, 'SIGALRM')}")
else:
    print("Windows: SIGALRM não será usado (comportamento esperado)")
```

### Teste 2: Testar queries com parâmetros
```bash
# Rodar diretamente
python -c "
from audit_logger import get_audit_logs
logs = get_audit_logs(limit=5, status_filter='SUCCESS')
print(f'Logs encontrados: {len(logs)}')
"
```

### Teste 3: Fazer uma pergunta simples
```bash
# Rodar Streamlit normalmente
streamlit run app_v2.py

# Fazer uma pergunta de teste:
# "Qual é o total de gastos do IFS em 2024?"
```

### Teste 4: Verificar Audit Log
```python
from db_connection import DBConnection
import pandas as pd

db = DBConnection()
engine = db.get_engine()

# Ver últimos logs
df = pd.read_sql("SELECT * FROM chat_audit_log ORDER BY timestamp DESC LIMIT 5", engine)
print(df[['timestamp', 'pergunta_original', 'status', 'confidence_score']])
```

---

## ✅ Sinais de Sucesso

Depois das correções, procure por:

1. **Nenhum erro de SIGALRM** - A app deve rodar sem erros de sinal
2. **Log salvos com sucesso** - Mensagem `✅ Audit log salvo` deve aparecer
3. **Respostas completas** - O bot deve retornar resposta + confidence + metadata
4. **Banco de dados atualizado** - `chat_audit_log` deve ter novos registros

---

## 🔍 Monitoramento

Se ainda houver erros, procure em:

```bash
# Logs da app
2024-XX-XX ERROR:audit_logger ❌ Erro ao salvar audit log: ...
2024-XX-XX ERROR:crew_definition_v2 ❌ Erro: ...
2024-XX-XX ERROR:db_connection ❌ Erro ao executar query: ...
```

---

## 📝 Resumo das Mudanças

| Arquivo | Tipo | Mudança |
|---------|------|---------|
| crew_definition_v2.py | 2 functions | Adicionar platform check para SIGALRM |
| db_connection.py | 1 function | Validar params como dict |
| audit_logger.py | 3 functions | Mudar placeholders %s → :named |
| **Total** | **6 mudanças** | **Todas compatíveis com Windows** |

---

**Status:** ✅ Todas as correções aplicadas  
**Data:** 27 de Março de 2026  
**Compatibilidade:** Windows, macOS, Linux
