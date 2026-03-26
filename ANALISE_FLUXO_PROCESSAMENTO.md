# 📊 ANÁLISE DE FLUXO DO PROCESSAMENTO

## 🔄 Fluxo Completo de Processamento

```
┌────────────────────────────────────────────────────────────────────┐
│ 1️⃣ INPUT: Pergunta do Usuário                                      │
│    "Qual o total de gastos do IFS em 2024?"                       │
└──────────────────────┬───────────────────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────────────────────┐
│ 2️⃣ VALIDAÇÃO (app_v2.py - process_input)                          │
│    ✅ Input válido? (5-500 caracteres)                            │
│    ✅ Rate limiting? (mín 2s entre requisições)                   │
└──────────────────────┬───────────────────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────────────────────┐
│ 3️⃣ INICIALIZAÇÃO DO CREW                                          │
│    crew = IFSCrewV2()                                             │
│    crew_instance = crew.get_crew(user_input)                      │
│    • Inicializa 3 agentes                                         │
│    • Define 3 tasks em sequência                                  │
└──────────────────────┬───────────────────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────────────────────┐
│ 4️⃣ EXECUÇÃO COM CONFIDENCE                                        │
│    crew_response = crew.execute_with_confidence(crew_instance)    │
│    └─ DENTRO: execute_with_confidence()                           │
│       ├─ Inicia SIGNAL ALARM (se não Windows) ← ⚠️ PROBLEMA AQUI │
│       ├─ Executa crew.kickoff()                                   │
│       ├─ [SE ERRO: except Exception]                              │
│       │  └─ ❌ signal.alarm() NÃO é cancelado! ← ERRO CRÍTICO    │
│       └─ Retorna dict com resposta + confidence                   │
└──────────────────────┬───────────────────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────────────────────┐
│ 5️⃣ AGENTES INTELIGENTES (Sequential Process)                      │
│                                                                   │
│    AGENTE 1: 🔍 Data Detective                                   │
│    ┌─────────────────────────────────────────────────────────┐   │
│    │ Input: "Qual o total de gastos do IFS em 2024?"        │   │
│    │ Tarefa: Extrair intent, entidades, período             │   │
│    │ Ferramentas: search_entity_fuzzy                       │   │
│    │ Output (esperado):                                     │   │
│    │ {                                                      │   │
│    │   "intent": "TOTAL",                                  │   │
│    │   "entities": [...],                                  │   │
│    │   "date_filter": {"year": 2024}                       │   │
│    │   "action": "EXECUTE_SQL"                             │   │
│    │ }                                                      │   │
│    │ ❌ PROBLEMA: Agente retorna texto em vez de JSON?     │   │
│    └─────────────────────────────────────────────────────────┘   │
│                          ↓                                        │
│    AGENTE 2: 🏗️ SQL Expert                                       │
│    ┌─────────────────────────────────────────────────────────┐   │
│    │ Input: JSON do Data Detective                          │   │
│    │ Tarefa: Gerar SQL baseado no intent                    │   │
│    │ Ferramentas:                                           │   │
│    │   • search_sql_memory                                  │   │
│    │   • execute_sql ← EXECUTA A QUERY                      │   │
│    │   • export_csv                                         │   │
│    │ Output (esperado):                                     │   │
│    │ SELECT SUM(valor) FROM v_financas_geral                │   │
│    │ WHERE YEAR(data) = 2024                                │   │
│    │ ❌ PROBLEMA: execute_sql() pode falhar aqui            │   │
│    └─────────────────────────────────────────────────────────┘   │
│                          ↓                                        │
│    AGENTE 3: 📊 Public Analyst                                   │
│    ┌─────────────────────────────────────────────────────────┐   │
│    │ Input: Resultado SQL (tabela markdown)                 │   │
│    │ Tarefa: Formatar resposta em PT-BR claro              │   │
│    │ Output (esperado):                                     │   │
│    │ "Segundo os dados do IFS, o total de gastos..."       │   │
│    │ ❌ PROBLEMA: Pode não receber input válido             │   │
│    └─────────────────────────────────────────────────────────┘   │
└──────────────────────┬───────────────────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────────────────────┐
│ 6️⃣ SE TUDO OK: Extração de Metadata                               │
│    ✅ Parsear resultado                                           │
│    ✅ Calcular confidence score                                   │
│    ✅ Extrair período de dados                                    │
│    ✅ Identificar warnings                                        │
└──────────────────────┬───────────────────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────────────────────┐
│ 7️⃣ AUDITORIA + LOG                                                │
│    log_to_audit(                                                  │
│      pergunta=...,                                               │
│      resposta=...,                                               │
│      confidence=...,                                             │
│      tempo_ms=...                                                │
│    )                                                              │
│    └─ Insere em chat_audit_log com named parameters             │
└──────────────────────┬───────────────────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────────────────────┐
│ 8️⃣ RESPOSTA AO USUÁRIO (app_v2.py)                               │
│    ✅ Markdown com resposta                                      │
│    ✅ Badge de confiança (🟢/🟡/🔴)                              │
│    ✅ Período de dados                                           │
│    ✅ Warnings (se houver)                                       │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🆘 PROBLEMAS IDENTIFICADOS

### ❌ PROBLEMA PRINCIPAL: Signal Alarm não é cancelado em exceções

**Localização:** `crew_definition_v2.py` - `execute_with_confidence()` linhas 340-390

**Código Problemático:**
```python
try:
    if platform.system() != 'Windows':
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)  # ← INICIA!

    resultado = crew.kickoff()  # ← QUALQUER ERRO AQUI

    if platform.system() != 'Windows':
        signal.alarm(0)  # ← NUNCA CHEGA AQUI!

