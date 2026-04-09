# 🔧 GUIA DE CORREÇÃO: AGENTES E QUERIES SQL

**Data:** 9 de abril de 2026  
**Objetivo:** Diagnosticar e corrigir os agentes que não conseguem gerar queries corretas

---

## 📍 Localização dos Problemas nos Agentes

### Problem Map

```
┌─ crew_definition_v2.py
│  ├─ Metadata Navigator Agent (Detecção de período)  ← ⚠️ PROBLEMA 2
│  │  └─ Task: task_mapping
│  │
│  ├─ SQL Architect Agent (Geração de SQL)  ← ❌ PROBLEMA 1 + 3
│  │  └─ Task: task_query
│  │
│  └─ Public Data Analyst Agent (Formatação)
│     └─ Task: task_response (funciona OK)
```

---

## ❌ PROBLEMA 1: SUM Agregado Não Funciona

### Sintoma
```
Pergunta: "Qual o total de gastos do IFS em 2024?"
Resposta: "não há informações disponíveis para a soma do campo 'valor'"
```

### Raiz do Problema

O SQL Architect Agent não está usando `SUM()`.

**Query Incorreta (Provável):**
```sql
SELECT valor FROM v_financas_geral 
WHERE data BETWEEN '2024-01-01' AND '2024-12-31'
LIMIT 1;  -- ← Retorna só uma linha!
```

**Query Correta (Deveria ser):**
```sql
SELECT SUM(valor) as total FROM v_financas_geral 
WHERE data BETWEEN '2024-01-01' AND '2024-12-31';  -- R$ 339.539.000,00
```

### Localização do Agente

**Arquivo:** `crew_definition_v2.py`  
**Linhas:** ~220-250 (SQL Architect Agent)  
**Prompt:** `sql_architect.description` na task

### Código Atual (Problema)
```python
sql_architect = Agent(
    role="SQL Architect",
    goal="Translate intent to proper SQL queries",
    description="""You are a SQL expert...
    Use the following tools: search_sql_memory, execute_sql
    You MUST respond with valid SQL that retrieves the data.""",
    # ← PROBLEMA: Não menciona SUM, GROUP BY, ou agregação!
)
```

### Solução: Melhorar o Prompt

```python
sql_architect = Agent(
    role="SQL Architect",
    goal="Translate intent to proper SQL queries with aggregation",
    description="""You are a SQL expert who knows how to handle aggregations.

CRITICAL RULES:
1. If user asks for TOTALS or SUM, use: SUM(valor)
2. If user asks for TOP N (5 maiores), use: GROUP BY with ORDER BY DESC LIMIT N
3. If user asks for filtering by person/entity: use WHERE with LIKE or =
4. ALWAYS include WHERE date filter for year/month when relevant
5. For diarias, energisa, etc: use LIKE '%ENTITY%' for fuzzy matching

EXAMPLE PATTERNS:
- "Total": SELECT SUM(valor) FROM v_financas_geral WHERE YEAR(data) = 2024
- "Top 5": SELECT entity, SUM(valor) as total FROM v_financas_geral GROUP BY entity ORDER BY total DESC LIMIT 5
- "Person": SELECT SUM(valor) FROM v_financas_geral WHERE pessoa_nome LIKE '%NAME%' AND YEAR(data) = 2024

NEVER return data without aggregation unless user asks for details.""",
    tools=[search_sql_memory, execute_sql],
    # ... resto do agent
)
```

### Test Query

Execute manualmente no MySQL:
```sql
SELECT SUM(valor) as total FROM v_financas_geral 
WHERE YEAR(data) = 2024;
-- Esperado: 339539000 (ou similar)
```

---

## ⚠️ PROBLEMA 2: Período Não Está Máximo

### Sintoma
```
Pergunta: "Quais foram os 5 maiores fornecedores do IFS em 2024?"
Resposta: Valores 21.4% menores (como se fosse só 3 meses)
```

### Análise

