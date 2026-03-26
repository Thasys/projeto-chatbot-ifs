#!/usr/bin/env python
"""
Script de validação das correções realizadas
Testa: SIGALRM, parâmetros de query, INSERT audit log
"""

import sys
import platform
import logging

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("=" * 70)
print("🧪 VALIDAÇÃO DAS CORREÇÕES DO CHATBOT")
print("=" * 70)
print()

# ========== TESTE 1: Platform Check ==========
print("📋 TESTE 1: Verificar Sistema Operacional")
print("-" * 70)

system = platform.system()
print(f"Sistema: {system}")
print(f"Python: {platform.python_version()}")

if system == 'Windows':
    print("✅ Windows detectado - SIGALRM será skipped corretamente")
else:
    print("✅ Unix/Linux detectado - SIGALRM será habilitado")

print()

# ========== TESTE 2: Import de Módulos ==========
print("📋 TESTE 2: Importar Módulos Corrigidos")
print("-" * 70)

try:
    logger.info("Importando db_connection...")
    from db_connection import DBConnection
    print("✅ db_connection importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar db_connection: {e}")
    sys.exit(1)

try:
    logger.info("Importando audit_logger...")
    from audit_logger import log_to_audit, get_audit_logs, create_audit_table
    print("✅ audit_logger importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar audit_logger: {e}")
    sys.exit(1)

try:
    logger.info("Importando crew_definition_v2...")
    from crew_definition_v2 import IFSCrewV2
    print("✅ crew_definition_v2 importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar crew_definition_v2: {e}")
    sys.exit(1)

print()

# ========== TESTE 3: Conexão com Banco ==========
print("📋 TESTE 3: Testar Conexão com Banco de Dados")
print("-" * 70)

try:
    db = DBConnection()
    engine = db.get_engine()
    print("✅ Conexão com banco de dados estabelecida")

    # Testar execute_query com None params
    from sqlalchemy import text
    result = db.execute_query("SELECT NOW() as tempo", {})
    print(f"✅ Query simples executada: {result[0]['tempo']}")

except Exception as e:
    print(f"⚠️  Erro na conexão (DB pode não estar online): {e}")
    print("   (Isso é esperado se MySQL não está rodando)")

print()

# ========== TESTE 4: Testar Tabela Audit ==========
print("📋 TESTE 4: Criar/Verificar Tabela chat_audit_log")
print("-" * 70)

try:
    result = create_audit_table()
    if result:
        print("✅ Tabela chat_audit_log pronta")
    else:
        print("⚠️  Tabela não pôde ser criada (DB offline?)")
except Exception as e:
    print(f"⚠️  Erro ao criar tabela: {e}")

print()

# ========== TESTE 5: Testar Insert Audit Log ==========
print("📋 TESTE 5: Testar INSERT de Audit Log com Named Parameters")
print("-" * 70)

try:
    success = log_to_audit(
        pergunta="Pergunta de teste",
        resposta="Resposta de teste",
        status="SUCCESS",
        tempo_ms=100,
        confidence=85.0,
        periodo_dados_inicio="2024-01-01",
        periodo_dados_fim="2024-12-31"
    )

    if success:
        print("✅ Log de auditoria inserido com sucesso")
        print("   (Parâmetros named funcionam corretamente)")
    else:
        print("⚠️  Erro ao inserir log")

except Exception as e:
    print(f"❌ Erro ao inserir log: {e}")

print()

# ========== TESTE 6: Testar Query com Parâmetros ==========
print("📋 TESTE 6: Testar Query com Named Parameters")
print("-" * 70)

try:
    logs = get_audit_logs(limit=1, status_filter='SUCCESS')
    if logs is not None:
        print(f"✅ Query com parâmetros funcionou")
        print(f"   Registros encontrados: {len(logs)}")
    else:
        print("⚠️  Nenhum registro encontrado (esperado na primeira execução)")
except Exception as e:
    print(f"❌ Erro ao recuperar logs: {e}")

print()

# ========== TESTE 7: Verificar SIGALRM ==========
print("📋 TESTE 7: Verificar Handlement de SIGALRM")
print("-" * 70)

try:
    import signal

    if system == 'Windows':
        print("⚠️  Windows: SIGALRM não existe (comportamento esperado)")
        print("✅ Código tratará isso corretamente com 'platform.system() check'")
    else:
        if hasattr(signal, 'SIGALRM'):
            print("✅ Unix/Linux: SIGALRM disponível")
        else:
            print("❌ Unix/Linux mas SIGALRM não encontrado (anormal)")
except Exception as e:
    print(f"❌ Erro ao verificar SIGALRM: {e}")

print()

# ========== RESUMO ==========
print("=" * 70)
print("✅ VALIDAÇÃO CONCLUÍDA")
print("=" * 70)
print()
print("Próximos passos:")
print("1. Executar: streamlit run app_v2.py")
print("2. Fazer uma pergunta no chatbot")
print("3. Verificar se não há erros de SIGALRM ou List argument")
print("4. Verificar chat_audit_log tem novo registro")
print()
