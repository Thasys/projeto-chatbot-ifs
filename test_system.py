#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste do sistema chatbot após correção de decorador duplicado.
Testa a pergunta: "Qual o total de gastos do IFS em 2024?"
"""

import sys
import os
import traceback
from datetime import datetime

# Forçar UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("\n" + "="*70)
print("[TESTE] SISTEMA CHATBOT IFS - Validacao apos Correcao")
print("="*70)

# ========== TESTE 1: Importações ==========
print("\n[TESTE 1] Validando Importacoes...")
try:
    from tools import search_entity_fuzzy, search_sql_memory, execute_sql, export_csv
    print("   [OK] tools.py importado corretamente")
except Exception as e:
    print(f"   [ERRO] Erro ao importar tools: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from crew_definition import IFSCrew
    print("   [OK] IFSCrew importado corretamente")
except Exception as e:
    print(f"   [ERRO] Erro ao importar IFSCrew: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from crew_definition_v2 import IFSCrewV2
    print("   [OK] IFSCrewV2 importado corretamente")
except Exception as e:
    print(f"   [ERRO] Erro ao importar IFSCrewV2: {e}")
    traceback.print_exc()
    sys.exit(1)

# ========== TESTE 2: Instanciação do Crew ==========
print("\n[TESTE 2] Instanciando Crew...")
try:
    crew = IFSCrew()
    print("   [OK] IFSCrew instanciado com sucesso")
except Exception as e:
    print(f"   [ERRO] Erro ao instanciar IFSCrew: {e}")
    traceback.print_exc()
    sys.exit(1)

# ========== TESTE 3: Criação da Crew ==========
print("\n[TESTE 3] Criando instancia de crew.get_crew()...")
try:
    user_question = "Qual o total de gastos do IFS em 2024?"
    print(f"   Pergunta: {user_question}")

    crew_instance = crew.get_crew(user_question)
    print("   [OK] Crew instance criado com sucesso")
    print(f"   Tipo: {type(crew_instance)}")
except Exception as e:
    print(f"   [ERRO] Erro ao criar crew instance: {e}")
    traceback.print_exc()
    sys.exit(1)

# ========== TESTE 4: Execução do Crew ==========
print("\n[TESTE 4] Executando crew.kickoff()...")
print("-" * 70)
try:
    result = crew_instance.kickoff()
    print("-" * 70)
    print("   [OK] Execucao concluida com sucesso!")
    print(f"\nRESULTADO:\n{result}\n")
except Exception as e:
    print("-" * 70)
    print(f"   [ERRO] Erro na execucao: {e}")
    print(f"   Tipo de erro: {type(e).__name__}")
    traceback.print_exc()
    sys.exit(1)

# ========== TESTE 5: Validação de Resultado ==========
print("\n[TESTE 5] Validando resultado...")
if result and len(str(result)) > 10:
    print("   [OK] Resultado valido (retornou conteudo)")
    print(f"   Tamanho: {len(str(result))} caracteres")
else:
    print("   [AVISO] Resultado vazio ou muito curto")

print("\n" + "="*70)
print("[OK] TESTES CONCLUIDOS COM SUCESSO!")
print("="*70)
print(f"\nTeste executado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("\nProximo passo: streamlit run app_v2.py\n")
