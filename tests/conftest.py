"""
Configuração global de fixtures para pytest.
Compartilhada entre todos os testes.
"""

import pytest
import os
import json
from unittest.mock import Mock, MagicMock, patch
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="session")
def test_env():
    """Fornece variáveis de ambiente para testes."""
    return {
        "DB_USER": os.getenv("DB_USER", "root"),
        "DB_PASS": os.getenv("DB_PASS", "test_password"),
        "DB_HOST": os.getenv("DB_HOST", "localhost"),
        "DB_PORT": os.getenv("DB_PORT", "3306"),
        "DB_NAME": os.getenv("DB_NAME", "dw_ifs_gastos"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "test_key"),
        "OPENAI_MODEL_NAME": os.getenv("OPENAI_MODEL_NAME", "gpt-4o"),
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER", "openai"),
    }


@pytest.fixture
def mock_db_engine():
    """Mock de SQLAlchemy engine para testes de DB."""
    mock_engine = MagicMock()

    # Mock de conexão
    mock_connection = MagicMock()
    mock_result = MagicMock()

    # Simular retorno de query
    mock_result.keys.return_value = ['id_favorecido', 'nome_favorecido']
    mock_result.fetchall.return_value = [
        (1, 'Energisa'),
        (2, 'Deso'),
        (3, 'CETEL'),
    ]

    mock_connection.execute.return_value = mock_result
    mock_engine.connect.return_value.__enter__.return_value = mock_connection

    return mock_engine


@pytest.fixture
def mock_guardrails_data():
    """Mock de dados de guardrails para testes."""
    return [
        {
            "id": "vague_query",
            "gatilhos": ["todos os dados", "tudo", "me mostre tudo"],
            "resposta": "Essa pergunta é muito abrangente..."
        },
        {
            "id": "help_request",
            "gatilhos": ["ajuda", "help", "como funciona"],
            "resposta": "Sou um assistente de transparência..."
        },
        {
            "id": "security_block",
            "gatilhos": ["delete", "drop", "update"],
            "resposta": "Operação não permitida por segurança"
        }
    ]


@pytest.fixture
def sample_entity_cache():
    """Mock de cache de entidades para testes."""
    return {
        'ug': {
            1: 'Campus Aracaju',
            2: 'Campus Lagarto',
            3: 'Campus Estancia',
            4: 'Reitoria'
        },
        'favorecido': {
            1: 'Energisa Sergipe',
            2: 'Deso - Companhia de Saneamento',
            3: 'CETEL',
            4: 'Empresa X'
        },
        'programa': {
            1: 'Educação Superior',
            2: 'Assistência Estudantil',
            3: 'Pesquisa e Inovação'
        },
        'natureza': {
            1: 'Energia Elétrica',
            2: 'Água e Esgoto',
            3: 'Telecomunicações'
        }
    }


@pytest.fixture
def sample_sql_result():
    """Exemplo de resultado SQL para testes."""
    return [
        {
            'favorecido_nome': 'Energisa Sergipe',
            'total': 5000000.00,
            'id_favorecido': 1
        },
        {
            'favorecido_nome': 'Deso',
            'total': 3000000.00,
            'id_favorecido': 2
        },
        {
            'favorecido_nome': 'CETEL',
            'total': 1500000.00,
            'id_favorecido': 3
        }
    ]


@pytest.fixture
def sample_crew_json():
    """Exemplo de JSON esperado do crew."""
    return {
        "intent": "RANKING",
        "entities": [
            {
                "type": "UG",
                "name": "Campus Lagarto",
                "id": 2,
                "similarity_score": 95.0
            }
        ],
        "date_filter": {
            "year": 2024,
            "month": None
        },
        "action": "EXECUTE_SQL"
    }


@pytest.fixture
def temp_csv_path(tmp_path):
    """Fornece um caminho temporário para testes com arquivo CSV."""
    return tmp_path / "test_export.csv"


@pytest.fixture
def sample_dataframe():
    """Cria um DataFrame de exemplo para testes."""
    import pandas as pd

    return pd.DataFrame({
        'data': ['2024-01-15', '2024-01-16', '2024-01-17'],
        'valor': [1000.00, 2000.00, 1500.00],
        'favorecido_nome': ['Empresa A', 'Empresa B', 'Empresa A'],
        'unidade_pagadora': ['Campus Aracaju', 'Reitoria', 'Campus Lagarto'],
        'id_favorecido': [1, 2, 1],
        'id_ug': [1, 4, 2],
        'tipo_despesa': ['Material', 'Serviço', 'Material'],
        'programa_governo': ['Educação', 'Assistência', 'Educação']
    })


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset de Singletons entre testes para evitar estado compartilhado."""
    yield
    # Cleanup após cada teste
    # Remover instâncias de singleton se necessário
    try:
        from tools import EntityCache
        EntityCache._instance = None
        EntityCache._data = {}
    except:
        pass


# Marcadores customizados para categorizar testes
def pytest_configure(config):
    config.addinivalue_line("markers", "unit: marca testes unitários")
    config.addinivalue_line(
        "markers", "integration: marca testes de integração")
    config.addinivalue_line("markers", "slow: marca testes lentos")
    config.addinivalue_line(
        "markers", "requires_db: marca testes que precisam de BD real")
