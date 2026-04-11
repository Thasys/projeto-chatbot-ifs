import sys
from crew_definition_v2 import IFSCrewV2

def main():
    print("### IFS Transparência Inteligente — Modo CLI ###")
    print("Digite 'sair' para encerrar.\n")

    crew_engine = IFSCrewV2(use_json_mode=True, cache_ttl=300)

    while True:
        try:
            user_input = input("Pergunta: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'sair', 'quit']:
                break

            crew_instance = crew_engine.get_crew(user_input)
            resultado = crew_engine.execute_with_confidence(crew_instance, user_input)

            print("\n--- RESPOSTA ---")
            print(resultado['resposta'])
            print(f"Confiança: {resultado['confidence']:.0f}%\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    main()