import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()


class LLMFactory:
    @staticmethod
    def create_llm():
        """
        Cria e retorna uma instância de LLM usando a classe nativa do CrewAI.
        Isso evita erros de roteamento para a API da OpenAI.
        """
        provider = os.getenv("LLM_PROVIDER", "openai").lower()

        if provider == "openai":
            model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")
            print(f"[LLM] Init OpenAI ({model_name})")
            return LLM(
                model=model_name,
                api_key=os.getenv("OPENAI_API_KEY")
            )

        elif provider == "ollama":
            model_name = os.getenv("OLLAMA_MODEL_NAME", "llama3")
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

            print(f"[LLM] Init Ollama ({model_name}) @ {base_url}")

            # O prefixo 'ollama/' é CRUCIAL para o CrewAI saber que é local
            # Se o modelo no .env já tiver 'ollama/', não adicionamos de novo
            full_model_name = model_name if model_name.startswith(
                "ollama/") else f"ollama/{model_name}"

            return LLM(
                model=full_model_name,
                base_url=base_url
            )

        else:
            raise ValueError(f"Provedor '{provider}' não suportado.")
