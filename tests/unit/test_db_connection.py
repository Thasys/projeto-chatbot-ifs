"""
Testes unitários para db_connection.py

Testa:
- Inicialização da conexão
- Singleton pattern
- Validação de conexão
- Tratamento de erro
- Métodos de query e schema
"""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from sqlalchemy import create_engine
import logging

logger = logging.getLogger(__name__)


class TestDBConnectionInitialization:
    """Testa inicialização e Singleton pattern."""

    @pytest.mark.unit
    def test_singleton_instance_created_once(self):
        """Verifica que DBConnection usa Singleton corretamente."""
        from db_connection import DBConnection

        # Reseta singleton
        DBConnection._instance = None

        # Mock da conexão
        with patch.dict('os.environ', {
            'DB_USER': 'test_user',
            'DB_PASS': 'test_pass',
            'DB_HOST': 'localhost',
            'DB_PORT': '3306',
            'DB_NAME': 'test_db'
        }):
            with patch('db_connection.create_engine') as mock_engine:
                mock_engine.return_value = MagicMock()

                instance1 = DBConnection()
                instance2 = DBConnection()

                # Mesma instância
                assert instance1 is instance2

                # create_engine chamado uma vez
                assert mock_engine.call_count == 1

    @pytest.mark.unit
    def test_missing_environment_variables_raises_error(self):
        """Verifica que variáveis de ambiente incompletas causam erro."""
        from db_connection import DBConnection

        DBConnection._instance = None

        # Ambiente vazio
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                DBConnection()

            assert "incompletas" in str(exc_info.value).lower()
            assert "env" in str(exc_info.value).lower()

    @pytest.mark.unit
    def test_connection_validation_on_init(self):
        """Verifica que validação de conexão é chamada na inicialização."""
        from db_connection import DBConnection

        DBConnection._instance = None

        with patch.dict('os.environ', {
            'DB_USER': 'test',
            'DB_PASS': 'test',
            'DB_HOST': 'localhost',
            'DB_PORT': '3306',
            'DB_NAME': 'test'
        }):
            with patch('db_connection.create_engine') as mock_engine:
                with patch.object(DBConnection, '_validate_connection') as mock_validate:
                    mock_engine.return_value = MagicMock()

                    DBConnection()

                    # Validação foi chamada
                    assert mock_validate.called


class TestDBConnectionValidation:
    """Testa métodos de validação."""

    @pytest.mark.unit
    def test_validate_connection_success(self):
        """Verifica sucesso na validação de conexão."""
        from db_connection import DBConnection

        DBConnection._instance = None

        with patch.dict('os.environ', {
            'DB_USER': 'test',
            'DB_PASS': 'test',
            'DB_HOST': 'localhost',
            'DB_PORT': '3306',
            'DB_NAME': 'test'
        }):
            with patch('db_connection.create_engine') as mock_engine:
                mock_conn = MagicMock()
                mock_result = MagicMock()
                mock_result.close.return_value = None

                mock_conn.execute.return_value = mock_result
                mock_engine.return_value.connect.return_value.__enter__.return_value = mock_conn

                db = DBConnection()

                assert db.is_connected() is True

    @pytest.mark.unit
    def test_validate_connection_failure(self):
        """Verifica erro quando validação de conexão falha."""
        from db_connection import DBConnection

        DBConnection._instance = None

        with patch.dict('os.environ', {
            'DB_USER': 'test',
            'DB_PASS': 'test',
            'DB_HOST': 'localhost',
            'DB_PORT': '3306',
            'DB_NAME': 'test'
        }):
            with patch('db_connection.create_engine') as mock_engine:
                # Simular erro de conexão
                mock_engine.return_value.connect.return_value.__enter__.side_effect = \
                    ConnectionError("Não conseguiu conectar")

                with pytest.raises(ConnectionError) as exc_info:
                    DBConnection()

                assert "conectar" in str(exc_info.value).lower()

    @pytest.mark.unit
    def test_is_connected_method(self):
        """Verifica método is_connected()."""
        from db_connection import DBConnection

        DBConnection._instance = None

        with patch.dict('os.environ', {
            'DB_USER': 'test',
            'DB_PASS': 'test',
            'DB_HOST': 'localhost',
            'DB_PORT': '3306',
            'DB_NAME': 'test'
        }):
            with patch('db_connection.create_engine') as mock_engine:
                mock_engine.return_value = MagicMock()
                mock_engine.return_value.connect.return_value.__enter__.return_value = MagicMock()

                db = DBConnection()

                # Connected
                assert db.is_connected() is True

                # Simular desconexão
                db._is_connected = False
                assert db.is_connected() is False


