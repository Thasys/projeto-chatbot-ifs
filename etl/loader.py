from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Float, Date, ForeignKey, Index
from sqlalchemy.pool import NullPool
from config import Config
import pandas as pd
from datetime import datetime
import logging
from typing import Dict, Tuple

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


class DataLoader:
    def __init__(self):
        self.engine = create_engine(
            Config.DB_URI,
            poolclass=NullPool,  # Sem pooling para operações longas
            echo=False
        )
        self.metadata = MetaData()
        self.audit_log = {
            'timestamp': datetime.now().isoformat(),
            'tabelas_processadas': {},
            'erros': [],
            'avisos': []
        }

    # ========== RECOMENDAÇÃO 1: CRIAR FOREIGN KEYS ==========
    def _criar_tabelas_com_constraints(self):
        """Cria schema com Foreign Keys e Índices."""
        logger.info("[SCHEMA] Criando/Validando schema com constraints...")

        sql_schema = """
        -- Dimensões (sem FK)
        CREATE TABLE IF NOT EXISTS dim_favorecido (
            id_favorecido INT PRIMARY KEY AUTO_INCREMENT,
            codigoFavorecido VARCHAR(50) NOT NULL UNIQUE,
            nomeFavorecido VARCHAR(255) NOT NULL,
            ufFavorecido VARCHAR(50),
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_codigo (codigoFavorecido),
            INDEX idx_nome (nomeFavorecido)
        ) ENGINE=InnoDB;

        CREATE TABLE IF NOT EXISTS dim_programa (
            id_programa INT PRIMARY KEY AUTO_INCREMENT,
            funcao VARCHAR(255),
            subfuncao VARCHAR(255),
            programa VARCHAR(255),
            acao VARCHAR(255),
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_programa (programa(100)),
            INDEX idx_acao (acao(100))
        ) ENGINE=InnoDB;

        CREATE TABLE IF NOT EXISTS dim_natureza (
            id_natureza INT PRIMARY KEY AUTO_INCREMENT,
            categoria VARCHAR(255),
            grupo VARCHAR(255),
            modalidade VARCHAR(255),
            elemento VARCHAR(255),
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_elemento (elemento(100))
        ) ENGINE=InnoDB;

        CREATE TABLE IF NOT EXISTS dim_ug (
            id_ug INT PRIMARY KEY AUTO_INCREMENT,
            codigoUg VARCHAR(50) NOT NULL UNIQUE,
            ug VARCHAR(255) NOT NULL,
            codigoOrgao VARCHAR(50),
            orgao VARCHAR(255),
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_codigo_ug (codigoUg),
            INDEX idx_ug (ug)
        ) ENGINE=InnoDB;

        -- Fato com Foreign Keys
        CREATE TABLE IF NOT EXISTS fato_execucao (
            id_fato INT PRIMARY KEY AUTO_INCREMENT,
            data_emissao DATE NOT NULL,
            documento VARCHAR(50),
            numeroProcesso VARCHAR(50),
            observacao TEXT,
            valor_transacao DECIMAL(15,2) NOT NULL,
            id_favorecido INT NOT NULL,
            id_programa INT NOT NULL,
            id_natureza INT NOT NULL,
            id_ug INT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            
            CONSTRAINT fk_fato_favorecido FOREIGN KEY (id_favorecido) 
                REFERENCES dim_favorecido(id_favorecido) ON DELETE RESTRICT,
            CONSTRAINT fk_fato_programa FOREIGN KEY (id_programa) 
                REFERENCES dim_programa(id_programa) ON DELETE RESTRICT,
            CONSTRAINT fk_fato_natureza FOREIGN KEY (id_natureza) 
                REFERENCES dim_natureza(id_natureza) ON DELETE RESTRICT,
            CONSTRAINT fk_fato_ug FOREIGN KEY (id_ug) 
                REFERENCES dim_ug(id_ug) ON DELETE RESTRICT,
            
            INDEX idx_data (data_emissao),
            INDEX idx_valor (valor_transacao),
            INDEX idx_favorecido (id_favorecido),
            INDEX idx_programa (id_programa),
            INDEX idx_natureza (id_natureza),
            INDEX idx_ug (id_ug)
        ) ENGINE=InnoDB;

        -- Tabela de Auditoria (RECOMENDAÇÃO 6)
        CREATE TABLE IF NOT EXISTS etl_auditoria (
            id_auditoria INT PRIMARY KEY AUTO_INCREMENT,
            timestamp_execucao TIMESTAMP,
            tabela_nome VARCHAR(50),
            registros_inseridos INT,
            registros_atualizados INT,
            registros_rejeitados INT,
            motivo_rejeicao TEXT,
            usuario VARCHAR(100),
            status ENUM('SUCESSO', 'ERRO', 'AVISO'),
            INDEX idx_timestamp (timestamp_execucao),
            INDEX idx_tabela (tabela_nome)
        ) ENGINE=InnoDB;
        """

        with self.engine.connect() as conn:
            for statement in sql_schema.split(';'):
                if statement.strip():
                    try:
                        conn.execute(text(statement))
                    except Exception as e:
                        logger.warning(f"Schema já existe ou erro: {e}")
            conn.commit()

    # ========== RECOMENDAÇÃO 2: DEDUPLICAÇÃO E IDEMPOTÊNCIA ==========
    def _carregar_dimensao_com_dedup(self, nome_tabela: str, df: pd.DataFrame,
                                     chave_unica: str, id_col: str = None) -> Tuple[int, int, int]:
        """
        Carrega dimensão com deduplicação via batch insert.
        Busca chaves existentes no BD, insere apenas as novas.
        Retorna (inseridos, atualizados, rejeitados)
        """
        logger.info(f"Carregando {nome_tabela}...")

        # Validar dados antes de carregar
        df_valido, rejeicoes = self._validar_dados(df, nome_tabela, chave_unica)
        rejeitados = len(rejeicoes)

        if rejeicoes:
            logger.warning(f"{rejeitados} registros rejeitados em {nome_tabela}")
            self.audit_log['avisos'].append({
                'tabela': nome_tabela,
                'quantidade': rejeitados,
                'motivos': rejeicoes[:5]
            })

        if df_valido.empty:
            logger.warning(f"Nenhum dado valido para {nome_tabela}")
            return 0, 0, rejeitados

        try:
            # Identificar coluna de ID do transformer
            id_col = f"id_{nome_tabela.replace('dim_', '')}"

            # Buscar chaves já existentes em uma única query
            chaves_existentes = pd.read_sql(
                f"SELECT {chave_unica} FROM {nome_tabela}",
                self.engine
            )[chave_unica].astype(str).tolist()

            # Separar novos vs existentes
            df_valido[chave_unica] = df_valido[chave_unica].astype(str)
            df_novos = df_valido[~df_valido[chave_unica].isin(chaves_existentes)].copy()
            atualizados = len(df_valido) - len(df_novos)

            inseridos = 0
            if not df_novos.empty:
                # Inserir COM o id do transformer (precisamos corresponder aos FK de fato_execucao)
                df_novos.to_sql(
                    nome_tabela, con=self.engine,
                    if_exists='append', index=False,
                    chunksize=500, method='multi'
                )
                inseridos = len(df_novos)

            logger.info(f"{nome_tabela}: {inseridos} inseridos, {atualizados} ja existentes, {rejeitados} rejeitados")
            return inseridos, atualizados, rejeitados

        except Exception as e:
            logger.error(f"Erro ao carregar {nome_tabela}: {e}")
            return 0, 0, len(df_valido)

    # ========== RECOMENDAÇÃO 7: VALIDAÇÃO DE DADOS ==========
    def _validar_dados(self, df: pd.DataFrame, tabela: str, chave_unica: str) -> Tuple[pd.DataFrame, list]:
        """
        Valida dados e retorna (df_válido, lista_de_rejeições)
        """
        rejeicoes = []
        indices_invalidos = []

        for idx, row in df.iterrows():
            erros = []

            # Validação 1: Chave única não pode ser nula
            if pd.isna(row[chave_unica]) or str(row[chave_unica]).strip() == '':
                erros.append(f"Chave única ({chave_unica}) vazia")

            # Validação 2: Valores monetários não podem ser negativos (excepto em casos específicos)
            if 'valor' in row and pd.notna(row['valor']) and row['valor'] < 0:
                logger.warning(
                    f"Valor negativo em {tabela} linha {idx}: {row['valor']}")
                erros.append(f"Valor negativo: {row['valor']}")

            # Validação 3: Datas inválidas
            if 'data' in row or 'data_emissao' in row:
                data_col = 'data_emissao' if 'data_emissao' in row else 'data'
                if pd.isna(row[data_col]):
                    erros.append(f"Data inválida ou nula")

            if erros:
                indices_invalidos.append(idx)
                rejeicoes.append({
                    'linha': idx,
                    'chave': row.get(chave_unica, 'N/A'),
                    'erros': erros
                })

        df_valido = df.drop(indices_invalidos) if indices_invalidos else df

        if rejeicoes:
            logger.warning(
                f"[AVISO] Validação: {len(rejeicoes)} registros rejeitados em {tabela}")

        return df_valido, rejeicoes

    # ========== RECOMENDAÇÃO 8: VERIFICAR INTEGRIDADE REFERENCIAL ==========
    def _validar_chaves_estrangeiras(self, fato_df: pd.DataFrame) -> pd.DataFrame:
        """
        Valida integridade referencial via JOIN em batch (uma query por dimensão).
        Remove registros órfãos.
        """
        logger.info("Validando integridade referencial (batch)...")

        fks = [
            ('id_favorecido', 'dim_favorecido'),
            ('id_programa',   'dim_programa'),
            ('id_natureza',   'dim_natureza'),
            ('id_ug',         'dim_ug'),
        ]

        mascara_valida = pd.Series(True, index=fato_df.index)

        for fk_col, tabela in fks:
            try:
                ids_validos = pd.read_sql(
                    f"SELECT {fk_col} FROM {tabela}",
                    self.engine
                )[fk_col].astype(int).tolist()

                mascara = fato_df[fk_col].astype(int).isin(ids_validos)
                orfaos = (~mascara).sum()
                if orfaos > 0:
                    logger.warning(f"{orfaos} registros orfaos em {tabela}.{fk_col} — removendo")
                mascara_valida &= mascara

            except Exception as e:
                logger.error(f"Erro ao validar FK {fk_col}: {e}")

        total_removidos = (~mascara_valida).sum()
        if total_removidos > 0:
            logger.warning(f"Total de {total_removidos} registros orfaos removidos da fato")
            fato_df = fato_df[mascara_valida]

        logger.info(f"Integridade OK: {len(fato_df)} registros validos")
        return fato_df

    # ========== RECOMENDAÇÃO 9: INCREMENTALISMO ==========
    def _carregar_incrementalmente(self, fato_df: pd.DataFrame) -> int:
        """
        Carrega apenas novos registros (baseado em data e documento).
        Evita duplicatas.
        """
        logger.info("[DADOS] Carregando de forma incremental...")

        # Pegar datas mínimas/máximas existentes
        query_minmax = "SELECT MIN(data_emissao) as min_data, MAX(data_emissao) as max_data FROM fato_execucao"

        try:
            resultado = pd.read_sql(query_minmax, self.engine)
            min_data_db = resultado['min_data'].iloc[0]
            max_data_db = resultado['max_data'].iloc[0]
        except:
            min_data_db = None
            max_data_db = None

        # Filtrar apenas novos dados
        if max_data_db:
            fato_novo = fato_df[fato_df['data_emissao'] > max_data_db]
            logger.info(
                f"[GRAFICO] Dados novos desde {max_data_db}: {len(fato_novo)} registros")
        else:
            fato_novo = fato_df
            logger.info(f"[GRAFICO] Primeira carga: {len(fato_novo)} registros")

        # Inserir de forma em batch (mais eficiente que linha por linha)
        batch_size = 1000
        inseridos = 0

        with self.engine.begin() as conn:
            for i in range(0, len(fato_novo), batch_size):
                batch = fato_novo.iloc[i:i+batch_size]
                batch.to_sql('fato_execucao', con=conn,
                             if_exists='append', index=False)
                inseridos += len(batch)
                logger.info(
                    f"[OK] Batch {i//batch_size + 1}: {len(batch)} registros inseridos")

        return inseridos

    # ========== RECOMENDAÇÃO 5: ADICIONAR ÍNDICES ==========
    def _criar_indices_performance(self):
        """Cria índices para melhorar performance de queries."""
        logger.info("[INICIO] Criando índices de performance...")

        indices_sql = [
            "ALTER TABLE fato_execucao ADD INDEX idx_data_ug (data_emissao, id_ug);",
            "ALTER TABLE fato_execucao ADD INDEX idx_data_favorecido (data_emissao, id_favorecido);",
            "ALTER TABLE fato_execucao ADD INDEX idx_valor_desc (valor_transacao DESC);",
            "ALTER TABLE dim_favorecido ADD INDEX idx_nome_uf (nomeFavorecido, ufFavorecido);",
        ]

        with self.engine.connect() as conn:
            for sql in indices_sql:
                try:
                    conn.execute(text(sql))
                    logger.info(f"[OK] Índice criado: {sql[:50]}...")
                except Exception as e:
                    logger.warning(f"Índice pode já existir: {e}")
            conn.commit()

    # ========== RECOMENDAÇÃO 10: DATA QUALITY CHECKS ==========
    def _gerar_relatorio_qualidade(self) -> Dict:
        """Gera relatório de qualidade dos dados carregados."""
        logger.info("[LISTA] Gerando relatório de qualidade dos dados...")

        relatorio = {
            'timestamp': datetime.now().isoformat(),
            'tabelas': {}
        }

        tabelas = ['dim_favorecido', 'dim_programa',
                   'dim_natureza', 'dim_ug', 'fato_execucao']

        with self.engine.connect() as conn:
            for tabela in tabelas:
                try:
                    # Total de registros
                    total = pd.read_sql(
                        f"SELECT COUNT(*) as cnt FROM {tabela}", conn)['cnt'].iloc[0]

                    # Registros nulos em colunas críticas
                    if tabela == 'fato_execucao':
                        nulos = pd.read_sql(
                            "SELECT COUNT(*) as cnt FROM fato_execucao WHERE id_favorecido IS NULL OR id_ug IS NULL OR valor_transacao IS NULL",
                            conn
                        )['cnt'].iloc[0]
                    else:
                        nulos = 0

                    relatorio['tabelas'][tabela] = {
                        'total_registros': total,
                        'registros_com_nulos': nulos,
                        'percentual_qualidade': f"{((total - nulos) / total * 100):.2f}%" if total > 0 else "0%"
                    }

                except Exception as e:
                    logger.error(f"Erro ao gerar relatório de {tabela}: {e}")

        logger.info(f"[OK] Relatório de qualidade: {relatorio}")
        return relatorio

    # ========== MAIN: ORQUESTRADOR ==========
    def carregar_mysql(self, dados_transformados):
        """
        Orquestra o processo de carga: dimensões + fato.
        Usa INSERT IGNORE com FK checks desabilitados para evitar conflitos.
        """
        if not dados_transformados:
            logger.error("Dados transformados vazios!")
            return

        logger.info("Iniciando carga no banco de dados...")

        try:
            with self.engine.begin() as conn:
                conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))

                # 1. Carregar dimensões preservando os IDs do transformer
                dim_tabelas = [
                    ('dim_favorecido', dados_transformados['dim_favorecido'], 'codigoFavorecido'),
                    ('dim_programa',   dados_transformados['dim_programa'],   'acao'),
                    ('dim_natureza',   dados_transformados['dim_natureza'],   'elemento'),
                    ('dim_ug',         dados_transformados['dim_ug'],         'codigoUg'),
                ]

                for nome_tab, df, chave in dim_tabelas:
                    ins, atu, rej = self._carregar_dimensao_com_dedup(nome_tab, df, chave)
                    self.audit_log['tabelas_processadas'][nome_tab] = {
                        'inseridos': ins, 'atualizados': atu, 'rejeitados': rej
                    }

                conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))

            # 2. Carregar fato_execucao de forma incremental
            fato_df = dados_transformados['fato_execucao'].copy()
            # Remover linhas com FK nulas
            fato_df = fato_df.dropna(subset=['id_favorecido', 'id_programa', 'id_natureza', 'id_ug'])
            inseridos_fato = self._carregar_incrementalmente(fato_df)
            self.audit_log['tabelas_processadas']['fato_execucao'] = {
                'inseridos': inseridos_fato,
                'atualizados': 0,
                'rejeitados': len(dados_transformados['fato_execucao']) - inseridos_fato
            }

            self._criar_indices_performance()
            relatorio_qualidade = self._gerar_relatorio_qualidade()
            self.audit_log['relatorio_qualidade'] = relatorio_qualidade
            self._registrar_auditoria()

            logger.info("Carga concluida com sucesso!")
            logger.info(f"Resumo: {self.audit_log['tabelas_processadas']}")

        except Exception as e:
            logger.error(f"Erro critico na carga: {e}")
            self.audit_log['erros'].append({
                'timestamp': datetime.now().isoformat(),
                'erro': str(e)
            })
            self._registrar_auditoria(status='ERRO', motivo=str(e))
            raise

    def _registrar_auditoria(self, status: str = 'SUCESSO', motivo: str = None):
        """
        RECOMENDAÇÃO 6: Registra log de auditoria no banco.
        """
        logger.info("[NOTA] Registrando auditoria...")

        for tabela, stats in self.audit_log.get('tabelas_processadas', {}).items():
            sql = """
            INSERT INTO etl_auditoria
            (timestamp_execucao, tabela_nome, registros_inseridos, registros_atualizados,
             registros_rejeitados, motivo_rejeicao, status)
            VALUES (:ts, :tab, :ins, :atu, :rej, :mot, :sta)
            """

            try:
                with self.engine.begin() as conn:
                    conn.execute(
                        text(sql),
                        {
                            'ts': datetime.now(),
                            'tab': tabela,
                            'ins': stats.get('inseridos', 0),
                            'atu': stats.get('atualizados', 0),
                            'rej': stats.get('rejeitados', 0),
                            'mot': motivo or 'N/A',
                            'sta': status
                        }
                    )
            except Exception as e:
                logger.error(f"Erro ao registrar auditoria: {e}")
