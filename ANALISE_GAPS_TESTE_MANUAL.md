# 📊 ANÁLISE COMPARATIVA: TESTE MANUAL vs RESPOSTAS ESPERADAS

**Data:** 9 de abril de 2026  
**Status:** ⚠️ PROBLEMAS IDENTIFICADOS  
**Severidade:** CRÍTICA

---

## 🔍 Resumo Executivo

| Pergunta | Status | Problema | Severidade |
|----------|--------|----------|-----------|
| 1 - Total 2024 | ❌ FALHA | Retorna "sem informações" em vez de R$ 339.539.000 | 🔴 CRÍTICA |
| 2 - Top 5 Fornecedores | ⚠️ PARCIAL | Valores 20-30% menores que esperado | 🔴 CRÍTICA |
| 3 - Energisa | ⚠️ PARCIAL | Retorna R$ 110.831 vs esperado R$ 1.250.430 (8.8x menor) | 🔴 CRÍTICA |
| 4 - Campus Propriá Jan | ⚠️ INCERTO | "Sem transações" - pode estar correto | 🟡 MENOR |
| 5 - Diárias Civil | ✅ OK | Valores exatos e pessoas corretas | 🟢 OK |

**Taxa de Sucesso:** 1/5 (20%) ❌

---

## 📋 Análise Detalhada por Pergunta

### ❌ PERGUNTA 1: "Qual o total de gastos do IFS em 2024?"

#### Resposta Recebida
```
"Segundo os dados do IFS, não há informações disponíveis para a soma do 
campo 'valor' neste momento. Isso pode ocorrer por diversas razões, 
como ausência de registros na base de dados ou falta de integração 
correta com a fonte de dados para capturar os valores necessários."
```

#### Resposta Esperada
```
"Segundo os dados do IFS, o total de gastos em 2024 foi de aproximadamente 
R$ 339.539.000,00"
```

#### Análise do Erro
| Item | Esperado | Recebido | Status |
|------|----------|----------|--------|
| **Formato** | Valor numérico em R$ | Mensagem de erro | ❌ FALHA |
| **Valor** | R$ 339.539.000,00 | "não há informações" | ❌ FALHA |
| **Tipo Query** | SUM(valor) de toda v_financas_geral | Não conseguiu executar | ❌ FALHA |

#### Possíveis Causas

**Ranking de Probabilidade:**

1. **[ALTA PROB 70%]** Agentes não conseguem fazer query tipo SUM/agregação
   - Problema: SQL gerado está incorreto
   - Indício: Agent não identifica que precisa SUM(valor)
   - Solução: Melhorar prompt do SQL Architect

2. **[MÉDIA PROB 20%]** Conexão com banco ou view não está acessível
   - Problema: v_financas_geral pode estar vazia ou inacessível
   - Indício: Mensagem mencionada "ausência de registros na base de dados"
   - Solução: Validar conexão MySQL e dados na view

3. **[BAIXA PROB 10%]** Converter de CrewOutput para string cortou dados
   - Problema: str(CrewOutput) pode estar vindo vazio
   - Indício: Raro mas possível com fix anterior
   - Solução: Adicionar logging extra ao execute_with_confidence()

---

### ⚠️ PERGUNTA 2: "Quais foram os 5 maiores fornecedores do IFS em 2024?"

#### Resposta Recebida
```
BANCO DO BRASIL SA:              R$ 108.862.000,00  ← Esperado: R$ 141.123.000,00 (-23.5%)
INST.FED.DE EDUC.CIENC.E TEC:    R$ 100.603.000,00  ← Esperado: R$ 118.285.000,00 (-14.9%)
CAIXA ECONOMICA FEDERAL:         R$  80.271.600,00  ← Esperado: R$ 103.296.000,00 (-22.3%)
GEAP AUTOGESTAO EM SAUDE:        R$   4.455.740,00  ← Esperado: R$   5.782.570,00 (-23.0%)
BANCO SANTANDER (BRASIL) S.A.:   R$   3.737.070,00  ← Esperado: R$   4.867.730,00 (-23.2%)
```

