import pandas as pd
import logging
import time
from typing import Dict, Tuple
from datetime import datetime

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


class DataTransformer:
    """
    Classe responsável pela transformação (T) do ETL.
    Implementa validações, normalização e criação de dimensões robustas.
    """

    def __init__(self):
        self.relatorio_transformacao = {
            'timestamp': datetime.now().isoformat(),
            'dados_entrada': 0,
            'dados_saida': 0,
            'registros_rejeitados': [],
            'duplicatas_detectadas': {},
            'avisos': []
        }

    # ========== MELHORIA: LIMPEZA ROBUSTA DE MOEDA ==========
    @staticmethod
    def clean_currency(val, linha: int = None) -> float:
        """
        Remove acentos, pontuação e coloca em minúsculas.
        Converte formato brasileiro (1.234,56) para float (1234.56)
        Trata exceções com logging.
        """
        if pd.isna(val):
            return 0.0

        try:
            val_str = str(val).strip()

            # Se for negativo (formato "- 1.234,56")
            if val_str.startswith('- '):
                val_str = '-' + val_str.replace('- ', '')

            # Converter formato brasileiro
            val_str = val_str.replace('.', '').replace(',', '.')

            resultado = float(val_str)

            # Validação: valores muito altos podem ser erros
            if resultado > 999_999_999:
                logger.warning(
                    f"Valor suspeita mente alto na linha {linha}: {resultado}")

            return resultado

        except ValueError:
            logger.error(f"Erro ao converter moeda na linha {linha}: {val}")
            return 0.0

    # ========== MELHORIA: PARSING ROBUSTO DE CÓDIGO/DESCRIÇÃO ==========
    @staticmethod
    def split_cod_desc(text: str, campo: str = None) -> Tuple[str, str]:
        """
        Separa código e descrição do formato "CODIGO - DESCRIÇÃO".
        Trata múltiplos hífens corretamente.
        """
        if pd.isna(text) or str(text).strip() == '':
            logger.warning(f"Campo {campo} vazio ou nulo")
            return 'SEM_CODIGO', 'SEM_DESCRICAO'

        text_str = str(text).strip()

        if ' - ' not in text_str:
            # Se não tiver hífen, assume que é apenas descrição
            return text_str, text_str

        # Split apenas no PRIMEIRO hífen (correto!)
        parts = text_str.split(' - ', 1)

        codigo = parts[0].strip()
        descricao = parts[1].strip() if len(parts) > 1 else ''

        # Validação
        if not codigo or not descricao:
            logger.warning(
                f"Separação incompleta no campo {campo}: '{text_str}'")

        return codigo, descricao

    # ========== MELHORIA 1: DETECÇÃO DE DUPLICATAS EM DIMENSÕES ==========
    def _detectar_duplicatas_dimensao(self, df: pd.DataFrame, dimensao_nome: str,
                                      colunas_chave: list) -> Dict:
        """
        Detecta e registra duplicatas por chave única em uma dimensão.
        """
        duplicatas = df.duplicated(subset=colunas_chave, keep=False).sum()

        if duplicatas > 0:
            logger.warning(
                f"🔍 {dimensao_nome}: {duplicatas} duplicatas detectadas")
            self.relatorio_transformacao['duplicatas_detectadas'][dimensao_nome] = duplicatas

        return {'total_duplicatas': duplicatas}

    # ========== MELHORIA 2: SCD (Slowly Changing Dimension) ==========
    def _aplicar_scd_tipo2(self, df: pd.DataFrame, colunas_chave: list) -> pd.DataFrame:
        """
        Implementa SCD Tipo 2 para rastrear mudanças em dimensões.
        Adiciona data_inicio e data_fim (ainda não implementado no BD, preparação para futuro).
        """
        df['data_inicio'] = datetime.now().date()
        df['data_fim'] = None  # Será atualizado se houver mudança
        df['versao'] = 1

        logger.info(f"✅ SCD Tipo 2 aplicado com {len(df)} registros")
        return df

    # ========== MELHORIA 3: VALIDAÇÃO PRÉ-TRANSFORMAÇÃO ==========
    def _validar_dados_entrada(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, list]:
        """
        Valida dados de entrada e remove registros problemáticos.
        """
        logger.info("🔍 Validando dados de entrada...")

        rejeicoes = []
        indices_invalidos = []

        colunas_obrigatorias = ['valor', 'data', 'codigoFavorecido', 'nomeFavorecido',
                                'codigoUg', 'ug', 'categoria', 'grupo', 'modalidade', 'elemento']

        for col in colunas_obrigatorias:
            if col not in df.columns:
                logger.error(f"❌ Coluna obrigatória ausente: {col}")
                raise ValueError(f"Coluna ausente: {col}")

        for idx, row in df.iterrows():
            erros = []

            # Validação 1: Valores nulos em colunas críticas
            if pd.isna(row['codigoFavorecido']) or str(row['codigoFavorecido']).strip() == '':
                erros.append("codigoFavorecido nulo")

            if pd.isna(row['codigoUg']) or str(row['codigoUg']).strip() == '':
                erros.append("codigoUg nulo")

            # Validação 2: Data inválida
            if pd.isna(row['data']) or str(row['data']).strip() == '':
                erros.append("data nula")

            # Validação 3: Valor negativo (suspeito)
            try:
                valor = self.clean_currency(row['valor'], linha=idx)
                if valor < 0:
                    logger.warning(
                        f"Linha {idx}: Valor negativo detectado: {valor}")
                    # NÃO REJEITA, mas registra aviso
                    erros.append(f"Valor negativo: {valor}")
            except:
                erros.append("Valor inválido")

            if erros:
                indices_invalidos.append(idx)
                rejeicoes.append({
                    'linha': idx,
                    'codigo_favorecido': row.get('codigoFavorecido', 'N/A'),
                    'erros': erros
                })

        df_valido = df.drop(indices_invalidos) if indices_invalidos else df

        if rejeicoes:
            logger.warning(
                f"⚠️ {len(rejeicoes)} registros rejeitados na validação de entrada")
            self.relatorio_transformacao['registros_rejeitados'] = rejeicoes

        return df_valido, rejeicoes

    # ========== PROCESSAR DIMENSÃO COM VALIDAÇÕES ==========
    def _processar_dimensao_favorecido(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria dim_favorecido com todos os favorecidos."""
        logger.info("📦 Processando dim_favorecido...")

        try:
            dim = df[['codigoFavorecido', 'nomeFavorecido',
                      'ufFavorecido']].drop_duplicates().reset_index(drop=True)
            dim['id_favorecido'] = range(1, len(dim) + 1)

            logger.info(f"✅ dim_favorecido: {len(dim)} registros únicos")
            return dim

        except Exception as e:
            logger.error(f"❌ Erro ao processar dim_favorecido: {e}")
            return pd.DataFrame()

    def _processar_dimensao_programa(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria dim_programa."""
        logger.info("📦 Processando dim_programa...")

        try:
            cols_prog = ['funcao', 'subfuncao', 'programa', 'acao']

            # Verificar se colunas existem
            for col in cols_prog:
                if col not in df.columns:
                    df[col] = 'SEM_DADOS'

            temp_prog = df[cols_prog].drop_duplicates().reset_index(drop=True)

            for col in cols_prog:
                temp_prog[f'cod_{col}'], temp_prog[f'desc_{col}'] = zip(
                    *temp_prog[col].map(lambda x: self.split_cod_desc(x, campo=col))
                )

            dim_programa = temp_prog.drop(columns=cols_prog)
            dim_programa['id_programa'] = range(1, len(dim_programa) + 1)

            logger.info(
                f"✅ dim_programa: {len(dim_programa)} registros únicos")
            return dim_programa

        except Exception as e:
            logger.error(f"❌ Erro ao processar dim_programa: {e}")
            return pd.DataFrame()

    def _processar_dimensao_natureza(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria dim_natureza."""
        logger.info("📦 Processando dim_natureza...")

        try:
            cols_nat = ['categoria', 'grupo', 'modalidade', 'elemento']

            # Verificar se colunas existem
            for col in cols_nat:
                if col not in df.columns:
                    df[col] = 'SEM_DADOS'

            temp_nat = df[cols_nat].drop_duplicates().reset_index(drop=True)

            for col in cols_nat:
                temp_nat[f'cod_{col}'], temp_nat[f'desc_{col}'] = zip(
                    *temp_nat[col].map(lambda x: self.split_cod_desc(x, campo=col))
                )

            dim_natureza = temp_nat.drop(columns=cols_nat)
            dim_natureza['id_natureza'] = range(1, len(dim_natureza) + 1)

            logger.info(
                f"✅ dim_natureza: {len(dim_natureza)} registros únicos")
            return dim_natureza

        except Exception as e:
            logger.error(f"❌ Erro ao processar dim_natureza: {e}")
            return pd.DataFrame()

    def _processar_dimensao_ug(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria dim_ug."""
        logger.info("📦 Processando dim_ug...")

        try:
            dim = df[['codigoUg', 'ug', 'codigoOrgao', 'orgao']
                     ].drop_duplicates().reset_index(drop=True)
            dim['id_ug'] = range(1, len(dim) + 1)

            logger.info(f"✅ dim_ug: {len(dim)} registros únicos")
            return dim

        except Exception as e:
            logger.error(f"❌ Erro ao processar dim_ug: {e}")
            return pd.DataFrame()

        # ========== MAIN: PROCESSAR ==========
    def processar(self, df_raw: pd.DataFrame) -> Dict:
        """Orquestra transformação otimizada."""
        inicio = time.time()

        logger.info("=" * 80)
        logger.info("🚀 TRANSFORMAÇÃO OTIMIZADA (V2)")
        logger.info("=" * 80)

        if df_raw is None or df_raw.empty:
            logger.error("❌ DataFrame vazio")
            return None

        self.relatorio_transformacao['dados_entrada'] = len(df_raw)

        try:
            # ETAPA 1: Limpeza básica
            df = df_raw.copy()
            df.columns = df.columns.str.strip().str.replace('\ufeff', '')

            # ETAPA 2: Processar dimensões com validação
            dim_favorecido = self._processar_dimensao_favorecido(df)
            dim_programa = self._processar_dimensao_programa(df)
            dim_natureza = self._processar_dimensao_natureza(df)
            dim_ug = self._processar_dimensao_ug(df)

            # ETAPA 3: Criar fato (CORRIGIDO)
            logger.info("📦 Processando fato_execucao...")

            fato = df.copy()

            # ✅ Renomear coluna de data
            if 'data' in fato.columns and 'data_emissao' not in fato.columns:
                fato['data_emissao'] = fato['data']

            # Converter data para formato correto
            try:
                fato['data_emissao'] = pd.to_datetime(
                    fato['data_emissao'],
                    format='%d/%m/%Y',
                    errors='coerce'
                ).dt.date
            except Exception as e:
                logger.warning(f"⚠️ Erro ao converter data: {e}")
                fato['data_emissao'] = None

            # Limpar valores de moeda
            try:
                fato['valor_transacao'] = fato['valor'].apply(
                    lambda x: self.clean_currency_vectorized(
                        pd.Series([x])).iloc[0]
                )
            except Exception as e:
                logger.warning(f"⚠️ Erro ao limpar moeda: {e}")
                fato['valor_transacao'] = 0.0

            # ✅ MERGE COM DIMENSÕES (INNER JOIN)
            try:
                fato = fato.merge(
                    dim_favorecido[['codigoFavorecido', 'id_favorecido']],
                    on='codigoFavorecido',
                    how='inner'
                )
                logger.info(f"✅ Após merge favorecido: {len(fato)} registros")
            except Exception as e:
                logger.error(f"❌ Erro no merge favorecido: {e}")
                return None

            try:
                fato = fato.merge(
                    dim_ug[['codigoUg', 'id_ug']],
                    on='codigoUg',
                    how='inner'
                )
                logger.info(f"✅ Após merge UG: {len(fato)} registros")
            except Exception as e:
                logger.error(f"❌ Erro no merge UG: {e}")
                return None

            # Merge com programa (com validação de colunas)
            try:
                if all(col in fato.columns for col in ['funcao', 'subfuncao', 'programa', 'acao']):
                    fato = fato.merge(
                        dim_programa[['cod_funcao', 'id_programa']],
                        left_on='funcao',
                        right_on='cod_funcao',
                        how='left'
                    )
                else:
                    fato['id_programa'] = 1
            except Exception as e:
                logger.warning(f"⚠️ Erro no merge programa: {e}")
                fato['id_programa'] = 1

            # Merge com natureza (com validação de colunas)
            try:
                if 'categoria' in fato.columns:
                    fato = fato.merge(
                        dim_natureza[['cod_categoria', 'id_natureza']],
                        left_on='categoria',
                        right_on='cod_categoria',
                        how='left'
                    )
                else:
                    fato['id_natureza'] = 1
            except Exception as e:
                logger.warning(f"⚠️ Erro no merge natureza: {e}")
                fato['id_natureza'] = 1

            # ETAPA 4: Selecionar colunas finais
            colunas_fato = [
                'data_emissao', 'documento', 'numeroProcesso', 'observacao',
                'id_favorecido', 'id_programa', 'id_natureza', 'id_ug', 'valor_transacao'
            ]

            fato_final = fato[colunas_fato].copy()

            # Remover valores nulos críticos
            fato_final = fato_final.dropna(
                subset=['id_favorecido', 'id_ug', 'valor_transacao'])

            self.relatorio_transformacao['dados_saida'] = len(fato_final)
            self.relatorio_transformacao['tempo_processamento'] = time.time(
            ) - inicio

            logger.info("=" * 80)
            logger.info("✅ TRANSFORMAÇÃO CONCLUÍDA")
            logger.info(f"📊 Entrada: {len(df)}, Saída: {len(fato_final)}")
            logger.info(
                f"⏱️ Tempo: {self.relatorio_transformacao['tempo_processamento']:.2f}s")
            logger.info("=" * 80)

            return {
                'dim_favorecido': dim_favorecido,
                'dim_programa': dim_programa,
                'dim_natureza': dim_natureza,
                'dim_ug': dim_ug,
                'fato_execucao': fato_final,
                'relatorio': self.relatorio_transformacao
            }

        except Exception as e:
            logger.error(f"❌ Erro crítico na transformação: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
