import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect, event
from sqlalchemy.pool import StaticPool
import logging

logger = logging.getLogger(__name__)

load_dotenv()


class DBConnection:
    """
    Gerenciador de conexão com banco MySQL com Singleton pattern.
    Inclui validação de conexão, retry logic e tratamento de erro.
    """
    _instance = None
    _is_connected = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBConnection, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance

    def _initialize_connection(self):
        """Inicializa conexão com validação e retry."""
        try:
            user = os.getenv("DB_USER")
            password = os.getenv("DB_PASS")
            host = os.getenv("DB_HOST")
            port = os.getenv("DB_PORT")
            database = os.getenv("DB_NAME")

            # Validar variáveis de ambiente
            if not all([user, password, host, port, database]):
                raise ValueError(
                    "⚠️ Variáveis de ambiente incompletas. Verifique .env")

            # Configuração da string de conexão
            db_url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"

            # Criar engine com pool_pre_ping para validar conexões
            self.engine = create_engine(
                db_url,
                echo=False,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,  # Valida conexão antes de usar
                pool_recycle=3600,  # Recicla conexões a cada 1 hora
                connect_args={
                    "auth_plugin": "mysql_native_password",
                    "autocommit": True,
                }
            )

            # Testar conexão
            self._validate_connection()
            self._is_connected = True
            logger.info(
                "✅ Conexão com banco de dados estabelecida com sucesso")

        except Exception as e:
            self._is_connected = False
            logger.error(f"❌ Erro ao inicializar conexão BD: {e}")
            raise

    def _validate_connection(self):
        """Testa se consegue conectar ao banco."""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.close()
            logger.info("✅ Validação de conexão OK")
        except Exception as e:
            logger.error(f"❌ Falha na validação de conexão: {e}")
            raise ConnectionError(
                f"Não conseguiu conectar ao banco de dados: {e}")

    def get_engine(self):
        """Retorna SQLAlchemy engine."""
        if not self._is_connected:
            raise RuntimeError("Conexão não está ativa. Reinicie a aplicação.")
        return self.engine

    def execute_query(self, query, params=None):
        """
        Executa query SELECT com tratamento de erro.

        Args:
            query (str): SQL query com :named_parameters (SQLAlchemy style)
            params (dict): Dicionário com valores dos parâmetros

        Returns:
            list: Lista de dicts com resultados
        """
        try:
            with self.engine.connect() as connection:
                # Converter params para dict se necessário
                params_dict = params if isinstance(params, dict) else {}
                result = connection.execute(text(query), params_dict)
                keys = result.keys()
                return [dict(zip(keys, row)) for row in result.fetchall()]
        except Exception as e:
            logger.error(f"❌ Erro ao executar query: {e}")
            raise

    def get_schema_info(self):
        """Retorna informações do schema do banco."""
        try:
            inspector = inspect(self.engine)
            schema_info = []

            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                cols_desc = ", ".join(
                    [f"{col['name']} ({col['type']})" for col in columns])
                schema_info.append(
                    f"Table: {table_name} | Columns: {cols_desc}")

            return "\n".join(schema_info)
        except Exception as e:
            logger.error(f"❌ Erro ao inspecionar schema: {e}")
            return f"Erro ao inspecionar schema: {str(e)}"

    def is_connected(self) -> bool:
        """Verifica se está conectado ao banco."""
        return self._is_connected

    def close(self):
        """Fecha a conexão."""
        if self.engine:
            self.engine.dispose()
            self._is_connected = False
            logger.info("🔌 Conexão fechada")
