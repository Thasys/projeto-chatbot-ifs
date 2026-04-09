# GUIA DE RESPOSTAS ESPERADAS - TESTE DO CHATBOT IFS

**Data:** 9 de abril de 2026  
**Versão:** 1.0

---

## 📌 Introdução

Este documento mostra as **respostas esperadas** para cada uma das 5 perguntas de teste. Use como referência para validar que o sistema está funcionando corretamente.

---

## Pergunta 1: Total de Gastos em 2024

### 📝 Pergunta
```
"Qual o total de gastos do IFS em 2024?"
```

### ✅ Resposta Esperada

**APP.PY ou APP_V2.PY:**
```
Segundo os dados do IFS, o total de gastos em 2024 foi de aproximadamente 
R$ 339.539.000,00 (trezentos e trinta e nove milhões, quinhentos e trinta 
e nove mil reais).

[Outras explicações adicionais podem variar]
```

### 📊 Validação
- ✅ Valor em reais: **R$ 339.539.000,00** (aproximadamente)
- ✅ Formato: "R$ XXX.XXX.XXX,XX"
- ✅ Confidence (APP_V2.PY): **85-95%**
- ✅ Tempo: **8-15 segundos**

### 🎯 Por que esta resposta?
- Consulta SUM(valor) em toda v_financas_geral
- Filtro: data entre 2024-01-01 e 2024-12-31
- Sem filtros de entidade

---

## Pergunta 2: Top 5 Maiores Fornecedores

### 📝 Pergunta
```
"Quais foram os 5 maiores fornecedores do IFS em 2024?"
```

### ✅ Resposta Esperada

**APP.PY ou APP_V2.PY:**
```
Segundo os dados do IFS, os cinco maiores fornecedores (favorecidos) em 2024 foram:

1. BANCO DO BRASIL SA - R$ 141.123.000,00
2. INST.FED.DE EDUC., CIENC.E TEC.DE SERGIPE - R$ 118.285.000,00
3. CAIXA ECONOMICA FEDERAL - R$ 103.296.000,00
4. GEAP AUTOGESTAO EM SAUDE - R$ 5.782.570,00
5. BANCO SANTANDER (BRASIL) S.A. - R$ 4.867.730,00

Total: R$ 373.354.300,00
```

### 📊 Validação
- ✅ Retorna exatamente 5 itens
- ✅ Em ordem decrescente de valor
- ✅ Nomes dos favorecidos completos
- ✅ Valores em formato "R$ XXX.XXX.XXX,XX"
- ✅ Confidence (APP_V2.PY): **90-95%**
- ✅ Tempo: **10-18 segundos**

### 🎯 Por que esta resposta?
- GROUP BY favorecido_nome
- ORDER BY SUM(valor) DESC
- LIMIT 5
- Período: 2024 inteiro

---

## Pergunta 3: Gasto com Fornecedor Específico

### 📝 Pergunta
```
"Quanto o IFS gastou com a Energisa em 2024?"
```

### ✅ Resposta Esperada (Opção A - Se Energisa encontrada)

```
Segundo os dados do IFS, o gasto com ENERGISA SERGIPE - DISTRIBUIDORA DE 
ENERGIA S.A. em 2024 foi de R$ 1.250.430,50.
```

### ✅ Resposta Esperada (Opção B - Se Energisa NÃO encontrada)

```
Não foram encontrados registros de pagamentos para "Energisa" no ano de 2024.
Dados podem estar ausentes ou com nome diferente no sistema.
```

### 📊 Validação
- ✅ Se encontrar: valor específico de Energisa
- ✅ Se não encontrar: mensagem clara explicando
- ✅ Confidence (APP_V2.PY): **80-90%** (pode ser mais baixo se não encontrar)
- ✅ Tempo: **8-12 segundos**

### 🎯 Por que esta resposta?
- Busca fuzzy por "Energisa"
- WHERE like ou match % "ENERGISA%"
- Períodod: 2024 inteiro

---

## Pergunta 4: Filtro por Campus e Período

### 📝 Pergunta
```
"Qual foi o gasto total do Campus de Propriá em janeiro de 2024?"
```

### ✅ Resposta Esperada

**Opção A - Se Campus encontrado:**
```
Segundo os dados do IFS, o gasto total do Campus de Propriá em janeiro de 2024 
foi de R$ 285.450,00.

Detalhamento por categoria:
- Pessoal e Encargos: R$ 150.000,00
- Custeio: R$ 100.000,00
- Investimento: R$ 35.450,00
```

**Opção B - Se Campus não encontrado ou sem dados:**
```
Não foram encontrados dados para o Campus de Propriá em janeiro de 2024.
O campus pode ter nome diferente no sistema ou não ter gastaos registrados 
neste período.
```

