from extractor import DataExtractor
from transformer import DataTransformer
from loader import DataLoader

def main():
    # 1. Extração
    extractor = DataExtractor()
    df_raw = extractor.extrair_dados()
    
    if df_raw.empty:
        print("Processo abortado: Falha na extração.")
        return

    # 2. Transformação
    transformer = DataTransformer()
    dados_prontos = transformer.processar(df_raw)

    # 3. Carga
    loader = DataLoader()
    loader.carregar_mysql(dados_prontos)

if __name__ == "__main__":
    main()