#### Análise do Erro
| Item | Esperado | Recebido | Delta |
|------|----------|----------|-------|
| **Top 1** | R$ 141.123.000 | R$ 108.862.000 | -23.5% ❌ |
| **Top 2** | R$ 118.285.000 | R$ 100.603.000 | -14.9% ❌ |
| **Top 3** | R$ 103.296.000 | R$  80.271.600 | -22.3% ❌ |
| **Top 4** | R$   5.782.570 | R$   4.455.740 | -23.0% ❌ |
| **Top 5** | R$   4.867.730 | R$   3.737.070 | -23.2% ❌ |
| **Média** | --- | --- | **-21.4%** |

#### Padrão Observado
- ✅ Nomes corretos (5 fornecedores identific ados corretamente)
- ✅ Ordem correta (maior para menor)
- ❌ Valores consistentemente 20-23% MENORES

#### Possíveis Causas

**Ranking de Probabilidade:**

1. **[MUITO ALTA 80%]** Período différente ou filtro extra na query
   - Problema: Query pode estar filtrando período parcial de 2024
   - Indício: Redução uniforme ~-21% sugere período reduzido (3 meses instead 12?)
   - Teste: Verificar se a query incluir todo 2024 (2024-01-01 até 2024-12-31)
   - Solução: Debug do SQL gerado pelos agentes

2. **[MÉDIA 15%]** Campos de data não alinhados entre view e código
   - Problema: DATE_FIELD pode ser diferente do esperado
   - Indício: Actor não conseguir identificar período corretamente
   - Solução: Verificar estrutura de v_financas_geral

3. **[BAIXA 5%]** Bug em duplicação de valores (JOIN incorreto)
   - Problema: SQL pode ter duplicado registros parcialmente
   - Indício: Estatísticamente improvável
   - Solução: Auditoria de SQL queries executadas

---

### ⚠️ PERGUNTA 3: "Quanto o IFS gastou com a Energisa em 2024?"

#### Resposta Recebida
```
"Segundo os dados do IFS, o total acumulado na coluna 'valor' é de 
R$ 110.831,00"
```

#### Resposta Esperada (Opção A)
```
"Segundo os dados do IFS, o gasto com ENERGISA SERGIPE - DISTRIBUIDORA 
DE ENERGIA S.A. em 2024 foi de R$ 1.250.430,50"
```

#### Análise do Erro
| Item | Esperado | Recebido | Ratio |
|------|----------|----------|-------|
| **Valor** | R$ 1.250.430,50 | R$ 110.831,00 | 8.8x MENOR ❌ |
| **Razão** | Busca fuzzy por "Energisa" | Encontrou algo menor | ??? |
| **Status** | ✅ Encontrou | ⚠️ Encontrou menos | INCONSISTENTE |

#### Possíveis Causas

1. **[MUITO ALTA 85%]** Busca fuzzy encontrou fornecedor errado ou parcial
   - Problema: Fuzzy match por "Energisa" pode ter capturado:
     - Forma abreviada incorreta
     - Registro duplicado/parcial em banco
     - Múltiplos registros somando errado
   - Indício: Valor muito menor (8.8x) não é erro de período
   - Solução: 
     - Validar query gerada
     - Testar busca fuzzy de "Energisa" no SQL
     - Verificar se "ENERGISA SERGIPE" existe no banco

2. **[BAIXA 15%]** Dados incorretos no banco de dados
   - Problema: Valor real pode ser R$ 110.831 (sistema está correto)
   - Indício: Documentação esperada pode estar errada
   - Solução: Validação contra banco de dados real

---

### ⚠️ PERGUNTA 4: "Qual foi o gasto total do Campus de Propriá em janeiro de 2024?"

#### Resposta Recebida
```
"Para o mês de janeiro de 2024, não foram encontradas transações registradas 
para o INSTITUTO FED. DE SERGIPE - CAMPUS PROPRIA. Isso indica que, de acordo 
com os critérios especificados para a pesquisa, não houve movimentações 
financeiras naquele mês."
```

#### Status
- ✅ Campus foi identificado (INSTITUTO FED. DE SERGIPE - CAMPUS PROPRIA)
- ✅ Período foi identificado (janeiro de 2024)
- ⚠️ Resultado pode estar correto OU incorreto (precisa validação)

#### O que fazer
1. Verificar no banco: quantos registros existem para Campus Propriá em JAN/2024
2. Validar também: dados de JAN/2024 para IFS inteiro

---