Valores recebidos vs esperados:
```
BANCO DO BRASIL:    R$ 108.862.000 vs R$ 141.123.000 (-23.5%)
Se é 1/4 do ano:   R$ 141M / 4 = R$ 35M (não bate)
Se é 3/12 do ano:  R$ 141M * 3/12 = R$ 35.25M (não bate)
Se é 9/12 do ano:  R$ 141M * 9/12 = R$ 105.75M ← BATE! (-25%)
```

**Conclusão:** O período está sendo filtrado para ~9 meses, não 12.

### Possível Causa

Metadata Navigator Agent está calculando período errado.

**Código Problemático (Provável):**
```python
# Evitar em metadata/periodo
hoje = datetime.now()
periodo_inicio = hoje.replace(month=1, day=1)  # 1º de janeiro
periodo_fim = hoje  # ← PROBLEMA: Só até hoje, não até 31 de dezembro!
```

### Localização

**Arquivo:** `crew_definition_v2.py`  
**Método:** `execute_with_confidence()`  
**Linhas:** ~380-390  

**Código Atual:**
```python
now = datetime.now()
metadata = ResponseMetadata(
    confidence=confidence,
    period_start=now.replace(month=1, day=1).strftime('%Y-%m-%d'),
    period_end=now.strftime('%Y-%m-%d'),  # ← PROBLEMA: today, não fim do ano!
    ...
)
```

### Solução

```python
from datetime import datetime

def get_year_period(year_or_current=None):
    """Retorna período completo do ano."""
    if year_or_current is None:
        year = datetime.now().year
    else:
        year = year_or_current
    
    periodo_inicio = f"{year}-01-01"
    periodo_fim = f"{year}-12-31"
    return periodo_inicio, periodo_fim

# Em execute_with_confidence():
period_start, period_end = get_year_period(2024)

metadata = ResponseMetadata(
    confidence=confidence,
    period_start=period_start,  # "2024-01-01"
    period_end=period_end,      # "2024-12-31" ← FIX!
    ...
)
```

### Validação

Execute no MySQL:
```sql
-- Teste com período correto (12 meses)
SELECT favorecido_nome, SUM(valor) as total
FROM v_financas_geral
WHERE data >= '2024-01-01' AND data <= '2024-12-31'
GROUP BY favorecido_nome
ORDER BY total DESC
LIMIT 5;

-- Comparar com período incorreto (9 meses até hoje)
SELECT favorecido_nome, SUM(valor) as total
FROM v_financas_geral
WHERE data >= '2024-01-01' AND data <= DATE_FORMAT(NOW(), '%Y-%m-%d')
GROUP BY favorecido_nome
ORDER BY total DESC
LIMIT 5;
```

---

## 🔍 PROBLEMA 3: Busca Fuzzy Encontrando Registros Errados

### Sintoma
```
Pergunta: "Quanto o IFS gastou com a Energisa em 2024?"
Resposta: R$ 110.831,00 (8.8x menor que esperado R$ 1.250.430,50)
```

### Investigação

1. **Possibilidade A:** Sistema achou "Energisa" correto mas valor está errado
2. **Possibilidade B:** Fuzzy match achou fornecedor diferente
3. **Possibilidade C:** Dados no banco estão realmente diferentes

### Como Debugar

**Passo 1:** Testar busca manual

```sql
-- Ver todos os fornecedores com "ENERGISA"
SELECT DISTINCT favorecido_nome, SUM(valor) as total
FROM v_financas_geral
WHERE favorecido_nome LIKE '%ENERGISA%'
AND YEAR(data) = 2024
GROUP BY favorecido_nome;

-- Resultado esperado:
-- ENERGISA SERGIPE - DISTRIBUIDORA DE ENERGIA S.A. | 1250430.50
```

**Passo 2:** Ver o que o agent está achando

Adicionar logging em `tools.py`:
```python
def search_entity_fuzzy(entity_name: str, entity_type: str = "fornecedor"):
    """Busca fuzzy com logging."""
    logger.info(f"[FUZZY] Buscando: {entity_name} (tipo: {entity_type})")
    
    # Busca fuzzy existente
    resultado = perform_fuzzy_search(entity_name)
    
    logger.info(f"[FUZZY] Melhor match: {resultado['nome']} (score: {resultado['score']})")
    logger.info(f"[FUZZY] Valor encontrado: {resultado.get('valor', 'N/A')}")
    
    return resultado
```

