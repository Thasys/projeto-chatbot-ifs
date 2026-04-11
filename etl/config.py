import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()


class Config:
    API_KEY = os.getenv("API_KEY")
    # Ajuste as datas para um intervalo válido
    # DATA_INICIO = "01/01/2024"
    # DATA_FIM = "30/06/2025"
    DATA_FIM = datetime.now().strftime("%d/%m/%Y")
    DATA_INICIO = (datetime.now() - timedelta(days=180)).strftime("%d/%m/%Y")

    # Parâmetros API
    UNIDADE_GESTORA = None
    GESTAO = "26423"
    FASE = "3"

    # Banco de Dados MySQL
    DB_URI = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

    CAMINHO_SALVAMENTO = os.path.join(os.getcwd(), "data", "raw")