### ✅ PERGUNTA 5: "Quais foram as maiores despesas com diárias em 2024?"

#### Resposta Recebida
```
RUTH SALES GAMA DE ANDRADE:         R$ 33.225,30  ✅
MARCUS ALEXANDRE NORONHA DE BRITO:  R$ 21.492,70  ✅
IDER DE SANTANA SANTOS:             R$ 11.248,10  ✅
CARLOS MENEZES DE SOUZA JUNIOR:     R$  9.781,67  ✅
JOSE OSMAN DOS SANTOS:              R$  9.662,04  ✅
```

#### Análise
| Item | Esperado | Recebido | Status |
|------|----------|----------|---------|
| **Pessoa 1** | RUTH SALES / R$ 33.225,30 | RUTH SALES / R$ 33.225,30 | ✅ EXATO |
| **Pessoa 2** | MARCUS ALEXANDRE / R$ 21.492,70 | MARCUS ALEXANDRE / R$ 21.492,70 | ✅ EXATO |
| **Pessoa 3** | IDER DE SANTANA / R$ 11.248,10 | IDER DE SANTANA / R$ 11.248,10 | ✅ EXATO |
| **Pessoa 4** | CARLOS MENEZES / R$ 9.781,67 | CARLOS MENEZES / R$ 9.781,67 | ✅ EXATO |
| **Pessoa 5** | JOSE OSMAN / R$ 9.662,04 | JOSE OSMAN / R$ 9.662,04 | ✅ EXATO |

**Conclusão:** ✅ **PERGUNTA FUNCIONA PERFEITAMENTE**

---

## 🎯 Problemas Identificados no Sistema

### Problema 1: Agregação SUM não funciona
**Severidade:** 🔴 CRÍTICA

- **Affect:** Pergunta 1 (Total de gastos)
- **Root Cause:** Agentes não conseguem construir query com SUM()
- **Evidence:** "não há informações disponíveis"
- **Impact:** Impossível retornar índices agregados

**Solução Proposta:**
```sql
-- Que deveria ser gerado:
SELECT SUM(valor) as total FROM v_financas_geral 
WHERE YEAR(data) = 2024

-- Mas provavelmente está gerando:
SELECT valor FROM v_financas_geral ...  -- sem SUM
```

### Problema 2: Período incorreto na query
**Severidade:** 🔴 CRÍTICA

- **Affect:** Pergunta 2 (Top 5 fornecedores)
- **Root Cause:** Agentes estão filtrando parcial ano de 2024
- **Evidence:** Valores 21.4% menores (consistente com 3-4 meses)
- **Impact:** Dados enganosos para fornecedores

**Solução Proposta:**
- Forçar período completo: 2024-01-01 até 2024-12-31
- Debug do metadata.periodo_start/fim

### Problema 3: Busca fuzzy encontrando registros errados
**Severidade:** 🔴 CRÍTICA

- **Affect:** Pergunta 3 (Energisa)
- **Root Cause:** Fuzzy match pode estar capturando registro diferente
- **Evidence:** Valor 8.8x menor (muito discrepante)
- **Impact:** Dados incorretos para fornecedores específicos

**Solução Proposta:**
- Testar busca de "ENERGISA" no banco
- Validar se fuzzy_match cutoff (60%) é apropriado
- Debug do SQL gerado

### Problema 4: Pergunta 5 funciona, outras não
**Severidade:** 🟡 ANÁLISE NECESSÁRIA

- **Paradoxo:** GROUP BY + ORDER BY + LIMIT funciona (P5)
- **Mas:** SUM agregado não funciona (P1)
- **Indicador:** Problema pode ser no construtor de SUM específico

---

## 🔧 Ações Recomendadas

### 1️⃣ Ativar Logging Detalhado (URGENTE)

Adicionar a `crew_definition_v2.py`:
```python
def execute_with_confidence(...):
    logger.info(f"SQL GERADO: {resultado_sql}")  # Log the SQL
    logger.info(f"PERÍODO ENCONTRADO: {periodo_inicio} a {periodo_fim}")
    logger.info(f"ENTIDADES ENCONTRADAS: {entities}")
```

### 2️⃣ Validar Dados no Banco (URGENTE)

