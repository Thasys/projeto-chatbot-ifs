import os
import requests
import pandas as pd
import time
import logging
from datetime import datetime, timedelta
from config import Config
from typing import Dict, List

# --- CONFIGURAR LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_logs.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataExtractor:
    """
    Classe responsável pela extração (E) do ETL.
    Implementa retry logic, rate limiting avançado e validações de API.
    """

    def __init__(self):
        self.base_url = "https://api.portaldatransparencia.gov.br/api-de-dados/despesas/documentos"
        self.headers = {
            "chave-api-dados": Config.API_KEY,
            "Accept": "application/json",
            "User-Agent": "IFS-ChatBot-ETL/1.0"
        }
        self.relatorio_extracao = {
            'timestamp': datetime.now().isoformat(),
            'dias_processados': 0,
            'registros_extraidos': 0,
            'registros_duplicados': 0,
            'erros_api': [],
            'tempo_total': 0
        }
        self.registros_ids = set()  # Para rastrear duplicatas entre requisições

    # ========== MELHORIA 1: RETRY LOGIC COM BACKOFF EXPONENCIAL ==========
    def _requisicao_com_retry(self, params: Dict, max_retries: int = 3) -> Dict:
        """
        Realiza requisição com retry automático e backoff exponencial.
        """
        for tentativa in range(max_retries):
            try:
                response = requests.get(
                    self.base_url,
                    headers=self.headers,
                    params=params,
                    timeout=30
                )

                if response.status_code == 200:
                    if not response.content or not response.text.strip():
                        return []
                    try:
                        return response.json()
                    except Exception:
                        return []

                elif response.status_code == 429:  # Rate Limit
                    tempo_espera = min(2 ** tentativa * 10, 300)  # Max 5 min
                    logger.warning(
                        f"[AGUARDANDO] Rate Limit! Aguardando {tempo_espera}s...")
                    time.sleep(tempo_espera)

                elif response.status_code == 500:
                    tempo_espera = min(2 ** tentativa * 5, 60)
                    logger.warning(
                        f"[ERRO] Erro 500 da API. Tentativa {tentativa + 1}/{max_retries}. Aguardando {tempo_espera}s...")
                    time.sleep(tempo_espera)

                else:
                    logger.error(
                        f"[ERRO] Erro {response.status_code}: {response.text}")
                    return None

            except requests.Timeout:
                logger.warning(
                    f"⏱ Timeout na tentativa {tentativa + 1}/{max_retries}")
                time.sleep(min(2 ** tentativa * 5, 60))

            except requests.ConnectionError as e:
                logger.warning(
                    f"[CONEXAO] Erro de conexão: {e}. Tentativa {tentativa + 1}/{max_retries}")
                time.sleep(min(2 ** tentativa * 5, 60))

        logger.error(f"[ERRO] Falha após {max_retries} tentativas")
        return None

    # ========== MELHORIA 2: GERAÇÃO DE DATAS COM VALIDAÇÃO ==========
    def _gerar_datas(self) -> List[str]:
        """
        Gera lista de datas com validação e logging.
        """
        lista_datas = []
        try:
            d_inicio = datetime.strptime(Config.DATA_INICIO, "%d/%m/%Y")
            d_fim = datetime.strptime(Config.DATA_FIM, "%d/%m/%Y")

            if d_fim < d_inicio:
                raise ValueError(
                    "Data de fim não pode ser anterior a data de início")

            delta = d_fim - d_inicio
            total_dias = delta.days + 1

            for i in range(total_dias):
                dia = d_inicio + timedelta(days=i)
                lista_datas.append(dia.strftime("%d/%m/%Y"))

            logger.info(
                f"[DATA] Período: {Config.DATA_INICIO} até {Config.DATA_FIM} ({total_dias} dias)")
            return lista_datas

        except ValueError as e:
            logger.error(f"[ERRO] Erro na geração de datas: {e}")
            return []

    # ========== MELHORIA 3: DETECÇÃO DE DUPLICATAS ==========
    def _detectar_duplicatas(self, dados: List[Dict]) -> tuple:
        """
        Detecta duplicatas de requisições usando ID único.
        Retorna (dados_unicos, quantidade_duplicatas)
        """
        dados_filtrados = []
        duplicatas = 0

        for registro in dados:
            # Criar ID único baseado em documento + valor + data
            id_unico = f"{registro.get('documento', '')}_{registro.get('valor', '')}_{registro.get('dataEmissao', '')}"

            if id_unico in self.registros_ids:
                duplicatas += 1
                logger.debug(f"[RETRY] Duplicata detectada: {id_unico}")
            else:
                self.registros_ids.add(id_unico)
                dados_filtrados.append(registro)

        self.relatorio_extracao['registros_duplicados'] = duplicatas
        return dados_filtrados, duplicatas

    # ========== MELHORIA 4: VALIDAÇÃO DE DADOS DA API ==========
    def _validar_registro_api(self, registro: Dict) -> bool:
        """
        Valida se um registro da API contém campos obrigatórios.
        """
        campos_obrigatorios = ['documento', 'valor',
                               'data', 'codigoUg', 'ug']

        for campo in campos_obrigatorios:
            if campo not in registro or registro[campo] is None or str(registro[campo]).strip() == '':
                logger.warning(
                    f"[AVISO] Campo obrigatório ausente: {campo} em {registro.get('documento', 'N/A')}")
                return False

        return True

    # ========== MELHORIA 5: EXTRAÇÃO COM TRATAMENTO ROBUSTO ==========
    def extrair_dados(self) -> pd.DataFrame:
        """
        Extrai dados da API com todas as melhorias implementadas.
        """
        inicio = time.time()
        logger.info("=" * 80)
        logger.info("[INICIO] INICIANDO EXTRAÇÃO DE DADOS")
        logger.info("=" * 80)

        dias = self._gerar_datas()
        if not dias:
            logger.error(
                "[ERRO] Nenhuma data gerada. Verifique Config.DATA_INICIO e Config.DATA_FIM")
            return pd.DataFrame()

        todos_dados = []
        registros_validos = 0
        registros_invalidos = 0

        for idx_dia, dia in enumerate(dias, 1):
            pagina = 1
            dados_do_dia = 0

            while True:
                params = {
                    "dataEmissao": dia,
                    "gestao": Config.GESTAO,
                    "fase": Config.FASE,
                    "pagina": pagina
                }

                if Config.UNIDADE_GESTORA:
                    params["unidadeGestora"] = Config.UNIDADE_GESTORA

                logger.info(
                    f"[ETL] [{idx_dia}/{len(dias)}] {dia} | Página {pagina}...")

                # MELHORIA 1: Retry com backoff
                dados = self._requisicao_com_retry(params)

                if dados is None:
                    logger.warning(
                        f"[AVISO] Falha ao extrair {dia} página {pagina}. Continuando...")
                    self.relatorio_extracao['erros_api'].append({
                        'data': dia,
                        'pagina': pagina,
                        'motivo': 'Requisição falhou'
                    })
                    break

                if not dados:
                    logger.info(f"[OK] Fim das páginas para {dia}")
                    break

                # MELHORIA 3: Detecção de duplicatas
                dados_unicos, dup_count = self._detectar_duplicatas(dados)

                if dup_count > 0:
                    logger.warning(
                        f"[RETRY] {dup_count} duplicatas removidas em {dia} página {pagina}")

                # MELHORIA 4: Validação de registros
                for registro in dados_unicos:
                    if self._validar_registro_api(registro):
                        todos_dados.append(registro)
                        registros_validos += 1
                    else:
                        registros_invalidos += 1

                dados_do_dia += len(dados_unicos)
                logger.info(
                    f"   [OK] {len(dados_unicos)} registros da página {pagina}")

                pagina += 1

                # Respeitar API (rate limiting responsável)
                time.sleep(0.5)

            self.relatorio_extracao['dias_processados'] += 1

        # --- SALVAR DADOS EM CSV ---
        if todos_dados:
            try:
                df = pd.json_normalize(todos_dados)

                os.makedirs(Config.CAMINHO_SALVAMENTO, exist_ok=True)

                nome_arquivo = f"backup_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                caminho_completo = os.path.join(
                    Config.CAMINHO_SALVAMENTO, nome_arquivo)

                df.to_csv(caminho_completo, index=False,
                          sep=';', encoding='utf-8-sig')

                tempo_decorrido = time.time() - inicio
                self.relatorio_extracao['tempo_total'] = tempo_decorrido
                self.relatorio_extracao['registros_extraidos'] = len(df)

                logger.info("=" * 80)
                logger.info("[OK] EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
                logger.info(f"[GRAFICO] Registros extraídos: {registros_validos}")
                logger.info(f"[AVISO] Registros inválidos: {registros_invalidos}")
                logger.info(f"📂 Arquivo: {nome_arquivo}")
                logger.info(f"⏱ Tempo total: {tempo_decorrido:.2f}s")
                logger.info("=" * 80)
                logger.info(f"[LISTA] Relatório: {self.relatorio_extracao}")

                return df

            except Exception as e:
                logger.error(f"[ERRO] Erro ao salvar arquivo: {e}")
                return pd.DataFrame()

        else:
            logger.warning("[AVISO] Nenhum dado extraído no período especificado")
            return pd.DataFrame()

    # ========== MELHORIA 6: CARREGAR BACKUP LOCAL (para testes) ==========
    def carregar_backup_local(self) -> pd.DataFrame:
        """
        Carrega o arquivo CSV mais recente da pasta local.
        Útil para testes e re-execução.
        """
        logger.info(f"📂 Buscando dados locais em: {Config.CAMINHO_SALVAMENTO}")

        if not os.path.exists(Config.CAMINHO_SALVAMENTO):
            logger.error("[ERRO] Pasta de dados não encontrada")
            return pd.DataFrame()

        arquivos = [f for f in os.listdir(Config.CAMINHO_SALVAMENTO)
                    if f.startswith("backup_raw_") and f.endswith(".csv")]

        if not arquivos:
            logger.error("[ERRO] Nenhum arquivo de backup encontrado")
            return pd.DataFrame()

        arquivos.sort(reverse=True)
        arquivo_recente = arquivos[0]
        caminho_completo = os.path.join(
            Config.CAMINHO_SALVAMENTO, arquivo_recente)

        try:
            logger.info(f"📂 Carregando: {arquivo_recente}")
            df = pd.read_csv(caminho_completo, sep=';', encoding='utf-8-sig')

            logger.info(f"[OK] {len(df)} registros carregados do disco")
            return df

        except Exception as e:
            logger.error(f"[ERRO] Erro ao ler arquivo: {e}")
            return pd.DataFrame()
