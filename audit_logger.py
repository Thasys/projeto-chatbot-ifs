"""
Módulo de Auditoria - Log de todas as interações do chatbot
Implementa P0.2: Audit Logging para Lei de Acesso à Informação (LAI)
"""

import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from db_connection import DBConnection

logger = logging.getLogger(__name__)


def create_audit_table():
    """
    Cria tabela chat_audit_log se não existir.
    Deve ser executado uma única vez durante a inicialização.
    """
    from sqlalchemy import text

    db = DBConnection()
    engine = db.get_engine()

    sql_create_table = """
    CREATE TABLE IF NOT EXISTS chat_audit_log (
      id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID único da entrada de log',
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Quando a pergunta foi feita',
      user_ip VARCHAR(45) COMMENT 'IP do usuário',
      user_id VARCHAR(100) COMMENT 'ID do usuário se autenticado',
      
      -- INPUT: Pergunta do usuário
      pergunta_original TEXT NOT NULL COMMENT 'Pergunta exata do usuário',
      
      -- PROCESSAMENTO: Dados intermediários
      json_intent JSON COMMENT 'Output do agente Data Detective',
      entidades_detectadas JSON COMMENT 'Entidades identificadas na pergunta',
      sql_executado TEXT COMMENT 'SQL gerado e executado',
      
      -- OUTPUT: Resposta fornecida
      resposta_final LONGTEXT COMMENT 'Resposta exata ao usuário',
      confidence_score FLOAT COMMENT 'Confiança 0-100%',
      
      -- METADATA: Informações sobre processamento
      tempo_processamento_ms INT COMMENT 'Total em milliseconds',
      status ENUM('SUCCESS', 'ERROR', 'TIMEOUT', 'BLOCKED') DEFAULT 'SUCCESS' COMMENT 'Status da execução',
      mensagem_erro TEXT COMMENT 'Se houver erro',
      
      -- RASTREABILIDADE: Contexto dos dados
      periodo_dados_inicio DATE COMMENT 'Dados consultados DE',
      periodo_dados_fim DATE COMMENT 'Dados consultados ATÉ',
      data_coleta_mais_recente DATE COMMENT 'Quando foram coletados',
      
      -- FILTROS/CONTEXTO: Parâmetros da requisição
      filtros_aplicados JSON COMMENT 'UG, natureza, etc',
      parametros_request JSON COMMENT 'Tudo que veio do request',
      
      -- ÍNDICES para performance
      INDEX idx_timestamp (timestamp),
      INDEX idx_user_id (user_id),
      INDEX idx_status (status),
      FULLTEXT INDEX idx_ft_pergunta (pergunta_original)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    COMMENT='Log de todas as interações do Chatbot IFS - Auditoria e LAI'
    """

    try:
        with engine.connect() as connection:
            connection.execute(text(sql_create_table))
            connection.commit()
        logger.info("✅ Tabela chat_audit_log criada/verificada com sucesso")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabela chat_audit_log: {e}")
        return False


def get_user_ip(request=None) -> str:
    """
    Extrai IP do usuário da requisição Flask/Streamlit.
    Trata proxies corretamente (X-Forwarded-For).
    """
    try:
        if request:
            # Verificar header X-Forwarded-For (para proxies)
            if hasattr(request, 'environ'):
                forwarded = request.environ.get('HTTP_X_FORWARDED_FOR')
                if forwarded:
                    return forwarded.split(',')[0].strip()

                # Fallback para REMOTE_ADDR
                return request.environ.get('REMOTE_ADDR', 'UNKNOWN')
    except Exception as e:
        logger.warning(f"⚠️ Erro ao extrair IP: {e}")

    return 'UNKNOWN'