class TestDBConnectionMethods:
    """Testa métodos get_engine, execute_query, get_schema_info."""

    @pytest.mark.unit
    def test_get_engine_returns_engine(self, mock_db_engine):
        """Verifica que get_engine retorna engine válida."""
        from db_connection import DBConnection

        DBConnection._instance = None

        with patch.dict('os.environ', {
            'DB_USER': 'test',
            'DB_PASS': 'test',
            'DB_HOST': 'localhost',
            'DB_PORT': '3306',
            'DB_NAME': 'test'
        }):
            with patch('db_connection.create_engine', return_value=mock_db_engine):
                db = DBConnection()
                engine = db.get_engine()

                assert engine is not None
                assert engine is mock_db_engine

    @pytest.mark.unit
    def test_get_engine_when_disconnected_raises_error(self):
        """Verifica erro ao chamar get_engine sem conexão."""
        from db_connection import DBConnection

        DBConnection._instance = None

        with patch.dict('os.environ', {
            'DB_USER': 'test',
            'DB_PASS': 'test',
            'DB_HOST': 'localhost',
            'DB_PORT': '3306',
            'DB_NAME': 'test'
        }):
            with patch('db_connection.create_engine') as mock_engine:
                with patch.object(DBConnection, '_validate_connection'):
                    db = DBConnection()
                    db._is_connected = False

                    with pytest.raises(RuntimeError) as exc_info:
                        db.get_engine()

                    assert "não está ativa" in str(exc_info.value).lower()

    @pytest.mark.unit
    def test_execute_query_success(self, mock_db_engine):
        """Verifica execução bem-sucedida de query."""
        from db_connection import DBConnection

        DBConnection._instance = None

        with patch.dict('os.environ', {
            'DB_USER': 'test',
            'DB_PASS': 'test',
            'DB_HOST': 'localhost',
            'DB_PORT': '3306',
            'DB_NAME': 'test'
        }):
            with patch('db_connection.create_engine', return_value=mock_db_engine):
                db = DBConnection()

                result = db.execute_query(
                    "SELECT * FROM dim_favorecido LIMIT 3")

                # Verifica resultado
                assert len(result) == 3
                assert result[0]['nomeFavorecido'] == 'Energisa'
                assert result[1]['nomeFavorecido'] == 'Deso'

    @pytest.mark.unit
    def test_execute_query_with_params(self, mock_db_engine):
        """Verifica execução de query com parâmetros."""
        from db_connection import DBConnection

        DBConnection._instance = None

        with patch.dict('os.environ', {
            'DB_USER': 'test',
            'DB_PASS': 'test',
            'DB_HOST': 'localhost',
            'DB_PORT': '3306',
            'DB_NAME': 'test'
        }):
            with patch('db_connection.create_engine', return_value=mock_db_engine):
                db = DBConnection()

                result = db.execute_query(
                    "SELECT * FROM dim_favorecido WHERE id_favorecido = :id",
                    {'id': 1}
                )

                assert len(result) == 1
                assert result[0]['nomeFavorecido'] == 'Energisa'

    @pytest.mark.unit
    def test_execute_query_error_handling(self, mock_db_engine):
        """Verifica tratamento de erro em execute_query."""
        from db_connection import DBConnection

        DBConnection._instance = None

        with patch.dict('os.environ', {
            'DB_USER': 'test',
            'DB_PASS': 'test',
            'DB_HOST': 'localhost',
            'DB_PORT': '3306',
            'DB_NAME': 'test'
        }):
            with patch('db_connection.create_engine', return_value=mock_db_engine):
                db = DBConnection()

                # Simular erro de query
                mock_db_engine.connect.return_value.__enter__.return_value.execute.side_effect = \
                    Exception("SQL Syntax Error")

                with pytest.raises(Exception) as exc_info:
                    db.execute_query("SELECT * FROM tabela_inexistente")

                assert "Syntax Error" in str(exc_info.value)

    @pytest.mark.unit
    def test_get_schema_info_success(self):
        """Verifica recuperação de informações de schema."""
        from db_connection import DBConnection

        DBConnection._instance = None

        with patch.dict('os.environ', {
            'DB_USER': 'test',
            'DB_PASS': 'test',
            'DB_HOST': 'localhost',
            'DB_PORT': '3306',
            'DB_NAME': 'test'
        }):
            with patch('db_connection.create_engine') as mock_engine:
                with patch('db_connection.inspect') as mock_inspect:
                    mock_engine.return_value = MagicMock()

                    # Mock do inspector
                    mock_inspector = MagicMock()
                    mock_inspect.return_value = mock_inspector
                    mock_inspector.get_table_names.return_value = [
                        'dim_favorecido', 'dim_ug']
                    mock_inspector.get_columns.side_effect = [
                        [{'name': 'id_favorecido', 'type': 'INT'},
                         {'name': 'nome', 'type': 'VARCHAR'}],
                        [{'name': 'id_ug', 'type': 'INT'},
                         {'name': 'ug_name', 'type': 'VARCHAR'}]
                    ]

                    db = DBConnection()
                    schema_info = db.get_schema_info()

                    assert 'dim_favorecido' in schema_info
                    assert 'dim_ug' in schema_info
                    assert 'INT' in schema_info
                    assert 'VARCHAR' in schema_info


