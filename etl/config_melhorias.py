"""
Configurações adicionais para melhorias de performance, segurança e observabilidade do ETL.
"""

# ========== CONFIGURAÇÕES DE PERFORMANCE ==========
ETL_CONFIG = {
    'performance': {
        'batch_size_carga': 5000,  # Tamanho de batch para carga incremental
        'timeout_api': 30,  # Timeout em segundos
        'max_retries': 3,  # Máximo de retentativas
        'sleep_entre_requisicoes': 0.5,  # Sleep entre requisições (segundos)
        'use_parallel_processing': False,  # Processar dimensões em paralelo
        'num_workers': 4,  # Número de workers para processamento paralelo
    },

    # ========== CONFIGURAÇÕES DE VALIDAÇÃO ==========
    'validacao': {
        'validar_chaves_estrangeiras': True,
        'remover_registros_orfaos': True,
        'limite_maximo_valor': 999_999_999,  # Valor máximo permitido
        'campos_obrigatorios_extracao': [
            'documento', 'valor', 'dataEmissao', 'codigoUg', 'ug'
        ],
        'campos_obrigatorios_transformacao': [
            'valor', 'data', 'codigoFavorecido', 'nomeFavorecido',
            'codigoUg', 'ug', 'categoria', 'grupo', 'modalidade', 'elemento'
        ],
    },

    # ========== CONFIGURAÇÕES DE AUDITORIA ==========
    'auditoria': {
        'registrar_cada_operacao': True,
        'manter_historico': True,
        'dias_retencao_logs': 90,
        'nivel_logging': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    },

    # ========== CONFIGURAÇÕES DE SEGURANÇA ==========
    'seguranca': {
        'criptografar_senhas': True,
        'validar_certificado_ssl': True,
        'mascarar_dados_sensiveis': True,
    },

    # ========== CONFIGURAÇÕES DE ALERTA ==========
    'alertas': {
        'habilitar_alertas': True,
        'limiar_rejeitados': 0.1,  # Percentual de rejeição para alerta (10%)
        'limiar_tempo_execucao': 3600,  # Tempo máximo em segundos (1 hora)
        'email_notificacao': 'admin@ifs.edu.br',
    },

    # ========== CONFIGURAÇÕES DE CACHE ==========
    'cache': {
        'usar_cache': True,
        'ttl_cache': 3600,  # Time to live em segundos
        'tipo_cache': 'memoria',  # 'memoria' ou 'redis'
    },
}

# ========== MAPEAMENTO DE CAMPOS ==========
MAPEAMENTO_COLUNAS = {
    'extracao': {
        'documento': 'documento',
        'valor': 'valor',
        'data_emissao': 'dataEmissao',
        'codigo_ug': 'codigoUg',
        'ug': 'ug',
    },
    'transformacao': {
        'valor_transacao': 'valor',
        'data_emissao': 'data',
        'codigo_favorecido': 'codigoFavorecido',
    }
}

# ========== PADRÕES DE VALIDAÇÃO ==========
PADROES_VALIDACAO = {
    'cpf': r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
    'cnpj': r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$',
    'data': r'^\d{4}-\d{2}-\d{2}$',
    'moeda': r'^-?\d{1,}[.,]\d{2}$',
}

# ========== NÍVEIS DE LOG ==========
LOG_LEVELS = {
    'DEBUG': 10,
    'INFO': 20,
    'WARNING': 30,
    'ERROR': 40,
    'CRITICAL': 50,
}
