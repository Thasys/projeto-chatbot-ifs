import sys
from crew_definition import IFSCrew

def main():
    print("### IFS Finance Chatbot Initialized ###")
    print("Type 'exit' to quit.")
    
    ifs_crew_system = IFSCrew()

    while True:
        try:
            user_input = input("\nPergunte sobre os dados públicos: ")
            if user_input.lower() in ['exit', 'sair', 'quit']:
                break

            crew = ifs_crew_system.get_crew(user_input)
            result = crew.kickoff()

            print("\n\n########################")
            print("## RESPOSTA DO AGENTE ##")
            print("########################\n")
            print(result)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()