```sql
-- Pergunta 1: Total
SELECT SUM(valor) FROM v_financas_geral 
WHERE YEAR(data) = 2024;  -- Deve retornar: ~336-340M

-- Pergunta 2: Top 5
SELECT favorecido_nome, SUM(valor) as valor_total 
FROM v_financas_geral 
WHERE YEAR(data) = 2024 
GROUP BY favorecido_nome 
ORDER BY valor_total DESC 
LIMIT 5;  -- Deve retornar: BANCO DO BRASIL R$141M, etc

-- Pergunta 3: Energisa
SELECT SUM(valor) FROM v_financas_geral 
WHERE favorecido_nome LIKE '%ENERGISA%' 
AND YEAR(data) = 2024;  -- Deve retornar: R$1.25M (?)

-- Pergunta 4: Campus Propriá Jan
SELECT SUM(valor) FROM v_financas_geral 
WHERE id_ug = (SELECT id_ug FROM ... WHERE nome LIKE '%PROPRIA%')
AND YEAR(data) = 2024 
AND MONTH(data) = 1;  -- Resultado: ? (0 ou valor)

-- Pergunta 5: Diárias (já funciona)
SELECT pessoa_nome, SUM(valor) FROM v_financas_geral 
WHERE id_natureza = (SELECT id FROM ... WHERE nome LIKE '%DIARIAS%')
AND YEAR(data) = 2024 
GROUP BY pessoa_nome 
ORDER BY SUM(valor) DESC 
LIMIT 5;  -- Já retorna correto!
```

### 3️⃣ Debugar Agentes (URGENTE)

Modificar `crew_definition_v2.py` para adicionar:
```python
task_mapping.expected_output = """
Mapeamento de entidades:
- tipo_filtro: (sum / top_n / etc)
- entidades: [...]
- período: [...]
IMPORTANT: Se é um SUM agregado, SEMPRE usar COUNT(*) ou SUM()
"""
```

### 4️⃣ Testar Fix Período (TODO)

Validar que `metadata.period_start` e `period_end` estão sendo usados corretamente:
```python
# Verificar em app_v2.py
print(f"DEBUG: Período detectado: {metadata.period_start} a {metadata.period_end}")
```

### 5️⃣ Validar Fuzzy Matching (TODO)

Testar fuzzy match para "Energisa":
```python
from rapidfuzz import fuzz

favorecidos = [
    "BANCO DO BRASIL SA",
    "ENERGISA SERGIPE - DISTRIBUIDORA...",
    "CAIXA ECONOMICA FEDERAL",
    ...
]

resultado = fuzz.token_set_ratio("Energisa", "ENERGISA SERGIPE - DISTRIBUIDORA...")
# Deve retornar: 95%+ (significa match correto)
```

---

## 📊 Matriz de Diagnóstico

| Pergunta | SQL Type | Status | Provável Culpado | Prioridade |
|----------|----------|--------|------------------|------------|
| 1 - Total | SUM | ❌ FALHA | SQL Architect Agent | 🔴 P0 |
| 2 - Top 5 | GROUP BY + ORDER + LIMIT | ⚠️ PERÍODO | Metadata Navigator Agent | 🔴 P0 |
| 3 - Energisa | WHERE LIKE + SUM | ⚠️ BUSCA | Fuzzy Matching / SQL | 🔴 P0 |
| 4 - Campus + Mês | WHERE + AND + SUM | ⚠️ ? | Precisa debug | 🟡 P1 |
| 5 - Diárias | GROUP BY + ORDER + LIMIT | ✅ OK | --- | ✅ --- |

---

## 🚀 Próximos Passos

1. **Hoje:** Executar queries SQL de validação no banco
2. **Hoje:** Ativar logging em crew_definition_v2.py
3. **Amanhã:** Debug das queries geradas pelos agentes
4. **Amanhã:** Corrigir SQL Architect Agent (SUM issue)
5. **Amanhã:** Corrigir Metadata Navigator Agent (período)
6. **Depois:** Testes de revalidação

---

**Status Geral:** ⚠️ **SISTEMA PARCIALMENTE FUNCIONAL**  
**Recomendação:** Pausar testes de aceitação até fixes serem aplicados  
**Timeline de Correção Estimado:** 4-8 horas de debug + testes

---

*Documento criado em 9 de abril de 2026 - Análise do Teste Manual*
