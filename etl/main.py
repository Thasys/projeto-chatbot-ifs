import logging
import sys
import json
import pandas as pd
from datetime import datetime
from extractor import DataExtractor
from transformer_v2 import DataTransformerV2 as DataTransformer
from loader import DataLoader
from config import Config
from typing import Dict


# --- CONFIGURAR LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/etl.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
# Antes de começar:
loader = DataLoader()
loader._criar_tabelas_com_constraints()
logger.info("✅ Schema validado")


class ETLOrchestrator:
    """
    Orquestrador do pipeline ETL completo.
    Coordena Extração → Transformação → Carga com tratamento de erros e rollback.
    """

    def __init__(self):
        self.relatorio_final = {
            'timestamp_inicio': datetime.now().isoformat(),
            'etapas': {
                'extracao': {'status': 'PENDENTE', 'dados': None, 'erros': []},
                'transformacao': {'status': 'PENDENTE', 'dados': None, 'erros': []},
                'carga': {'status': 'PENDENTE', 'dados': None, 'erros': []}
            },
            'status_geral': 'EXECUTANDO',
            'tempo_total': 0
        }

    # ========== ETAPA 1: EXTRAÇÃO ==========
    def executar_extracao(self, usar_backup_local: bool = False) -> pd.DataFrame:
        """
        Executa etapa de extração com opção de usar backup local.
        """
        logger.info("=" * 80)
        logger.info("🔄 ETAPA 1: EXTRAÇÃO DE DADOS")
        logger.info("=" * 80)

        try:
            extractor = DataExtractor()

            if usar_backup_local:
                logger.info("📂 Usando backup local para testes...")
                df_raw = extractor.carregar_backup_local()
            else:
                logger.info("🌐 Extraindo dados da API...")
                df_raw = extractor.extrair_dados()

            if df_raw is None or df_raw.empty:
                raise ValueError("Extração retornou DataFrame vazio")

            self.relatorio_final['etapas']['extracao']['status'] = 'SUCESSO'
            self.relatorio_final['etapas']['extracao']['dados'] = {
                'quantidade_registros': len(df_raw),
                'quantidade_colunas': len(df_raw.columns),
                'relatorio': extractor.relatorio_extracao
            }

            logger.info(
                f"✅ Extração concluída: {len(df_raw)} registros, {len(df_raw.columns)} colunas")
            logger.info(f"📊 Relatório: {extractor.relatorio_extracao}")

            return df_raw

        except Exception as e:
            logger.error(f"❌ Erro na extração: {e}")
            self.relatorio_final['etapas']['extracao']['status'] = 'ERRO'
            self.relatorio_final['etapas']['extracao']['erros'].append(str(e))
            return None

    # ========== ETAPA 2: TRANSFORMAÇÃO ==========
    def executar_transformacao(self, df_raw) -> Dict:
        """
        Executa etapa de transformação com validações.
        """
        logger.info("=" * 80)
        logger.info("🔄 ETAPA 2: TRANSFORMAÇÃO DE DADOS")
        logger.info("=" * 80)

        try:
            if df_raw is None or df_raw.empty:
                raise ValueError("DataFrame de entrada vazio")

            transformer = DataTransformer()
            dados_transformados = transformer.processar(df_raw)

            if dados_transformados is None:
                raise ValueError("Transformação retornou None")

            # Validações pós-transformação
            tabelas_esperadas = [
                'dim_favorecido', 'dim_programa', 'dim_natureza', 'dim_ug', 'fato_execucao']
            for tabela in tabelas_esperadas:
                if tabela not in dados_transformados:
                    raise ValueError(f"Tabela esperada não gerada: {tabela}")

                if dados_transformados[tabela].empty:
                    raise ValueError(
                        f"Tabela vazia após transformação: {tabela}")

            self.relatorio_final['etapas']['transformacao']['status'] = 'SUCESSO'
            self.relatorio_final['etapas']['transformacao']['dados'] = {
                'dimensoes': {
                    'favorecido': len(dados_transformados['dim_favorecido']),
                    'programa': len(dados_transformados['dim_programa']),
                    'natureza': len(dados_transformados['dim_natureza']),
                    'ug': len(dados_transformados['dim_ug'])
                },
                'fato': len(dados_transformados['fato_execucao']),
                'relatorio': transformer.relatorio_transformacao
            }

            logger.info("✅ Transformação concluída:")
            for tabela, dados in self.relatorio_final['etapas']['transformacao']['dados']['dimensoes'].items():
                logger.info(f"   - dim_{tabela}: {dados} registros")
            logger.info(
                f"   - fato_execucao: {self.relatorio_final['etapas']['transformacao']['dados']['fato']} registros")

            return dados_transformados

        except Exception as e:
            logger.error(f"❌ Erro na transformação: {e}")
            self.relatorio_final['etapas']['transformacao']['status'] = 'ERRO'
            self.relatorio_final['etapas']['transformacao']['erros'].append(
                str(e))
            return None

    # ========== ETAPA 3: CARGA ==========
    def executar_carga(self, dados_transformados) -> bool:
        """
        Executa etapa de carga com validações.
        """
        logger.info("=" * 80)
        logger.info("🔄 ETAPA 3: CARGA NO BANCO DE DADOS")
        logger.info("=" * 80)

        try:
            if dados_transformados is None or len(dados_transformados) == 0:
                raise ValueError("Dados transformados vazios")

            loader = DataLoader()
            loader.carregar_mysql(dados_transformados)

            self.relatorio_final['etapas']['carga']['status'] = 'SUCESSO'
            self.relatorio_final['etapas']['carga']['dados'] = {
                'audit_log': loader.audit_log
            }

            logger.info("✅ Carga concluída com sucesso:")
            logger.info(f"📊 Auditoria: {loader.audit_log}")

            return True

        except Exception as e:
            logger.error(f"❌ Erro na carga: {e}")
            self.relatorio_final['etapas']['carga']['status'] = 'ERRO'
            self.relatorio_final['etapas']['carga']['erros'].append(str(e))
            return False

    # ========== VALIDAÇÃO FINAL ==========
    def validar_sucesso(self) -> bool:
        """
        Valida se todas as etapas foram bem-sucedidas.
        """
        etapas = self.relatorio_final['etapas']
        sucesso = all(etapa['status'] ==
                      'SUCESSO' for etapa in etapas.values())
        return sucesso

    # ========== GERAR RELATÓRIO FINAL ==========
    def gerar_relatorio_final(self):
        """
        Gera relatório final do ETL em JSON.
        """
        self.relatorio_final['timestamp_fim'] = datetime.now().isoformat()

        if self.validar_sucesso():
            self.relatorio_final['status_geral'] = 'SUCESSO'
        else:
            self.relatorio_final['status_geral'] = 'FALHA'

        # Salvar relatório em arquivo JSON
        nome_relatorio = f"logs/etl_relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(nome_relatorio, 'w', encoding='utf-8') as f:
                json.dump(self.relatorio_final, f,
                          indent=2, ensure_ascii=False)

            logger.info(f"📄 Relatório salvo: {nome_relatorio}")

        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {e}")

        return self.relatorio_final

    # ========== EXECUTAR PIPELINE COMPLETO ==========
    def executar(self, usar_backup_local: bool = False):
        """
        Executa o pipeline ETL completo.
        """
        inicio_tempo = datetime.now()
        logger.info("🚀 INICIANDO PIPELINE ETL COMPLETO")

        try:
            # Etapa 1: Extração
            df_raw = self.executar_extracao(
                usar_backup_local=usar_backup_local)
            if df_raw is None:
                raise Exception("Extração falhou. Pipeline abortado.")

            # Etapa 2: Transformação
            dados_transformados = self.executar_transformacao(df_raw)
            if dados_transformados is None:
                raise Exception("Transformação falhou. Pipeline abortado.")

            # Etapa 3: Carga
            sucesso_carga = self.executar_carga(dados_transformados)
            if not sucesso_carga:
                raise Exception("Carga falhou. Pipeline abortado.")

            # Relatório Final
            relatorio = self.gerar_relatorio_final()

            # Tempo total
            tempo_total = (datetime.now() - inicio_tempo).total_seconds()
            self.relatorio_final['tempo_total'] = tempo_total

            logger.info("=" * 80)
            if self.validar_sucesso():
                logger.info("✅ PIPELINE ETL EXECUTADO COM SUCESSO!")
                logger.info(f"⏱️ Tempo total: {tempo_total:.2f}s")
                logger.info("=" * 80)
                return True
            else:
                logger.error("❌ PIPELINE FINALIZADO COM ERROS")
                logger.error("=" * 80)
                return False

        except Exception as e:
            logger.error(f"❌ ERRO CRÍTICO NO PIPELINE: {e}")
            self.gerar_relatorio_final()
            return False


def main():
    """
    Função principal do ETL.
    """
    # Verificar argumentos da linha de comando
    usar_backup = '--backup' in sys.argv

    if usar_backup:
        logger.info("⚠️ Modo BACKUP LOCAL ativado")
    else:
        logger.info(
            "ℹ️ Modo EXTRAÇÃO DA API ativado (use --backup para usar dados locais)")

    # Executar pipeline
    orchestrator = ETLOrchestrator()
    sucesso = orchestrator.executar(usar_backup_local=usar_backup)

    sys.exit(0 if sucesso else 1)


if __name__ == "__main__":
    main()