def log_to_audit(
    pergunta: str,
    resposta: str = "",
    status: str = "SUCCESS",
    tempo_ms: int = 0,
    user_ip: str = None,
    json_intent: Optional[Dict[str, Any]] = None,
    sql_executado: str = "",
    confidence: float = 0.0,
    entidades_detectadas: Optional[Dict] = None,
    periodo_dados_inicio: Optional[str] = None,
    periodo_dados_fim: Optional[str] = None,
    data_coleta_mais_recente: Optional[str] = None,
    filtros_aplicados: Optional[Dict] = None,
    mensagem_erro: str = None
) -> bool:
    """
    Log uma interação do chatbot em chat_audit_log.

    Args:
        pergunta (str): Pergunta original do usuário
        resposta (str): Resposta fornecida (até 5000 chars)
        status (str): SUCCESS, ERROR, TIMEOUT, BLOCKED
        tempo_ms (int): Tempo de processamento em milliseconds
        user_ip (str): IP do usuário (obtém automaticamente se None)
        json_intent (dict): Output do agente Data Detective
        sql_executado (str): SQL que foi executado
        confidence (float): Confiança 0-100%
        entidades_detectadas (dict): Entidades ParsedadeEntities JSON
        periodo_dados_inicio (str): Data início dos dados (YYYY-MM-DD)
        periodo_dados_fim (str): Data fim dos dados (YYYY-MM-DD)
        data_coleta_mais_recente (str): Última coleta (YYYY-MM-DD)
        filtros_aplicados (dict): Filtros aplicados (UG, natureza, etc)
        mensagem_erro (str): Mensagem de erro se status=ERROR

    Returns:
        bool: True se sucesso, False se erro
    """

    db = None
    try:
        db = DBConnection()

        # Sanitizar inputs
        pergunta_sanitizada = (pergunta or "")[:5000]
        resposta_sanitizada = (resposta or "")[:5000]

        # Converter JSON com defaults vazios
        json_intent_str = json.dumps(json_intent or {}, ensure_ascii=False)
        entidades_str = json.dumps(
            entidades_detectadas or {}, ensure_ascii=False)
        filtros_str = json.dumps(filtros_aplicados or {}, ensure_ascii=False)
        parametros_request = json.dumps({
            "source": "streamlit_app",
            "version": "2.0",
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False)

        # Garantir que user_ip tenha valor
        if not user_ip:
            user_ip = "UNKNOWN"

        # Query INSERT com named parameters (SQLAlchemy style)
        from sqlalchemy import text

        query = """
        INSERT INTO chat_audit_log (
            timestamp,
            user_ip,
            pergunta_original,
            json_intent,
            entidades_detectadas,
            sql_executado,
            resposta_final,
            confidence_score,
            tempo_processamento_ms,
            status,
            mensagem_erro,
            periodo_dados_inicio,
            periodo_dados_fim,
            data_coleta_mais_recente,
            filtros_aplicados,
            parametros_request
        ) VALUES (
            NOW(),
            :user_ip, :pergunta, :intent, :entidades, :sql,
            :resposta, :confidence, :tempo_ms, :status, :erro,
            :periodo_inicio, :periodo_fim, :data_coleta, :filtros, :parametros
        )
        """

        params = {
            'user_ip': user_ip,
            'pergunta': pergunta_sanitizada,
            'intent': json_intent_str,
            'entidades': entidades_str,
            'sql': sql_executado[:5000] if sql_executado else "",
            'resposta': resposta_sanitizada,
            'confidence': max(0, min(100, confidence)),
            'tempo_ms': tempo_ms,
            'status': status,
            'erro': mensagem_erro,
            'periodo_inicio': periodo_dados_inicio,
            'periodo_fim': periodo_dados_fim,
            'data_coleta': data_coleta_mais_recente,
            'filtros': filtros_str,
            'parametros': parametros_request
        }

        # Usar engine direto pois execute_query é para SELECT
        engine = db.get_engine()
        try:
            with engine.connect() as connection:
                connection.execute(text(query), params)
                connection.commit()
        except Exception as insert_error:
            logger.error(f"❌ Erro no INSERT audit: {insert_error}")
            raise

        logger.debug(
            f"✅ Audit log salvo: {pergunta_sanitizada[:50]}... (status={status})")
        return True

    except Exception as e:
        logger.error(f"❌ Erro ao salvar audit log: {str(e)}")
        # NÃO deixar erro de logging quebrar a aplicação
        # Apenas log e retorna False
        return False


def get_audit_logs(
    limit: int = 100,
    status_filter: Optional[str] = None,
    user_id_filter: Optional[str] = None
) -> list:
    """
    Recupera logs de auditoria do banco.
    Útil para analytics e monitoramento.

    Args:
        limit: Número máximo de registros
        status_filter: Filtrar por status (SUCCESS, ERROR, etc)
        user_id_filter: Filtrar por user_id

    Returns:
        list: Lista de dicts com logs
    """
    db = DBConnection()

    # Clamp seguro: evita interpolação direta de valor externo no SQL
    safe_limit = max(1, min(int(limit), 10000))

    query = "SELECT * FROM chat_audit_log WHERE 1=1"
    params = {}

    if status_filter:
        query += " AND status = :status"
        params['status'] = status_filter

    if user_id_filter:
        query += " AND user_id = :user_id"
        params['user_id'] = user_id_filter

    query += f" ORDER BY timestamp DESC LIMIT {safe_limit}"

    try:
        return db.execute_query(query, params)
    except Exception as e:
        logger.error(f"❌ Erro ao recuperar audit logs: {e}")
        return []


def get_audit_statistics() -> Dict[str, Any]:
    """
    Retorna estatísticas dos logs de auditoria.
    Útil para dashboards e monitoramento.
    """
    db = DBConnection()

    stats_query = """
    SELECT
        COUNT(*) as total_queries,
        COUNT(CASE WHEN status='SUCCESS' THEN 1 END) as success_count,
        COUNT(CASE WHEN status='ERROR' THEN 1 END) as error_count,
        AVG(tempo_processamento_ms) as avg_time_ms,
        AVG(confidence_score) as avg_confidence,
        MIN(timestamp) as first_query,
        MAX(timestamp) as last_query
    FROM chat_audit_log
    WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    """

    try:
        result = db.execute_query(stats_query)
        if result:
            return result[0]
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas: {e}")

    return {}


if __name__ == "__main__":
    """Script para inicializar tabela de auditoria"""
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("🔧 Inicializando tabela de auditoria...")
    if create_audit_table():
        print("✅ Tabela chat_audit_log pronta para usar!")
        sys.exit(0)
    else:
        print("❌ Erro ao criar tabela")
        sys.exit(1)
