#!/usr/bin/env python3
"""
Script para renomear banco de dados no Railway
Executa: ALTER DATABASE railway RENAME TO dw_ifs_gastos;
"""

import mysql.connector
import sys

# Credenciais do Railway MySQL (PÚBLICAS - para acessar de fora)
# IMPORTANTE: Use RAILWAY_TCP_PROXY_DOMAIN e RAILWAY_TCP_PROXY_PORT (não mysql.railway.internal!)
config = {
    'host': 'metro.proxy.rlwy.net',  # RAILWAY_TCP_PROXY_DOMAIN
    'port': 12752,  # RAILWAY_TCP_PROXY_PORT
    'user': 'root',
    'password': 'nNuyrJXmgQJOAOQkPVZnkrrZpWwvvEyL',
    'database': 'railway'
}


def main():
    print("=" * 60)
    print("Script de Renomeação de Banco de Dados")
    print("=" * 60)
    print()

    # 1. Conectar ao MySQL
    print("1. Conectando ao MySQL Railway...")
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        print("   ✅ Conectado com sucesso!")
    except mysql.connector.Error as err:
        print(f"   ❌ Erro ao conectar: {err}")
        print()
        print("   Possíveis causas:")
        print("   - Host incorreto (não é 'mysql.railway.internal')")
        print("   - Senha errada")
        print("   - Porta diferente de 3306")
        print("   - Firewall bloqueando conexão")
        sys.exit(1)

    # 2. Verificar banco atual
    print()
    print("2. Verificando banco de dados existentes...")
    cursor.execute("SHOW DATABASES;")
    databases = cursor.fetchall()
    print(f"   Bancos encontrados: {[db[0] for db in databases]}")

    # 3. Verificar se 'railway' existe
    if not any(db[0] == 'railway' for db in databases):
        print()
        print("   ❌ ERRO: Banco 'railway' não encontrado!")
        print("   Abortando renomeação.")
        cursor.close()
        conn.close()
        sys.exit(1)

    # 4. Verificar se 'dw_ifs_gastos' já existe
    if any(db[0] == 'dw_ifs_gastos' for db in databases):
        print()
        print("   ⚠️  AVISO: Banco 'dw_ifs_gastos' já existe!")
        print("   Pulando renomeação (banco já tem o nome correto)")
        cursor.close()
        conn.close()
        sys.exit(0)

    # 5. Executar renomeação
    print()
    print("3. Renomeando 'railway' → 'dw_ifs_gastos'...")
    try:
        # Tentar ALTER SCHEMA (MySQL 8.0+)
        cursor.execute("ALTER SCHEMA railway RENAME TO dw_ifs_gastos;")
        conn.commit()
        print("   ✅ Banco renomeado com sucesso!")
    except mysql.connector.Error as err:
        print(f"   ❌ Erro na renomeação: {err}")
        conn.rollback()
        cursor.close()
        conn.close()
        sys.exit(1)

    # 6. Verificar novo nome
    print()
    print("4. Verificando novo nome...")
    cursor.execute("SHOW DATABASES;")
    databases = cursor.fetchall()
    db_names = [db[0] for db in databases]
    print(f"   Bancos agora: {db_names}")

    if 'dw_ifs_gastos' in db_names:
        print("   ✅ Verificação OK!")
    else:
        print("   ❌ Algo deu errado na renomeação")

    # 7. Fechar conexão
    print()
    cursor.close()
    conn.close()

    print("=" * 60)
    print("✅ CONCLUSÃO: Banco de dados renomeado com sucesso!")
    print("=" * 60)
    print()
    print("Próximos passos:")
    print("1. Verifique se o app em Railway está usando DB_NAME='dw_ifs_gastos'")
    print("2. Ou atualize a variável no Railway para usar 'dw_ifs_gastos'")


if __name__ == '__main__':
    main()
