from sqlalchemy import create_engine, text
from config import Config

class DataLoader:
    def __init__(self):
        self.engine = create_engine(Config.DB_URI)

    def carregar_mysql(self, dados_transformados):
        if not dados_transformados:
            return

        print("\n--- Iniciando Carga no MySQL ---")
        
        # Ordem de carga: Dimensões primeiro, depois Fato (devido a Foreign Keys se existissem constraints)
        tabelas = [
            ('dim_favorecido', dados_transformados['dim_favorecido']),
            ('dim_programa', dados_transformados['dim_programa']),
            ('dim_natureza', dados_transformados['dim_natureza']),
            ('dim_ug', dados_transformados['dim_ug']),
            ('fato_execucao', dados_transformados['fato_execucao'])
        ]

        with self.engine.connect() as conn:
            for nome_tabela, df in tabelas:
                try:
                    print(f"Carregando tabela: {nome_tabela} ({len(df)} linhas)...")
                    # 'replace' recria a tabela a cada execução. 
                    # Em produção, usaria 'append' com verificação de IDs existentes.
                    df.to_sql(name=nome_tabela, con=conn, if_exists='replace', index=False)
                except Exception as e:
                    print(f"Erro ao carregar {nome_tabela}: {e}")
        
        print("✅ Carga concluída com sucesso no MySQL Workbench!")