except Exception as e:
    # ❌ O signal.alarm() AINDA ESTÁ ATIVO!
    # Isso causa problema em próximas requisições
    logger.error(f"❌ Erro: {e}")
```

**Por que é problema?**
1. Se `crew.kickoff()` falha, o `signal.alarm()` não é cancelado
2. O alarme continua ativo para a próxima requisição
3. Quando chega o timeout do alarme antigo, levanta exceção inesperada
4. Erro cascata em requisições subsequentes

**Efeito observado:**
```
Requisição 1:
  - Start: signal.alarm(60)
  - Erro em crew.kickoff()
  - ❌ signal.alarm() NÃO cancelado
  - Resposta: "❌ Erro no processamento"

Requisição 2:
  - Start: signal.alarm(60)
  - Erro: "module 'signal' has no attribute 'SIGALRM'"  ← Cascata!
```

---

### ❌ PROBLEMA 2: Agente Data Detective pode não retornar JSON válido

**Localização:** `crew_definition_v2.py` - `get_crew()` linhas 170-190

**Problema:**
```
Agente solicita: "ALWAYS output ONLY a valid JSON object"
Agente recebe: "Okay, I'll output JSON" (texto em vez de JSON!)

Resultado:
  ❌ _extract_json_safe() falha
  ❌ Usa fallback JSON
  ❌ Próximo agente recebe JSON incorreto
  ❌ Query SQL errada
  ❌ Resposta nonsense
```

**Sintomas:**
- Agente retorna texto explicativo em vez de JSON
- CrewAI tem limitações em forçar JSON output
- LLM (GPT-4o) às vezes desobedece instruções

---

### ❌ PROBLEMA 3: execute_sql() pode falhar silenciosamente

**Localização:** `tools.py` - `execute_sql()` linhas 165-220

**Problema:**
```python
def execute_sql(sql_query: str):
    db = DBConnection()
    try:
        sql_query = sql_query.strip()  # ← Pode receber None, empty string
        if not sql_query.upper().startswith("SELECT"):
            return "Error: Only SELECT..."  # ← Resposta texto para erro
        
        df = pd.read_sql(sql_query, db.get_engine())  # ← Pode falhar aqui
        # Erro aqui = Agente não sabe o porquê (mensagem vaga)
