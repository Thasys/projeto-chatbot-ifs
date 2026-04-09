#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simplificado de 5 perguntas - Versão SEM emojis para Windows console
"""

import sys
import os
import logging
from datetime import datetime

# Forçar encoding UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

# Desabilitar logging do CrewAI verboso
for logger_name in ['crew', 'crewai', 'langchain']:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

logging.basicConfig(level=logging.WARNING)

print("\n" + "="*70)
print("TESTE DE 5 PERGUNTAS - APP.PY vs APP_V2.PY")
print("Data: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("="*70)

# Perguntas para teste
PERGUNTAS = [
    "Qual o total de gastos do IFS em 2024?",
    "Quais foram os 5 maiores fornecedores do IFS em 2024?",
    "Quanto o IFS gastou com a Energisa em 2024?",
    "Qual foi o gasto total do Campus de Propria em janeiro de 2024?",
    "Quais foram as maiores despesas com diarias em 2024?"
]

RESPOSTAS_ESPERADAS = {
    0: "Total de gastos em 2024",
    1: "5 maiores fornecedores",
    2: "Energisa",
    3: "Campus Propria em janeiro",
    4: "Maiores despesas com diarias"
}

# ======================== TESTE 1: APP.PY ========================
print("\n[TESTE 1] APP.PY (IFSCrew v1)")
print("-"*70)

sucessos_app1 = 0
erros_app1 = 0

try:
    from crew_definition import IFSCrew
    print("[OK] Importacao de crew_definition.IFSCrew")

    crew = IFSCrew()
    print("[OK] Instanciacao de IFSCrew\n")

    for i, pergunta in enumerate(PERGUNTAS, 1):
        print(f"[PERGUNTA {i}] {pergunta[:45]}...")
        try:
            crew_inst = crew.get_crew(pergunta)
            resultado = crew_inst.kickoff()
            resultado_str = str(resultado)
            char_count = len(resultado_str)
            
            # Validacoes basicas
            tem_dados = len(resultado_str) > 100
            tem_reais = "R$" in resultado_str
            
            status = "[PASS]" if tem_dados else "[INFO]"
            print(f"        Status: {status} ({char_count} chars, reais: {tem_reais})")
            
            sucessos_app1 += 1
        except Exception as e:
            print(f"        Status: [ERRO] {type(e).__name__}: {str(e)[:60]}")
            erros_app1 += 1

    print(f"\n>>> RESULTADO APP.PY: {sucessos_app1} OK, {erros_app1} ERROS")

except Exception as e:
    print(f"[ERRO] Falha geral ao testar APP.PY:")
    print(f"       {type(e).__name__}: {str(e)[:100]}")
    erros_app1 = 5

# ======================== TESTE 2: APP_V2.PY ========================
print("\n[TESTE 2] APP_V2.PY (IFSCrewV2 v2 com Confidence)")
print("-"*70)

sucessos_app2 = 0
erros_app2 = 0

try:
    from crew_definition_v2 import IFSCrewV2
    print("[OK] Importacao de crew_definition_v2.IFSCrewV2")

    crew_v2 = IFSCrewV2()
    print("[OK] Instanciacao de IFSCrewV2\n")

    for i, pergunta in enumerate(PERGUNTAS, 1):
        print(f"[PERGUNTA {i}] {pergunta[:45]}...")
        try:
            crew_inst = crew_v2.get_crew(pergunta)
            crew_response = crew_v2.execute_with_confidence(crew_inst, pergunta)
            
            resultado_str = crew_response['resposta']
            confidence = crew_response['confidence']
            char_count = len(resultado_str)
            
            # Validacoes basicas
            tem_dados = len(resultado_str) > 100
            tem_reais = "R$" in resultado_str
            
            status = "[PASS]" if tem_dados else "[INFO]"
            print(f"        Status: {status} ({char_count} chars, conf: {confidence:.0f}%, reais: {tem_reais})")
            
            sucessos_app2 += 1
        except Exception as e:
            print(f"        Status: [ERRO] {type(e).__name__}: {str(e)[:60]}")
            erros_app2 += 1

    print(f"\n>>> RESULTADO APP_V2.PY: {sucessos_app2} OK, {erros_app2} ERROS")

except Exception as e:
    print(f"[ERRO] Falha geral ao testar APP_V2.PY:")
    print(f"       {type(e).__name__}: {str(e)[:100]}")
    erros_app2 = 5

# ======================== RESUMO FINAL ========================
print("\n" + "="*70)
print("RESUMO FINAL")
print("="*70)

total_ok = sucessos_app1 + sucessos_app2
total_erros = erros_app1 + erros_app2
total_testes = total_ok + total_erros

print(f"APP.PY:    {sucessos_app1}/5 OK  |  {erros_app1} ERROS")
print(f"APP_V2.PY: {sucessos_app2}/5 OK  |  {erros_app2} ERROS")
print(f"TOTAL:     {total_ok}/{total_testes} OK  |  {total_erros} ERROS")

if total_erros == 0:
    print("\n[SUCESSO] Todos os testes passaram!")
    sys.exit(0)
else:
    print(f"\n[ATENCAO] {total_erros} teste(s) falharam")
    sys.exit(1)