### Possível Solução

O cutoff fuzzy pode estar muito baixo (60%):

```python
# Em tools.py - procurar por fuzzy_match ou RapidFuzz

# ANTES:
best_match = fuzz.token_set_ratio(search_term, candidate)
if best_match >= 60:  # ← 60% é muito baixo
    results.append(...)

# DEPOIS:
best_match = fuzz.token_set_ratio(search_term, candidate)
if best_match >= 80:  # ← 80% é mais seletivo
    results.append(...)
```

---

## ✅ O QUE FUNCIONA: Pergunta 5

### Por que funciona?

```
Query estrutura:
SELECT pessoa_nome, SUM(valor)
FROM v_financas_geral
WHERE id_natureza = (SELECT id FROM naturezas WHERE nome LIKE '%DIARIAS%')
GROUP BY pessoa_nome
ORDER BY SUM(valor) DESC
LIMIT 5
```

**Elementos corretos:**
- ✅ SUM() agregation
- ✅ GROUP BY
- ✅ ORDER BY DESC
- ✅ LIMIT 5
- ✅ WHERE com LIKE fuzzy
- ✅ Período 2024 implícito

Este é o **modelo de referência** para corrigir os agentes!

---

## 🛠️ Roteiro de Correção (1-2 horas)

### 1️⃣ Ativar Logging Completo (15 min)

**Arquivo:** `crew_definition_v2.py`

Adicioned após `resultado = crew.kickoff()`:
```python
logger.info(f"=== DEBUG CREW RESULT ===")
logger.info(f"Raw result type: {type(resultado)}")
logger.info(f"Raw result: {str(resultado)[:500]}")
logger.info(f"Result length: {len(str(resultado))}")
logger.info(f"=======================")
```

**Arquivo:** `tools.py`

Em cada função, adicionar:
```python
@tool("Execute SQL Query")
def execute_sql(sql_query: str):
    logger.info(f"[SQL EXEC] Query: {sql_query}")
    try:
        result = db.execute(sql_query)
        logger.info(f"[SQL EXEC] Rows affected: {len(result)}")
        logger.info(f"[SQL EXEC] Result:" {result[:2]}")  # Primeiras 2 linhas
        return result
    except Exception as e:
        logger.error(f"[SQL EXEC] Error: {e}")
        raise
```

### 2️⃣ Melhorar Prompt do SQL Architect (30 min)

**Arquivo:** `crew_definition_v2.py`

Modificar description do `sql_architect` Agent conforme indicado acima.

### 3️⃣ Corrigir Período em ResponseMetadata (15 min)

**Arquivo:** `crew_definition_v2.py`

Sempre usar ano completo (01-01 até 12-31).

### 4️⃣ Validar com Queries SQL (15 min)

Executar as 5 queries de validação no MySQL Client.

### 5️⃣ Reexecutar Testes (30 min)

```bash
python test_simples_v2.py
```

---

## 📋 Checklist de Diagnóstico

Antes de corrigir, preencher:

- [ ] Logging de ResultSQL adicionado
- [ ] SQL Architect prompt melhorado
- [ ] Período fixado em ano inteiro
- [ ] 5 queries SQL validadas no MySQL
- [ ] test_simples_v2.py roda sem erros
- [ ] Pergunta 1: Retorna R$ 339.539.000 ±5%
- [ ] Pergunta 2: BANCO DO BRASIL = R$ 141.123.000 ±5%
- [ ] Pergunta 3: ENERGISA = R$ 1.250.430 ±5%
- [ ] Pergunta 4: Propriá = valor correto ou "não encontrado"
- [ ] Pergunta 5: RUTH SALES = R$ 33.225,30 (EXATO)

---

**Status:** 🔴 AGUARDANDO IMPLEMENTAÇÃO  
**Owner:** Developer  
**Deadline:** Hoje

---

*Guia de Diagnóstico e Correção - 9 de abril de 2026*
