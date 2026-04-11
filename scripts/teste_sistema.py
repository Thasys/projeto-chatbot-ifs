"""
Teste manual do sistema com 5 perguntas de usuário comum.
Cobre: guardrails, busca de entidade, SQL, crew completo, score de confiança.
"""
import os
import sys
import time
import logging
from datetime import datetime

# Forçar UTF-8 no stdout para evitar UnicodeEncodeError no Windows
if sys.stdout.encoding != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.WARNING)  # Silenciar logs verbosos do CrewAI

SEPARADOR = "=" * 70

PERGUNTAS = [
    {
        "id": 1,
        "pergunta": "Me mostre tudo",
        "descricao": "Pergunta vaga — deve ser interceptada pelos Guardrails",
        "esperado": "guardrails",
    },
    {
        "id": 2,
        "pergunta": "Quais os 5 maiores fornecedores do IFS em 2024?",
        "descricao": "Ranking — GROUP BY + ORDER BY DESC + LIMIT 5",
        "esperado": "crew",
    },
    {
        "id": 3,
        "pergunta": "Quanto foi pago para Energisa em 2024?",
        "descricao": "Total por entidade — fuzzy match + SUM(valor)",
        "esperado": "crew",
    },
    {
        "id": 4,
        "pergunta": "Qual o gasto total do Campus Lagarto?",
        "descricao": "Filtro por unidade pagadora",
        "esperado": "crew",
    },
    {
        "id": 5,
        "pergunta": "Quais foram as diárias pagas pelo IFS em 2024?",
        "descricao": "Filtro por tipo de despesa",
        "esperado": "crew",
    },
]


def testar_guardrails(pergunta: str) -> str | None:
    from guardrails import Guardrails
    gr = Guardrails("respostas_prontas.json")
    return gr.check_intent(pergunta)


def testar_crew(pergunta: str) -> dict:
    from crew_definition_v2 import IFSCrewV2
    crew_engine = IFSCrewV2(use_json_mode=True, cache_ttl=300)
    crew_instance = crew_engine.get_crew(pergunta)
    return crew_engine.execute_with_confidence(crew_instance, pergunta)


def imprimir_resultado(num, pergunta, descricao, inicio, resultado_tipo, conteudo, confianca=None):
    duracao = time.time() - inicio
    print(f"\n{SEPARADOR}")
    print(f"PERGUNTA {num}: {pergunta}")
    print(f"Descrição : {descricao}")
    print(f"Tempo     : {duracao:.2f}s")
    if confianca is not None:
        if confianca >= 80:
            badge = "🟢"
        elif confianca >= 50:
            badge = "🟡"
        else:
            badge = "🔴"
        print(f"Confiança : {badge} {confianca:.0f}%")
    print(f"Via       : {resultado_tipo}")
    print(f"\nRESPOSTA:\n{conteudo}")


def main():
    print(f"\n{'#' * 70}")
    print(f"  TESTE DO SISTEMA — {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{'#' * 70}")

    resultados_sumario = []

    for item in PERGUNTAS:
        num = item["id"]
        pergunta = item["pergunta"]
        descricao = item["descricao"]
        esperado = item["esperado"]
        inicio = time.time()

        print(f"\n[{num}/5] Testando: {pergunta[:60]}...")

        try:
            # 1. Verificar guardrails primeiro
            resposta_pronta = testar_guardrails(pergunta)

            if resposta_pronta:
                imprimir_resultado(
                    num, pergunta, descricao, inicio,
                    "GUARDRAILS (interceptado)",
                    resposta_pronta
                )
                status = "OK" if esperado == "guardrails" else "INESPERADO"

            else:
                # 2. Chamar crew completo
                resultado = testar_crew(pergunta)
                resposta = resultado["resposta"]
                confianca = resultado["confidence"]
                warnings = resultado.get("warnings", [])

                imprimir_resultado(
                    num, pergunta, descricao, inicio,
                    "CREW (pipeline completo)",
                    resposta,
                    confianca=confianca
                )

                if warnings:
                    print(f"\nAvisos: {warnings}")

                status = "OK" if esperado == "crew" else "INESPERADO"

        except Exception as e:
            duracao = time.time() - inicio
            print(f"\n{SEPARADOR}")
            print(f"PERGUNTA {num}: {pergunta}")
            print(f"ERRO após {duracao:.2f}s: {type(e).__name__}: {str(e)[:300]}")
            status = "ERRO"

        resultados_sumario.append({"id": num, "pergunta": pergunta[:50], "status": status})

    # Sumário final
    print(f"\n\n{'#' * 70}")
    print("  SUMÁRIO DOS TESTES")
    print(f"{'#' * 70}")
    for r in resultados_sumario:
        icone = "✅" if r["status"] == "OK" else ("⚠️" if r["status"] == "INESPERADO" else "❌")
        print(f"  {icone} [{r['id']}] {r['pergunta']} — {r['status']}")

    total_ok = sum(1 for r in resultados_sumario if r["status"] == "OK")
    print(f"\n  {total_ok}/{len(PERGUNTAS)} testes passaram\n")


if __name__ == "__main__":
    main()