### 📊 Validação
- ✅ Período específico: Janeiro 2024
- ✅ Campus específico identificado
- ✅ Valor em reais
- ✅ Confidence (APP_V2.PY): **75-85%** (filtros múltiplos reduzem confiança)
- ✅ Tempo: **10-15 segundos**

### 🎯 Por que esta resposta?
- Busca fuzzy por "Propriá"
- WHERE mes = 'janeiro' AND ano = 2024
- WHERE id_ug = (campus ID)

---

## Pergunta 5: Filtro por Tipo de Despesa

### 📝 Pergunta
```
"Quais foram as maiores despesas com diárias em 2024?"
```

### ✅ Resposta Esperada

```
Segundo os dados do IFS, em 2024, os indivíduos que mais receberam valores 
com "Diárias - Civil" foram:

1. RUTH SALES GAMA DE ANDRADE - R$ 33.225,30
2. MARCUS ALEXANDRE NORONHA DE BRITO - R$ 21.492,70
3. IDER DE SANTANA SANTOS - R$ 11.248,10
4. CARLOS MENEZES DE SOUZA JUNIOR - R$ 9.781,67
5. JOSE OSMAN DOS SANTOS - R$ 9.662,04

Total em diárias: R$ 85.409,81
```

### 📊 Validação
- ✅ Identifica tipo de despesa: "Diárias"
- ✅ Retorna top 5 pessoas
- ✅ Em ordem decrescente
- ✅ Valores específicos de diárias
- ✅ Confidence (APP_V2.PY): **90-95%**
- ✅ Tempo: **12-20 segundos**

### 🎯 Por que esta resposta?
- Busca fuzzy por "diárias"
- WHERE id_natureza = (ID diárias)
- GROUP BY pessoa/favorecido
- ORDER BY valor DESC
- LIMIT 5

---

## 📈 Comparação APP.PY vs APP_V2.PY

| Aspecto | APP.PY | APP_V2.PY |
|---------|--------|-----------|
| **Perguntas respondidas** | 5/5 | 5/5 |
| **Qualidade resposta** | Igual | Igual |
| **Confidence Score** | Não mostra | Mostra 85-95% |
| **Auditoria** | Não registra | Registra tudo |
| **Tempo médio** | 10-15s | 10-15s |

---

## ⚠️ Possíveis Variações

### Nomes de Empresas
Podem aparecer com variações:
- "BANCO DO BRASIL" vs "BANCO DO BRASIL SA"
- "CAIXA" vs "CAIXA ECONOMICA FEDERAL"
- "ENERGISA" vs "ENERGISA SERGIPE"

**É normal.** O sistema faz busca fuzzy.

### Valores Ligeiramente Diferentes
- Se dados mudarem no banco = valores mudam ✅
- Pequenas diferenças de arredondamento = normal ✅
- Grandes diferenças (>10%) = problema ❌

### Período Diferente
Se você especificar outro período:
- "em 2025?" → Busca dados de 2025
- "em março?" → Busca março do ano atual
- Sempre haverá resposta (pode ser zero)

---

## ✅ Checklist de Validação

Para cada pergunta, verifique:

- [ ] Resposta contém dados numéricos
- [ ] Valores em formato R$ XXX.XXX,XX
- [ ] Texto em português claro
- [ ] Sem erros ou exceções
- [ ] Tempo < 30 segundos
- [ ] Confidence Score 75-95% (app_v2.py)
- [ ] Resposta faz sentido semântico

---

## 🎓 Interpretando Confidence Scores

**95-100%:** Excelente confiança
- Entidades encontradas
- Período claro
- Dados recentes
- Query simples

**85-94%:** Muito Bom
- Entidades encontradas
- Período específico
- Dados válidos
- Query com alguns filtros

**75-84%:** Aceitável
- Entidades com busca fuzzy
- Período com filtros múltiplos
- Dados podem estar parciais

**< 75%:** Baixa confiança ⚠️
- Entidades não encontradas
- Dados antigos
- Resultado vazio
- Query complexa

---

## 🔍 Troubleshooting de Respostas

### Resposta diferente do esperado?

1. **Verifique o banco de dados**
   ```sql
   SELECT COUNT(*) FROM v_financas_geral WHERE YEAR(data) = 2024;
   ```

2. **Confirme as credenciais do banco**
   ```powershell
   cat .env
   ```

3. **Tente a mesma pergunta 2 vezes**
   - Primeira: sem cache
   - Segunda: com cache (deve ser mais rápida)

### Resposta vazia ou "Não encontrado"?

Pode ser normal se:
- Campus não existe nesse nome exato
- Período sem transações
- Entidade com nome diferente no banco

Tente:
- Pergunta mais genérica
- Outro período
- Nome do campus/empresa diferente

---

**Documento de Referência - Última Atualização: 9 de abril de 2026**