class TestDBConnectionClose:
    """Testa método close()."""

    @pytest.mark.unit
    def test_close_connection(self):
        """Verifica fechamento de conexão."""
        from db_connection import DBConnection

        DBConnection._instance = None

        with patch.dict('os.environ', {
            'DB_USER': 'test',
            'DB_PASS': 'test',
            'DB_HOST': 'localhost',
            'DB_PORT': '3306',
            'DB_NAME': 'test'
        }):
            with patch('db_connection.create_engine') as mock_engine:
                mock_engine.return_value = MagicMock()
                mock_engine.return_value.connect.return_value.__enter__.return_value = MagicMock()

                db = DBConnection()

                assert db.is_connected() is True

                db.close()

                assert db.is_connected() is False
                mock_engine.return_value.dispose.assert_called_once()


class TestDBConnectionPoolConfig:
    """Testa configuração de pool connection."""

    @pytest.mark.unit
    def test_pool_configuration(self):
        """Verifica parâmetros de pool passados ao create_engine."""
        from db_connection import DBConnection

        DBConnection._instance = None

        with patch.dict('os.environ', {
            'DB_USER': 'test',
            'DB_PASS': 'test',
            'DB_HOST': 'localhost',
            'DB_PORT': '3306',
            'DB_NAME': 'test'
        }):
            with patch('db_connection.create_engine') as mock_engine:
                mock_engine.return_value = MagicMock()
                mock_engine.return_value.connect.return_value.__enter__.return_value = MagicMock()

                DBConnection()

                # Verificar parâmetros de pool
                call_kwargs = mock_engine.call_args[1]
                assert call_kwargs.get('pool_pre_ping') is True
                assert call_kwargs.get('pool_size') == 5
                assert call_kwargs.get('max_overflow') == 10
                assert call_kwargs.get('pool_recycle') == 3600
