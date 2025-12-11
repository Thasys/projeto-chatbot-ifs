import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

load_dotenv()


class DBConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBConnection, cls).__new__(cls)
            user = os.getenv("DB_USER")
            password = os.getenv("DB_PASS")
            host = os.getenv("DB_HOST")
            port = os.getenv("DB_PORT")
            database = os.getenv("DB_NAME")

            # Configuração da string de conexão
            db_url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
            cls._instance.engine = create_engine(db_url)
        return cls._instance

    def get_engine(self):
        return self.engine

    def execute_query(self, query, params=None):

        with self.engine.connect() as connection:
            result = connection.execute(text(query), params or {})

            keys = result.keys()
            return [dict(zip(keys, row)) for row in result.fetchall()]

    def get_schema_info(self):

        try:

            inspector = inspect(self.engine)
            schema_info = []

            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                # Formata: nome_coluna (tipo)
                cols_desc = ", ".join(
                    [f"{col['name']} ({col['type']})" for col in columns])
                schema_info.append(
                    f"Table: {table_name} | Columns: {cols_desc}")

            return "\n".join(schema_info)
        except Exception as e:
            return f"Error inspecting schema: {str(e)}"
