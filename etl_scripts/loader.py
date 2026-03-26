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
        logger.info("🏗️ Criando/Validando schema com constraints...")

        sql_schema = """
        -- Dimensões (sem FK)
        CREATE TABLE IF NOT EXISTS dim_favorecido (
            id_favorecido INT PRIMARY KEY AUTO_INCREMENT,
            codigoFavorecido VARCHAR(50) NOT NULL UNIQUE,
            nomeFavorecido VARCHAR(255) NOT NULL,
            ufFavorecido VARCHAR(2),
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_codigo (codigoFavorecido),
            INDEX idx_nome (nomeFavorecido)
        ) ENGINE=InnoDB;

        CREATE TABLE IF NOT EXISTS dim_programa (
            id_programa INT PRIMARY KEY AUTO_INCREMENT,
            cod_funcao VARCHAR(50),
            desc_funcao VARCHAR(255),
            cod_subfuncao VARCHAR(50),
            desc_subfuncao VARCHAR(255),
            cod_programa VARCHAR(50),
            desc_programa VARCHAR(255),
            cod_acao VARCHAR(50),
            desc_acao VARCHAR(255),
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_desc_programa (desc_programa)
        ) ENGINE=InnoDB;

        CREATE TABLE IF NOT EXISTS dim_natureza (
            id_natureza INT PRIMARY KEY AUTO_INCREMENT,
            cod_categoria VARCHAR(50),
            desc_categoria VARCHAR(255),
            cod_grupo VARCHAR(50),
            desc_grupo VARCHAR(255),
            cod_modalidade VARCHAR(50),
            desc_modalidade VARCHAR(255),
            cod_elemento VARCHAR(50),
            desc_elemento VARCHAR(255),
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_desc_elemento (desc_elemento)
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
        Carrega dimensão com deduplicação e detecção de duplicatas.
        Retorna (inseridos, atualizados, rejeitados)
        """
        logger.info(f"⏳ Carregando {nome_tabela}...")

        inseridos = 0
        atualizados = 0
        rejeitados = 0
        rejeicoes = []

        with self.engine.connect() as conn:
            # RECOMENDAÇÃO 7: Validar dados antes de carregar
            df_valido, rejeicoes = self._validar_dados(
                df, nome_tabela, chave_unica)
            rejeitados = len(rejeicoes)

            if rejeicoes:
                logger.warning(
                    f"⚠️ {rejeitados} registros rejeitados em {nome_tabela}")
                self.audit_log['avisos'].append({
                    'tabela': nome_tabela,
                    'quantidade': rejeitados,
                    'motivos': rejeicoes[:5]  # Log dos primeiros 5
                })

            # Carregar dados válidos com UPSERT
            for _, row in df_valido.iterrows():
                chave_valor = row[chave_unica]

                # Verifica se já existe
                query = f"SELECT id_{nome_tabela.replace('dim_', '')} FROM {nome_tabela} WHERE {chave_unica} = %s"

                try:
                    result = pd.read_sql(
                        query, self.engine, params=[chave_valor])

                    if not result.empty:
                        # Atualizar
                        cols_update = ', '.join(
                            [f"`{col}` = %s" for col in df_valido.columns if col != chave_unica])
                        valores = list(
                            row[df_valido.columns != chave_unica].values) + [chave_valor]

                        update_sql = f"UPDATE {nome_tabela} SET {cols_update} WHERE {chave_unica} = %s"
                        with self.engine.begin() as conn:
                            conn.execute(text(update_sql), valores)
                        atualizados += 1
                    else:
                        # Inserir
                        row.to_sql(nome_tabela, con=self.engine,
                                   if_exists='append', index=False)
                        inseridos += 1

                except Exception as e:
                    logger.error(f"Erro ao processar {nome_tabela}: {e}")
                    rejeitados += 1

        logger.info(
            f"✅ {nome_tabela}: {inseridos} inseridos, {atualizados} atualizados, {rejeitados} rejeitados")
        return inseridos, atualizados, rejeitados

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
                f"⚠️ Validação: {len(rejeicoes)} registros rejeitados em {tabela}")

        return df_valido, rejeicoes

    # ========== RECOMENDAÇÃO 8: VERIFICAR INTEGRIDADE REFERENCIAL ==========
    def _validar_chaves_estrangeiras(self, fato_df: pd.DataFrame) -> pd.DataFrame:
        """
        Valida que todos os IDs das FK existem nas dimensões.
        Remove registros órfãos.
        """
        logger.info("🔍 Validando integridade referencial...")

        orfaos_removidos = 0
        indices_invalidos = []

        for idx, row in fato_df.iterrows():
            # Validar cada FK
            validacoes = [
                (row['id_favorecido'], 'dim_favorecido', 'id_favorecido'),
                (row['id_programa'], 'dim_programa', 'id_programa'),
                (row['id_natureza'], 'dim_natureza', 'id_natureza'),
                (row['id_ug'], 'dim_ug', 'id_ug'),
            ]

            for id_valor, tabela, coluna in validacoes:
                query = f"SELECT COUNT(*) as cnt FROM {tabela} WHERE {coluna} = {int(id_valor)}"
                try:
                    result = pd.read_sql(query, self.engine)
                    if result['cnt'].iloc[0] == 0:
                        logger.warning(
                            f"FK órfã em fato_execucao: {tabela}.{coluna}={id_valor}")
                        indices_invalidos.append(idx)
                        orfaos_removidos += 1
                        break
                except Exception as e:
                    logger.error(f"Erro ao validar FK: {e}")

        if indices_invalidos:
            fato_df = fato_df.drop(indices_invalidos)
            logger.info(
                f"⚠️ {orfaos_removidos} registros órfãos removidos da fato")

        return fato_df

    # ========== RECOMENDAÇÃO 9: INCREMENTALISMO ==========
    def _carregar_incrementalmente(self, fato_df: pd.DataFrame) -> int:
        """
        Carrega apenas novos registros (baseado em data e documento).
        Evita duplicatas.
        """
        logger.info("📈 Carregando de forma incremental...")

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
                f"📊 Dados novos desde {max_data_db}: {len(fato_novo)} registros")
        else:
            fato_novo = fato_df
            logger.info(f"📊 Primeira carga: {len(fato_novo)} registros")

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
                    f"✅ Batch {i//batch_size + 1}: {len(batch)} registros inseridos")

        return inseridos

    # ========== RECOMENDAÇÃO 5: ADICIONAR ÍNDICES ==========
    def _criar_indices_performance(self):
        """Cria índices para melhorar performance de queries."""
        logger.info("🚀 Criando índices de performance...")

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
                    logger.info(f"✅ Índice criado: {sql[:50]}...")
                except Exception as e:
                    logger.warning(f"Índice pode já existir: {e}")
            conn.commit()

    # ========== RECOMENDAÇÃO 10: DATA QUALITY CHECKS ==========
    def _gerar_relatorio_qualidade(self) -> Dict:
        """Gera relatório de qualidade dos dados carregados."""
        logger.info("📋 Gerando relatório de qualidade dos dados...")

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

        logger.info(f"✅ Relatório de qualidade: {relatorio}")
        return relatorio

    # ========== MAIN: ORQUESTRADOR ==========
    def carregar_mysql(self, dados_transformados):
        """
        Orquestra todo o processo de carga com as 10 melhorias implementadas.
        """
        if not dados_transformados:
            logger.error("❌ Dados transformados vazios!")
            return

        try:
            logger.info("=" * 80)
            logger.info("🚀 INICIANDO CARGA COM VALIDAÇÕES E MELHORIAS")
            logger.info("=" * 80)

            # CRÍTICO 1: Criar schema com constraints
            self._criar_tabelas_com_constraints()

            # CRÍTICO 2: Carregar dimensões com deduplicação
            dim_tabelas = [
                ('dim_favorecido',
                 dados_transformados['dim_favorecido'], 'codigoFavorecido'),
                ('dim_programa',
                 dados_transformados['dim_programa'], 'cod_funcao'),
                ('dim_natureza',
                 dados_transformados['dim_natureza'], 'cod_categoria'),
                ('dim_ug', dados_transformados['dim_ug'], 'codigoUg'),
            ]

            for nome_tab, df, chave in dim_tabelas:
                ins, atu, rej = self._carregar_dimensao_com_dedup(
                    nome_tab, df, chave)
                self.audit_log['tabelas_processadas'][nome_tab] = {
                    'inseridos': ins,
                    'atualizados': atu,
                    'rejeitados': rej
                }

            # CRÍTICO 3: Validar integridade referencial
            fato_df = dados_transformados['fato_execucao'].copy()
            fato_df = self._validar_chaves_estrangeiras(fato_df)

            # RECOMENDAÇÃO 9: Carregar incrementalmente
            inseridos_fato = self._carregar_incrementalmente(fato_df)
            self.audit_log['tabelas_processadas']['fato_execucao'] = {
                'inseridos': inseridos_fato,
                'atualizados': 0,
                'rejeitados': len(dados_transformados['fato_execucao']) - inseridos_fato
            }

            # RECOMENDAÇÃO 5: Criar índices
            self._criar_indices_performance()

            # RECOMENDAÇÃO 10: Gerar relatório de qualidade
            relatorio_qualidade = self._gerar_relatorio_qualidade()
            self.audit_log['relatorio_qualidade'] = relatorio_qualidade

            # RECOMENDAÇÃO 6: Registrar auditoria
            self._registrar_auditoria()

            logger.info("=" * 80)
            logger.info("✅ CARGA CONCLUÍDA COM SUCESSO!")
            logger.info("=" * 80)
            logger.info(f"📊 Resumo: {self.audit_log}")

        except Exception as e:
            logger.error(f"❌ Erro crítico na carga: {e}")
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
        logger.info("📝 Registrando auditoria...")

        for tabela, stats in self.audit_log.get('tabelas_processadas', {}).items():
            sql = """
            INSERT INTO etl_auditoria 
            (timestamp_execucao, tabela_nome, registros_inseridos, registros_atualizados, 
             registros_rejeitados, motivo_rejeicao, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            try:
                with self.engine.begin() as conn:
                    conn.execute(
                        text(sql),
                        [
                            datetime.now(),
                            tabela,
                            stats.get('inseridos', 0),
                            stats.get('atualizados', 0),
                            stats.get('rejeitados', 0),
                            motivo or 'N/A',
                            status
                        ]
                    )
            except Exception as e:
                logger.error(f"Erro ao registrar auditoria: {e}")
