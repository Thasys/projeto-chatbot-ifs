from db_connection import DBConnection
from sqlalchemy import inspect, text
import sys
import os
from pathlib import Path

# ========== SOLUÇÃO: Adicionar diretório pai ao PYTHONPATH ==========
# Isso permite que o script encontre db_connection.py independente de onde é executado
sys.path.insert(0, str(Path(__file__).parent.parent))


print("=" * 80)
print("🧪 TESTE DE CONEXÃO COM BANCO DE DADOS")
print("=" * 80)

try:
    print("\n✅ Passo 1: Criando conexão...")
    db = DBConnection()
    engine = db.get_engine()
    print("   ✅ Conexão estabelecida com sucesso!")

    print("\n✅ Passo 2: Verificando tabelas...")
    inspector = inspect(engine)
    tabelas = inspector.get_table_names()
    print(f"   ✅ Tabelas encontradas ({len(tabelas)}):")
    for tabela in tabelas:
        print(f"      - {tabela}")

    if not tabelas:
        print("      ⚠️ AVISO: Nenhuma tabela encontrada!")
        print("      Execute 'python setup_views.py' para criar as tabelas.")

    print("\n✅ Passo 3: Contando registros...")
    with engine.connect() as conn:
        # IMPORTANTE: usar text() para wrappear SQL strings
        tabelas_para_contar = ['dim_ug', 'dim_favorecido',
                               'dim_programa', 'dim_natureza', 'fato_execucao']

        for tabela in tabelas_para_contar:
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {tabela}"))
                count = result.fetchone()[0]
                print(f"      ✅ {tabela}: {count} registros")
            except Exception as e:
                erro_msg = str(e)
                if "doesn't exist" in erro_msg or "no such table" in erro_msg:
                    print(f"      ❌ {tabela}: Tabela não existe")
                else:
                    print(f"      ❌ {tabela}: Erro ({erro_msg[:50]})")

    print("\n" + "=" * 80)
    print("🎉 TESTE PASSOU! Sistema pronto para uso.")
    print("=" * 80)

except ModuleNotFoundError as e:
    print(f"\n❌ ERRO: Módulo não encontrado - {e}")
    print("\n🔧 Solução:")
    print("   Verifique se os arquivos estão no lugar certo:")
    print("   - db_connection.py deve estar na raiz do projeto")
    print("   - config.py deve estar em etl_scripts/")

except ConnectionError as e:
    print(f"\n❌ ERRO: Não foi possível conectar ao MySQL - {e}")
    print("\n🔧 Soluções possíveis:")
    print("   1. Verifique se MySQL está rodando")
    print("   2. Verifique as credenciais no arquivo .env:")
    print("      - DB_HOST")
    print("      - DB_USER")
    print("      - DB_PASS")
    print("      - DB_PORT")
    print("      - DB_NAME")

except Exception as e:
    print(f"\n❌ ERRO GERAL: {e}")
    print("\n🔧 Possíveis soluções:")
    print("   1. Verifique se MySQL está rodando")
    print("   2. Verifique credenciais no arquivo .env")
    print("   3. Verifique se o banco de dados existe")
    print("   4. Verifique se as tabelas existem")
    print(f"\n📋 Detalhes técnicos: {type(e).__name__}")
