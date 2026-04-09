#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste rápido: Uma pergunta em app_v2.py
"""

import sys
import logging

# Desabilitar logging verbose de CrewAI
for logger_name in ['crew', 'crewai', 'langchain', 'httpx']:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)

print("\n" + "="*70)
print("TESTE RÁPIDO: Uma pergunta (Pergunta 1)")
print("="*70 + "\n")

try:
    print("[1] Importando crew_definition_v2...")
    from crew_definition_v2 import IFSCrewV2

    print("[2] Criando instancia de IFSCrewV2...")
    crew_v2 = IFSCrewV2()

    pergunta = "Qual o total de gastos do IFS em 2024?"
    print(f"[3] Executando pergunta: '{pergunta}'")
    print("-"*70)

    crew_inst = crew_v2.get_crew(pergunta)
    crew_response = crew_v2.execute_with_confidence(crew_inst, pergunta)

    resposta = crew_response['resposta']
    confidence = crew_response['confidence']

    print(f"\n[RESULTADO]")
    print(f"Confiança: {confidence:.0f}%")
    print(f"\nResposta:\n{resposta}")

    # Validar resultado
    print(f"\n[VALIDAÇÃO]")
    if "339" in resposta or "R$" in resposta:
        print("✅ Contém valor em R$")
    else:
        print("❌ Não contém valor em R$")

    if confidence > 70:
        print(f"✅ Confiança > 70% ({confidence:.0f}%)")
    else:
        print(f"❌ Confiança baixa ({confidence:.0f}%)")

except Exception as e:
    print(f"❌ ERRO: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70 + "\n")
