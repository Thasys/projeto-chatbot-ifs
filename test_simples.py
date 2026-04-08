#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simplificado de 5 perguntas para diagnostico de funcionalidade
"""

import sys
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("\n" + "="*70)
print("TESTE DE 5 PERGUNTAS - APP.PY vs APP_V2.PY")
print("="*70)

# Perguntas para teste
PERGUNTAS = [
    "Qual o total de gastos do IFS em 2024?",
    "Quais foram os 5 maiores fornecedores do IFS em 2024?",
    "Quanto o IFS gastou com a Energisa em 2024?",
    "Qual foi o gasto total do Campus de Propriá em janeiro de 2024?",
    "Quais foram as maiores despesas com diárias em 2024?"
]

# Teste APP.PY
print("\n[TESTE 1] APP.PY (IFSCrew v1)")
print("-"*70)

try:
    from crew_definition import IFSCrew
    print("Importacao: OK")

    crew = IFSCrew()
    print("Instanciacao: OK\n")

    sucessos = 0
    erros = 0

    for i, pergunta in enumerate(PERGUNTAS, 1):
        print(f"\nPergunta {i}: {pergunta[:50]}...")
        try:
            crew_inst = crew.get_crew(pergunta)
            resultado = crew_inst.kickoff()
            print(f"  Status: OK ({len(str(resultado))} chars)")
            sucessos += 1
        except Exception as e:
            print(f"  Status: ERRO ({type(e).__name__})")
            erros += 1

    print(f"\nRESULTADO V1: {sucessos} OK, {erros} ERROS")

except Exception as e:
    print(f"FALHA GERAL: {e}")

# Teste APP_V2.PY
print("\n" + "="*70)
print("[TESTE 2] APP_V2.PY (IFSCrewV2 v2)")
print("-"*70)

try:
    from crew_definition_v2 import IFSCrewV2
    print("Importacao: OK")

    crew = IFSCrewV2(use_json_mode=True, cache_ttl=300)
    print("Instanciacao: OK\n")

    sucessos = 0
    erros = 0

    for i, pergunta in enumerate(PERGUNTAS, 1):
        print(f"\nPergunta {i}: {pergunta[:50]}...")
        try:
            crew_inst = crew.get_crew(pergunta)
            crew_resp = crew.execute_with_confidence(crew_inst, pergunta)
            resultado = crew_resp['resposta']
            confidence = crew_resp['confidence']
            print(
                f"  Status: OK ({len(str(resultado))} chars, {confidence:.0f}% conf)")
            sucessos += 1
        except Exception as e:
            print(f"  Status: ERRO ({type(e).__name__})")
            erros += 1

    print(f"\nRESULTADO V2: {sucessos} OK, {erros} ERROS")

except Exception as e:
    print(f"FALHA GERAL: {e}")

print("\n" + "="*70)
print("FIM DO TESTE")
print("="*70 + "\n")
