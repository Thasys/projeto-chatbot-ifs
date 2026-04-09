#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIX 4: Validação de Queries SQL contra o banco de dados

Este script executa as 5 queries de validação esperadas e mostra os resultados.
Útil para diagnosticar se os valores retornados pelo sistema estão corretos.

Uso: python validate_sql_queries.py
"""

import pandas as pd
import sys
import logging
from db_connection import DBConnection
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

print("\n" + "="*70)
print("VALIDAÇÃO DE QUERIES SQL - DIAGNÓSTICO")
print("="*70)
print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70 + "\n")

db = DBConnection()
engine = db.get_engine()


# ==================== PERGUNTA 1: TOTAL DE GASTOS 2024 ====================
print("\n[PERGUNTA 1] Qual o total de gastos do IFS em 2024?")
print("-"*70)

query1 = """
SELECT SUM(valor) as total_gastos
FROM v_financas_geral
WHERE YEAR(data) = 2024;
"""

try:
    df1 = pd.read_sql(query1, engine)
    total = df1['total_gastos'].iloc[0]

    print(f"Query: {query1.strip()}")
    print(f"\nResultado: R$ {total:,.2f}")

    # Validação
    esperado = 339539000  # Aproximadamente
    diferenca_pct = abs((total - esperado) / esperado * 100) if total else 100

    if diferenca_pct < 5:
        status = "✅ OK (within 5%)"
    elif diferenca_pct < 15:
        status = "⚠️ PARCIAL (within 15%)"
    else:
        status = f"❌ ERRADO (diferença: {diferenca_pct:.1f}%)"

    print(f"Esperado: ~R$ {esperado:,.2f}")
    print(f"Status: {status}")

except Exception as e:
    print(f"❌ Erro ao executar query: {e}")

# ==================== PERGUNTA 2: TOP 5 FORNECEDORES 2024 ====================
print("\n\n[PERGUNTA 2] Quais foram os 5 maiores fornecedores do IFS em 2024?")
print("-"*70)

query2 = """
SELECT favorecido_nome, SUM(valor) as valor_total
FROM v_financas_geral
WHERE YEAR(data) = 2024
GROUP BY favorecido_nome
ORDER BY valor_total DESC
LIMIT 5;
"""

try:
    df2 = pd.read_sql(query2, engine)

    print(f"Query: {query2.strip()}")
    print(f"\nResultados:")
    print(df2.to_string(index=False))

    # Validação
    expected_values = {
        'BANCO DO BRASIL SA': 141123000,
        'INST.FED.DE EDUC.,CIENC.E TEC.DE SERGIPE': 118285000,
        'CAIXA ECONOMICA FEDERAL': 103296000,
        'GEAP AUTOGESTAO EM SAUDE': 5782570,
        'BANCO SANTANDER (BRASIL) S.A.': 4867730,
    }

    print(f"\nValidação:")
    for idx, row in df2.iterrows():
        nome = row['favorecido_nome']
        valor = row['valor_total']

        # Procurar match aproximado
        match_found = False
        for expected_name, expected_valor in expected_values.items():
            if expected_name[:20].upper() in nome.upper() or nome.upper() in expected_name.upper():
                match_found = True
                diferenca_pct = abs(
                    (valor - expected_valor) / expected_valor * 100)
                if diferenca_pct < 5:
                    status = "✅"
                elif diferenca_pct < 15:
                    status = "⚠️"
                else:
                    status = "❌"
                print(
                    f"{status} {nome}: R$ {valor:,.2f} (esperado ~R$ {expected_valor:,.2f})")
                break

        if not match_found:
            print(f"❓ {nome}: R$ {valor:,.2f}")

except Exception as e:
    print(f"❌ Erro ao executar query: {e}")

# ==================== PERGUNTA 3: GASTO COM ENERGISA 2024 ====================
print("\n\n[PERGUNTA 3] Quanto o IFS gastou com a Energisa em 2024?")
print("-"*70)

query3 = """
SELECT SUM(valor) as total_energisa,
       favorecido_nome,
       COUNT(*) as num_registros
