#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Avançado: Investigar dados reais em v_financas_geral

Checklist:
1. Verificar quais unidade_pagadora existem (para Propriá)
2. Verificar padrão de diárias
3. Verificar se valores negativos estão inclusos
4. Comparar total com expected
"""

import pandas as pd
from db_connection import DBConnection

db = DBConnection()
engine = db.get_engine()

print("="*70)
print("DEBUG AVANÇADO - v_financas_geral")
print("="*70 + "\n")

# ======== 1. Unidades Pagadoras (substituir "ug") ========
print("[1] UNIDADES PAGADORAS - CAMPUS PROPRIÁ:")
print("-"*70)

query = """
SELECT DISTINCT unidade_pagadora
FROM v_financas_geral
WHERE unidade_pagadora LIKE '%PROPRIA%'
OR unidade_pagadora LIKE '%PROPRIO%'
OR unidade_pagadora LIKE '%PROPRIETARY%';
"""

try:
    df = pd.read_sql(query, engine)
    if not df.empty:
        print("Encontrado:")
        print(df.to_string(index=False))
    else:
        print("❌ Nenhuma unidade com 'PROPRIA'")
        print("\nTodas as unidades:")
        df_all = pd.read_sql(
            "SELECT DISTINCT unidade_pagadora FROM v_financas_geral", engine)
        print(df_all.to_string(index=False))
except Exception as e:
    print(f"❌ Erro: {e}")

# ======== 2. Padrão de Diárias ========
print("\n\n[2] PADRÃO DE DIÁRIAS:")
print("-"*70)

query = """
SELECT tipo_despesa, COUNT(*) as registros, SUM(valor) as total
FROM v_financas_geral
WHERE LOWER(tipo_despesa) LIKE '%diaria%'
AND YEAR(data) = 2024
GROUP BY tipo_despesa;
"""

try:
    df = pd.read_sql(query, engine)
    if not df.empty:
        print(f"Encontrado {len(df)} tipo(s) de diárias:")
        print(df.to_string(index=False))
    else:
        print("❌ Nenhum tipo_despesa contendo 'diaria'")
except Exception as e:
    print(f"❌ Erro: {e}")

# ======== 3. Verificar valores negativos ========
print("\n\n[3] ANÁLISE DE VALORES NEGATIVOS:")
print("-"*70)

query = """
SELECT 
    COUNT(*) as total_registros,
    SUM(valor) as total_com_negativos,
    SUM(ABS(valor)) as total_valor_absoluto,
    SUM(CASE WHEN valor > 0 THEN valor ELSE 0 END) as total_positivos,
    SUM(CASE WHEN valor < 0 THEN valor ELSE 0 END) as total_negativos,
    COUNT(CASE WHEN valor < 0 THEN 1 END) as count_negativos
FROM v_financas_geral
WHERE YEAR(data) = 2024;
"""

try:
    df = pd.read_sql(query, engine)
    print(df.to_string(index=False))

    # Análise
    row = df.iloc[0]
    print(f"\nAnálise:")
    print(f"  Total com negativos: R$ {row['total_com_negativos']:,.2f}")
    print(f"  Total valor absoluto: R$ {row['total_valor_absoluto']:,.2f}")
    print(
        f"  Resgistros negativos: {row['count_negativos']} de {row['total_registros']}")

except Exception as e:
    print(f"❌ Erro: {e}")

# ======== 4. Comparar Top 5 com histórico ========
print("\n\n[4] TOP 5 FORNECEDORES - Ajustado (sem débitos):")
print("-"*70)

query = """
SELECT favorecido_nome, 
       SUM(valor) as total_liquido,
       SUM(ABS(valor)) as total_absoluto,
       COUNT(*) as registros
FROM v_financas_geral
WHERE YEAR(data) = 2024
AND valor >= 0
GROUP BY favorecido_nome
ORDER BY SUM(valor) DESC
LIMIT 5;
"""

try:
    df = pd.read_sql(query, engine)
    print(df.to_string(index=False))
except Exception as e:
    print(f"❌ Erro: {e}")

# ======== 5. Buscar "RUTH SALES" (diárias) ========
print("\n\n[5] BUSCA POR DIÁRIAS - Padrão Histórico:")
print("-"*70)

query = """
SELECT historico_detalhado, COUNT(*) as registros, SUM(valor) as total
FROM v_financas_geral
WHERE YEAR(data) = 2024
AND historico_detalhado LIKE '%RUTH%' OR historico_detalhado LIKE '%DIARIA%'
GROUP BY historico_detalhado
LIMIT 5;
"""

try:
    df = pd.read_sql(query, engine)
    if not df.empty:
        print(f"Encontrados {len(df)} padrões:")
        for col in df.columns:
            print(f"\n{col}:")
            for val in df[col].head(3):
                print(f"  {str(val)[:80]}...")
    else:
        print("❌ Nenhum histórico com 'RUTH' ou 'DIARIA'")
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n" + "="*70 + "\n")
