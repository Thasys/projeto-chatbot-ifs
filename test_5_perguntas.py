# -*- coding: utf-8 -*-
"""
Script de teste com 5 perguntas realistas para ambos os apps.
Testa: app.py e app_v2.py
"""

from crew_definition_v2 import IFSCrewV2
from crew_definition import IFSCrew
import sys
import os
from datetime import datetime

# Forcar UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


# Perguntas realistas para teste
PERGUNTAS = [
    "Qual o total de gastos do IFS em 2024?",
    "Quais foram os 5 maiores fornecedores do IFS em 2024?",
    "Quanto o IFS gastou com a Energisa em 2024?",
    "Qual foi o gasto total do Campus de Propriá em janeiro de 2024?",
    "Quais foram as maiores despesas com diárias e passagens em 2024?"
]


def testar_crew_v1(perguntas):
    """Testa app.py (IFSCrew)"""
    print("\n" + "="*80)
    print("TESTE CREW V1 (app.py - IFSCrew)")
    print("="*80)

    try:
        crew = IFSCrew()
        print("[OK] IFSCrew instanciado\n")
    except Exception as e:
        print(f"[ERRO] Falha ao instanciar IFSCrew: {e}")
        return False

    resultados = []
    for i, pergunta in enumerate(perguntas, 1):
        print(f"\n[PERGUNTA {i}] {pergunta}")
        print("-" * 80)

        try:
            crew_instance = crew.get_crew(pergunta)
            resultado = crew_instance.kickoff()

            # Limitar tamanho da resposta para exibição
            resultado_exibido = str(resultado)[
                :400] + "..." if len(str(resultado)) > 400 else str(resultado)
            print(f"RESPOSTA: {resultado_exibido}\n")

            resultados.append({
                "pergunta": pergunta,
                "status": "OK",
                "caracteres": len(str(resultado))
            })
            print(f"[OK] Sucesso ({len(str(resultado))} caracteres)")

        except Exception as e:
            print(
                f"[ERRO] Execucao falhou: {type(e).__name__}: {str(e)[:200]}")
            resultados.append({
                "pergunta": pergunta,
                "status": "ERRO",
                "erro": type(e).__name__
            })

    return resultados


def testar_crew_v2(perguntas):
    """Testa app_v2.py (IFSCrewV2)"""
    print("\n" + "="*80)
    print("TESTE CREW V2 (app_v2.py - IFSCrewV2)")
    print("="*80)

    try:
        crew = IFSCrewV2(use_json_mode=True, cache_ttl=300)
        print("[OK] IFSCrewV2 instanciado\n")
    except Exception as e:
        print(f"[ERRO] Falha ao instanciar IFSCrewV2: {e}")
        return False

    resultados = []
    for i, pergunta in enumerate(perguntas, 1):
        print(f"\n[PERGUNTA {i}] {pergunta}")
        print("-" * 80)

        try:
            crew_instance = crew.get_crew(pergunta)
            crew_response = crew.execute_with_confidence(
                crew_instance, pergunta)

            resultado = crew_response['resposta']
            confidence = crew_response['confidence']

            # Limitar tamanho da resposta para exibição
            resultado_exibido = str(resultado)[
                :400] + "..." if len(str(resultado)) > 400 else str(resultado)
            print(f"RESPOSTA: {resultado_exibido}\n")
            print(f"CONFIANCA: {confidence:.1f}%")

            resultados.append({
                "pergunta": pergunta,
                "status": "OK",
                "caracteres": len(str(resultado)),
                "confidence": confidence
            })
            print(
                f"[OK] Sucesso ({len(str(resultado))} caracteres, {confidence:.1f}% confianca)")

        except Exception as e:
            print(
                f"[ERRO] Execucao falhou: {type(e).__name__}: {str(e)[:200]}")
            resultados.append({
                "pergunta": pergunta,
                "status": "ERRO",
                "erro": type(e).__name__
            })

    return resultados


def resumo_testes(v1_resultados, v2_resultados):
    """Exibe resumo dos testes"""
    print("\n" + "="*80)
    print("RESUMO DOS TESTES")
    print("="*80)

    print("\n[APP.PY - CREW V1]")
    v1_ok = sum(1 for r in v1_resultados if r["status"] == "OK")
    v1_total = len(v1_resultados)
    print(f"  Sucessos: {v1_ok}/{v1_total}")
    if v1_ok < v1_total:
        for r in v1_resultados:
            if r["status"] == "ERRO":
                print(f"    - {r['pergunta'][:50]}... [{r['erro']}]")

    print("\n[APP_V2.PY - CREW V2]")
    v2_ok = sum(1 for r in v2_resultados if r["status"] == "OK")
    v2_total = len(v2_resultados)
    print(f"  Sucessos: {v2_ok}/{v2_total}")
    if v2_ok < v2_total:
        for r in v2_resultados:
            if r["status"] == "ERRO":
                print(f"    - {r['pergunta'][:50]}... [{r['erro']}]")

    # Confidence scores v2
    v2_confs = [r.get("confidence", 0)
                for r in v2_resultados if r["status"] == "OK"]
    if v2_confs:
        print(f"  Confianca media: {sum(v2_confs)/len(v2_confs):.1f}%")

    print("\n" + "="*80)
    print(
        f"RESULTADO FINAL: {v1_ok + v2_ok}/{v1_total + v2_total} testes passaram")
    print(f"Tempo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*80)


if __name__ == "__main__":
    print("TESTE DE SISTEMA - 5 PERGUNTAS REALISTAS")
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")

    print("PERGUNTAS A TESTAR:")
    for i, p in enumerate(PERGUNTAS, 1):
        print(f"  {i}. {p}")

    # Testar ambos
    v1_resultados = testar_crew_v1(PERGUNTAS)
    v2_resultados = testar_crew_v2(PERGUNTAS)

    # Resumo
    resumo_testes(v1_resultados, v2_resultados)