```

**Sintomas:**
- Query SQL inválida
- Coluna não encontrada
- Syntax error
- Agente recebe resposta genérica "Error: ..."

---

### ❌ PROBLEMA 4: Context Passing entre Agentes

**Localização:** `crew_definition_v2.py` - Tasks linhas 250-280

**Problema:**
```python
task_mapping = Task(...)  # Data Detective

task_query = Task(
    ...
    context=[task_mapping]  # ← Depende OUTPUT de task_mapping
)
```

**Sintomas:**
- Se Task 1 retorna JSON inválido
- Task 2 recebe lixo na entrada
- Erro propagado para Task 3
- Resposta final sem sentido

---

## 🧪 TESTES PARA VERIFICAR CADA ETAPA

### Teste 1: Data Detective
```python
# Simular o que o agente recebe
user_question = "Qual o total de gastos do IFS em 2024?"

agent = metadata_navigator
task = task_mapping

# Executar apenas Task 1
from crewai import Crew
test_crew = Crew(
    agents=[agent],
    tasks=[task],
    verbose=True
)
resultado = test_crew.kickoff()
print(f"Raw output: {resultado}")
print(f"Is valid JSON? {_extract_json_safe(resultado)}")
```

### Teste 2: SQL Execution
```python
from tools import execute_sql

# Query válida para total
sql = """
SELECT SUM(valor) as total_gastos
FROM v_financas_geral
WHERE YEAR(data) = 2024
"""

resultado = execute_sql(sql)
print(f"SQL Result: {resultado}")
```

### Teste 3: Signal Handling
```python
import signal
import platform
import time

if platform.system() != 'Windows':
    print("Testing signal alarm...")
    
    def handler(signum, frame):
        raise TimeoutError("Alarm triggered!")
    
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(5)
    
    try:
        print("Sleeping 2s...")
        time.sleep(2)
        signal.alarm(0)  # Cancel
        print("✅ Alarm cancelled successfully")
    except TimeoutError:
        print("❌ Alarm triggered before cancel")
```

### Teste 4: Full Process com Logging
```python
# Em app_v2.py, adicionar logging detalhado
import logging

logging.basicConfig(level=logging.DEBUG)

# Depois refazer a pergunta
# Ver logs detalhados de cada etapa
```

---

## 🔍 COMO DIAGNOSTICAR ERROS ESPECÍFICOS

### Se vê: "signal has no attribute SIGALRM"
→ **Causa:** Signal alarm não foi cancelado em requisição anterior
→ **Solução:** Usar try/finally para SEMPRE cancelar alarm

### Se vê: "List argument must consist only of dictionaries"
→ **Causa:** Parâmetro SQL com format errado
→ **Solução:** Usar named parameters `:name` em vez de `%s`

### Se vê: "JSON parsing failed"
→ **Causa:** Agente não retornou JSON válido
→ **Solução:** Forçar mode JSON ou melhorar prompt

### Se vê: "Entity not found"
→ **Causa:** search_entity_fuzzy não encontrou
→ **Solução:** Verificar nomes em BD, usar busca mais flexível

### Se vê: "Empty result set"
→ **Causa:** Query retornou 0 linhas
→ **Solução:** Verificar filtros, período, tabela

---

## 📈 FLUXO DE DEBUGGING

```
Erro ocorre
    ↓
├─ Erro está em execute_with_confidence()? (Signal/Timeout)
│  └─ Solução: Try/Finally para cancelar alarm
│
├─ Erro está em Data Detective agent?
│  └─ Solução: Melhorar prompt, forçar JSON mode
│
├─ Erro está em execute_sql()?
│  └─ Solução: Validar SQL, melhorar mensagens erro
│
├─ Erro está em log_to_audit()?
│  └─ Solução: Usar named parameters corretamente
│
└─ Erro está em app_v2.py?
   └─ Solução: Adicionar logging, validação melhor
```

---

**Status:** Análise completa de fluxo e problemas identificados
**Data:** 27 de Março de 2026
**Próximo passo:** Implementar correções estruturadas
