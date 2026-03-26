#!/usr/bin/env python
"""
🧪 SCRIPT DE DIAGNÓSTICO DETALHADO
Testa cada etapa do pipeline separadamente
"""

import time
import signal
import platform
import sys
import logging
from datetime import datetime

# ========== SUPER LOGGING ==========
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('debug_chatbot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

print("=" * 80)
print("🧪 DIAGNÓSTICO COMPLETO DO PIPELINE CHATBOT")
print("=" * 80)
print()

# ========== TESTE 1: Signal Handling ==========
print("📋 TESTE 1: Signal Alarm Handling")
print("-" * 80)


system = platform.system()
print(f"Sistema: {system}")

if system != 'Windows':
    print("✅ Unix/Linux detectado - SIGALRM será testado")

    try:
        def test_handler(signum, frame):
            raise TimeoutError("Teste de alarme")

        signal.signal(signal.SIGALRM, test_handler)
        signal.alarm(5)

        print("  ⏰ Alarme iniciado por 5s")
        time.sleep(2)

        signal.alarm(0)  # Cancel
        print("  ✅ Alarme cancelado com sucesso")

    except Exception as e:
        print(f"  ❌ Erro no teste: {e}")
else:
    print("⚠️  Windows detectado - SIGALRM será skipped (comportamento esperado)")

print()

# ========== TESTE 2: Importações ==========
print("📋 TESTE 2: Importar Módulos Principais")
print("-" * 80)

try:
    logger.info("Importando db_connection...")
    from db_connection import DBConnection
    print("✅ db_connection OK")
except Exception as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)

try:
    logger.info("Importando tools...")
    from tools import search_entity_fuzzy, execute_sql
    print("✅ tools OK")
except Exception as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)

try:
    logger.info("Importando crew_definition_v2...")
    from crew_definition_v2 import IFSCrewV2, calculate_confidence
    print("✅ crew_definition_v2 OK")
except Exception as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)

try:
    logger.info("Importando audit_logger...")
    from audit_logger import log_to_audit, create_audit_table
    print("✅ audit_logger OK")
except Exception as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)

print()

# ========== TESTE 3: Database ==========
print("📋 TESTE 3: Conexão com Banco de Dados")
print("-" * 80)

try:
    db = DBConnection()
    engine = db.get_engine()
    print("✅ Conexão com BD estabelecida")

    # Testar query simples
    from sqlalchemy import text
    result = db.execute_query("SELECT NOW() as tempo", {})
    print(f"✅ Query simples OK: {result[0]['tempo']}")

except Exception as e:
    print(f"❌ Erro: {e}")
    print("⚠️  BD offline? Continuando com outros testes...")

print()

# ========== TESTE 4: Search Entity ==========
print("📋 TESTE 4: Search Entity Fuzzy")
print("-" * 80)

try:
    logger.info("Testando search_entity_fuzzy...")
    resultado = search_entity_fuzzy("Energisa")
    print(f"✅ Busca de entidade funcionou")
    print(f"   Resultado: {resultado[:100]}...")
except Exception as e:
    print(f"❌ Erro: {e}")
    logger.exception("Erro detalhado:")

print()

# ========== TESTE 5: Confidence Calculation ==========
print("📋 TESTE 5: Calculate Confidence")
print("-" * 80)

try:
    confidence = calculate_confidence(
        has_entities=True,
        entities_count=1,
        has_results=True,
        data_is_recent=True,
        fuzzy_match=False,
        query_type="total"
    )
    print(f"✅ Confiança calculada: {confidence}%")
except Exception as e:
    print(f"❌ Erro: {e}")

print()

# ========== TESTE 6: Full Crew Testing ==========
print("📋 TESTE 6: Full Crew Pipeline")
print("-" * 80)

try:
    logger.info("Inicializando IFSCrewV2...")
    crew_manager = IFSCrewV2(use_json_mode=True, cache_ttl=300)
    print("✅ Crew manager inicializado")

    # Criar crew para pergunta simples
    user_question = "Qual é o total de gastos do IFS em 2024?"
    logger.info(f"Pergunta: {user_question}")

    crew_instance = crew_manager.get_crew(user_question)
    print(f"✅ Crew criado com 3 agentes e 3 tasks")

    # Testar execute_with_confidence
    logger.info("Iniciando execute_with_confidence...")
    result = crew_manager.execute_with_confidence(
        crew_instance, user_question, timeout=30)

    print(f"✅ Resposta recebida")
    print(
        f"   - Status: {'SUCCESS' if result['resposta'] and not result['resposta'].startswith('❌') else 'ERROR'}")
    print(f"   - Confiança: {result['confidence']}%")
    print(
        f"   - Período: {result['periodo_inicio']} a {result['periodo_fim']}")
    print(
        f"   - Resposta (primeiras 100 chars): {result['resposta'][:100]}...")

except Exception as e:
    logger.error(f"❌ Erro no crew: {e}")
    logger.exception("Stack trace completo:")
    print(f"❌ Erro: {e}")

print()

# ========== TESTE 7: Audit Log ==========
print("📋 TESTE 7: Audit Logging")
print("-" * 80)

try:
    logger.info("Testando audit log...")
    success = log_to_audit(
        pergunta="Pergunta teste",
        resposta="Resposta teste",
        status="SUCCESS",
        tempo_ms=100,
        confidence=85.0,
        periodo_dados_inicio="2024-01-01",
        periodo_dados_fim="2024-12-31"
    )

    if success:
        print("✅ Audit log inserido com sucesso")
    else:
        print("⚠️  Audit log retornou False")

except Exception as e:
    logger.error(f"❌ Erro ao inserir audit log: {e}")
    print(f"❌ Erro: {e}")

print()

# ========== RESUMO ==========
print("=" * 80)
print("✅ DIAGNÓSTICO CONCLUÍDO")
print("=" * 80)
print()
print("📝 Log completo salvo em: debug_chatbot.log")
print()
print("Próximos passos:")
print("1. Verificar debug_chatbot.log para detalhes de erros")
print("2. Se tudo verde: Executar streamlit run app_v2.py")
print("3. Fazer pergunta teste: 'Qual o total de gastos do IFS em 2024?'")
print("4. Procurar por stack traces nos logs")
print()
