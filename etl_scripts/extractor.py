import os
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from config import Config

class DataExtractor:
    def __init__(self):
        self.base_url = "https://api.portaldatransparencia.gov.br/api-de-dados/despesas/documentos"
        self.headers = {"chave-api-dados": Config.API_KEY, "Accept": "application/json"}

    def _gerar_datas(self):
        lista_datas = []
        try:
            d_inicio = datetime.strptime(Config.DATA_INICIO, "%d/%m/%Y")
            d_fim = datetime.strptime(Config.DATA_FIM, "%d/%m/%Y")
            delta = d_fim - d_inicio
            for i in range(delta.days + 1):
                dia = d_inicio + timedelta(days=i)
                lista_datas.append(dia.strftime("%d/%m/%Y"))
        except ValueError as e:
            print(f"Erro na geração de datas: {e}")
            return []
        return lista_datas

    def extrair_dados(self):
        dias = self._gerar_datas()
        todos_dados = []
        
        print(f"--- Iniciando Extração: {len(dias)} dias ---")

        for dia in dias:
            pagina = 1
            while True:
                params = {
                    "dataEmissao": dia,
                    "gestao": Config.GESTAO,
                    "fase": Config.FASE,
                    "pagina": pagina
                }
                if Config.UNIDADE_GESTORA:
                    params["unidadeGestora"] = Config.UNIDADE_GESTORA

                try:
                    print(f"Extraindo {dia} | Pág {pagina}...", end='\r')
                    response = requests.get(self.base_url, headers=self.headers, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        dados = response.json()
                        if not dados: break
                        todos_dados.extend(dados)
                        pagina += 1
                        time.sleep(0.2) # Respeitar API
                    elif response.status_code == 429:
                        print("\nRate Limit. Aguardando 10s...")
                        time.sleep(10)
                    else:
                        print(f"\nErro {response.status_code} no dia {dia}")
                        break
                except Exception as e:
                    print(f"\nErro de conexão: {e}")
                    break
        
        if todos_dados:
            df = pd.json_normalize(todos_dados)
            
            # 1. Garante que a pasta de destino existe
            os.makedirs(Config.CAMINHO_SALVAMENTO, exist_ok=True)
            
            # 2. Define o nome do arquivo
            nome_arquivo = f"backup_raw_{datetime.now().strftime('%Y%m%d')}.csv"
            
            # 3. Cria o caminho completo (Pasta + Nome do Arquivo)
            caminho_completo = os.path.join(Config.CAMINHO_SALVAMENTO, nome_arquivo)
            
            # 4. Salva usando o caminho completo
            df.to_csv(caminho_completo, index=False, sep=';', encoding='utf-8-sig')
            
            print(f"\n✅ Extração concluída. {len(df)} registros.")
            print(f"📂 Arquivo salvo em: {caminho_completo}")
            return df
            
        print("\n⚠️ Nenhum dado encontrado no período.")
        return pd.DataFrame()