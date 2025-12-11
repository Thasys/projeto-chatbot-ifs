import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    API_KEY = os.getenv("API_KEY")
    # Ajuste as datas para um intervalo válido
    DATA_INICIO = "01/01/2024"
    DATA_FIM = "31/12/2024"

    # Parâmetros API
    UNIDADE_GESTORA = None
    GESTAO = "26423"
    FASE = "3"

    # Banco de Dados MySQL
    DB_URI = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

    CAMINHO_SALVAMENTO = os.path.join(os.getcwd(), "dados_brutos")