FROM v_financas_geral
WHERE favorecido_nome LIKE '%ENERGISA%'
AND YEAR(data) = 2024
GROUP BY favorecido_nome;
"""

try:
    df3 = pd.read_sql(query3, engine)

    print(f"Query: {query3.strip()}")
    print(f"\nResultados:")
    print(df3.to_string(index=False))

    if not df3.empty:
        total = df3['total_energisa'].sum()
        print(f"\nTotal gasto com Energisa: R$ {total:,.2f}")

        # Validação
        esperado = 1250430.50
        if total > 0:
            diferenca_pct = abs((total - esperado) / esperado * 100)
            if diferenca_pct < 10:
                status = "✅ Valor plausível"
            else:
                status = f"⚠️ Diferença significativa ({diferenca_pct:.1f}%)"
            print(f"Esperado: ~R$ {esperado:,.2f}")
            print(f"Status: {status}")
    else:
        print("⚠️ Nenhum registro encontrado para 'ENERGISA'")

        # Tentar busca alternativa
        query3_alt = """
        SELECT favorecido_nome, COUNT(*) as num_registros
        FROM v_financas_geral
        WHERE YEAR(data) = 2024
        GROUP BY favorecido_nome
        HAVING favorecido_nome LIKE '%ENER%' OR favorecido_nome LIKE '%DISTRIBUID%'
        LIMIT 5;
        """
        print("\nTentando busca alternativa (%ENER% ou %DISTRIBUID%):")
        df3_alt = pd.read_sql(query3_alt, engine)
        print(df3_alt.to_string(index=False))

except Exception as e:
    print(f"❌ Erro ao executar query: {e}")

# ==================== PERGUNTA 4: CAMPUS PROPRIA JAN 2024 ====================
print("\n\n[PERGUNTA 4] Qual foi o gasto total do Campus de Propriá em janeiro de 2024?")
print("-"*70)

query4 = """
SELECT SUM(valor) as total_propria,
       ug,
       COUNT(*) as num_registros
FROM v_financas_geral
WHERE ug LIKE '%PROPRIA%'
AND YEAR(data) = 2024
AND MONTH(data) = 1
GROUP BY ug;
"""

try:
    df4 = pd.read_sql(query4, engine)

    print(f"Query: {query4.strip()}")
    print(f"\nResultados:")

    if not df4.empty:
        print(df4.to_string(index=False))
        total = df4['total_propria'].sum()
        print(
            f"\nTotal: R$ {total:,.2f}" if total else "Total: R$ 0,00 (sem transações)")
    else:
        print("❌ Nenhum registro encontrado")
        print("\nTentando debug - Cargos em Propriá:")
        debug_query = """
        SELECT DISTINCT ug, COUNT(*) as registros
        FROM v_financas_geral
        WHERE ug LIKE '%PROPRIA%'
        GROUP BY ug;
        """
        df_debug = pd.read_sql(debug_query, engine)
        print(df_debug.to_string(index=False))

except Exception as e:
    print(f"❌ Erro ao executar query: {e}")

# ==================== PERGUNTA 5: MAIORES DIÁRIAS 2024 ====================
print("\n\n[PERGUNTA 5] Quais foram as maiores despesas com diárias em 2024?")
print("-"*70)

query5 = """
SELECT pessoa_nome, SUM(valor) as valor_diarias
FROM v_financas_geral
WHERE id_natureza IN (SELECT id_natureza FROM v_financas_geral WHERE tipo_despesa LIKE '%DIARIA%' GROUP BY id_natureza)
AND YEAR(data) = 2024
GROUP BY pessoa_nome
ORDER BY valor_diarias DESC
LIMIT 5;
"""

try:
    df5 = pd.read_sql(query5, engine)

    print(f"Query (alternativo): {query5.strip()}")
    print(f"\nResultados:")
    print(df5.to_string(index=False))

    # Validação
    if not df5.empty:
        expected_persons = {
            'RUTH SALES GAMA DE ANDRADE': 33225.30,
            'MARCUS ALEXANDRE NORONHA DE BRITO': 21492.70,
            'IDER DE SANTANA SANTOS': 11248.10,
            'CARLOS MENEZES DE SOUZA JUNIOR': 9781.67,
            'JOSE OSMAN DOS SANTOS': 9662.04,
        }

        print(f"\nValidação:")
        for idx, row in df5.iterrows():
            nome = row['pessoa_nome']
            valor = row['valor_diarias']

            match_found = False
            for expected_name, expected_valor in expected_persons.items():
                if expected_name[:20].upper() in nome.upper() or nome.upper() in expected_name.upper():
                    match_found = True
                    diferenca_pct = abs(
                        (valor - expected_valor) / expected_valor * 100)
                    if diferenca_pct < 1:
                        status = "✅"
                    elif diferenca_pct < 5:
                        status = "⚠️"
                    else:
                        status = "❌"
                    print(
                        f"{status} {nome}: R$ {valor:,.2f} (esperado R$ {expected_valor:,.2f})")
                    break

            if not match_found:
                print(f"❓ {nome}: R$ {valor:,.2f}")
    else:
        print("⚠️ Nenhum registro encontrado para diárias")

except Exception as e:
    print(f"❌ Erro ao executar query: {e}")

# ==================== RESUMO ====================
print("\n" + "="*70)
print("RESUMO DA VALIDAÇÃO")
print("="*70)
print("""
Se você vir principalmente ✅ (green), o banco de dados está correto e
os agentes precisam ser corrigidos.

Se você vir principalmente ❌ (red) ou ⚠️ (yellow), o banco de dados
pode ter dados diferentes do esperado.

Próximo passo: Verificar logs em debug_chatbot.log para ver qual SQL
os agentes estão gerando.
""")
print("="*70 + "\n")
