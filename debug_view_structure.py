#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug: Explorar estrutura da view v_financas_geral

Este script mostra quais colunas existem na view e alguns dados amostrais.
"""

import pandas as pd
import sys
import logging
from db_connection import DBConnection

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

print("\n" + "="*70)
print("EXPLORAÇÃO DA VIEW v_financas_geral")
print("="*70 + "\n")

db = DBConnection()
engine = db.get_engine()


# ==== PASSO 1: Ver estrutura ====
print("[1] COLUNAS DISPONÍVEIS:")
print("-"*70)

try:
    # Pega estrutura via DESCRIBE
    df_info = pd.read_sql("DESC v_financas_geral", engine)
    print(df_info[['Field', 'Type', 'Null']].to_string(index=False))
except Exception as e:
    print(f"❌ Erro em DESCRIBE: {e}")
    print("\nTentando via INFORMATION_SCHEMA:")
    try:
        df_info = pd.read_sql("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'v_financas_geral'
            AND TABLE_SCHEMA = 'ifs_db'
        """, engine)
        print(df_info.to_string(index=False))
    except Exception as e2:
        print(f"❌ Erro: {e2}")

# ==== PASSO 2: Primeiras linhas ====
print("\n\n[2] PRIMEIRAS 5 LINHAS:")
print("-"*70)

try:
    df_sample = pd.read_sql("SELECT * FROM v_financas_geral LIMIT 5", engine)
    print(df_sample.to_string())
except Exception as e:
    print(f"❌ Erro: {e}")

# ==== PASSO 3: Contagem de registros ====
print("\n\n[3] ESTATÍSTICAS:")
print("-"*70)

try:
    df_count = pd.read_sql(
        "SELECT COUNT(*) as total_registros FROM v_financas_geral", engine)
    print(f"Total de registros: {df_count.iloc[0]['total_registros']:,}")
except Exception as e:
    print(f"❌ Erro: {e}")

# ==== PASSO 4: Valores únicos em colunas-chave ====
print("\n\n[4] VALORES ÚNICOS (Amostra):")
print("-"*70)

try:
    # Tenta descobrir colunas existentes
    df_cols = pd.read_sql("SELECT * FROM v_financas_geral LIMIT 1", engine)
    cols = df_cols.columns.tolist()

    for col in cols[:10]:  # Primeiras 10 colunas
        try:
            unique_count = pd.read_sql(
                f"SELECT COUNT(DISTINCT {col}) as cnt FROM v_financas_geral", engine)
            count = unique_count.iloc[0]['cnt']
            print(f"  {col}: {count} valores únicos")
        except:
            pass

except Exception as e:
    print(f"❌ Erro: {e}")

# ==== PASSO 5: Dados 2024 ====
print("\n\n[5] REGISTROS 2024:")
print("-"*70)

try:
    df_2024 = pd.read_sql("""
        SELECT COUNT(*) as registros_2024,
               MIN(data) as data_minima,
               MAX(data) as data_maxima,
               SUM(valor) as total_valor
        FROM v_financas_geral
        WHERE YEAR(data) = 2024
    """, engine)
    print(df_2024.to_string(index=False))
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n" + "="*70 + "\n")
