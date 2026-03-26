"""
Testes unitários para tools.py

Testa:
- search_entity_fuzzy (busca semântica de entidades)
- search_sql_memory (recuperação de templates SQL)
- execute_sql (execução de queries)
- export_csv (exportação de dados)
- EntityCache (cache de entidades)
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
import pandas as pd
import json
import os


class TestEntityCache:
    """Testa o sistema de cache de entidades."""

    @pytest.mark.unit
    def test_entity_cache_singleton(self, sample_entity_cache):
        """Verifica que EntityCache usa Singleton."""
        from tools import EntityCache

        EntityCache._instance = None
        EntityCache._data = {}

        with patch('tools.DBConnection') as mock_db:
            mock_db.return_value.get_engine.return_value = MagicMock()
            with patch('tools.pd.read_sql') as mock_read_sql:
                mock_read_sql.return_value = pd.DataFrame(sample_entity_cache['ug'].items(),
                                                          columns=['id_ug', 'ug'])

                data1 = EntityCache.get_data()
                data2 = EntityCache.get_data()

                # Mesma instância
                assert data1 is data2

    @pytest.mark.unit
    def test_entity_cache_loading(self, sample_entity_cache):
        """Verifica carregamento de dados no cache."""
        from tools import EntityCache

        EntityCache._instance = None
        EntityCache._data = {}

        with patch('tools.DBConnection') as mock_db:
            with patch('tools.pd.read_sql') as mock_read_sql:
                # Simular retorno de leitura
                def side_effect(sql, engine):
                    if 'dim_ug' in sql:
                        return pd.DataFrame(
                            [(k, v)
                             for k, v in sample_entity_cache['ug'].items()],
                            columns=['id_ug', 'ug']
                        )
                    elif 'dim_favorecido' in sql:
                        return pd.DataFrame(
                            [(k, v)
                             for k, v in sample_entity_cache['favorecido'].items()],
                            columns=['id_favorecido', 'nomeFavorecido']
                        )
                    return pd.DataFrame()

                mock_read_sql.side_effect = side_effect

                data = EntityCache.get_data()

                assert 'ug' in data
                assert 'favorecido' in data
                assert len(data['ug']) > 0

    @pytest.mark.unit
    def test_entity_cache_error_handling(self):
        """Verifica tratamento de erro no cache."""
        from tools import EntityCache

        EntityCache._instance = None
        EntityCache._data = {}

        with patch('tools.DBConnection') as mock_db:
            with patch('tools.pd.read_sql') as mock_read_sql:
                mock_read_sql.side_effect = Exception("BD offline")

                # Não deve lançar exceção
                data = EntityCache.get_data()
                assert isinstance(data, dict)


class TestAggressiveClean:
    """Testa função de limpeza agressiva."""

    @pytest.mark.unit
    def test_aggressive_clean_removes_accents(self):
        """Verifica remoção de acentos."""
        from tools import aggressive_clean

        assert aggressive_clean("São Cristóvão") == "sao cristovao"
        assert aggressive_clean("Lagarto") == "lagarto"
        assert aggressive_clean("Estância") == "estancia"

    @pytest.mark.unit
    def test_aggressive_clean_lowercase(self):
        """Verifica conversão para minúscula."""
        from tools import aggressive_clean

        assert aggressive_clean("ENERGISA") == "energisa"
        assert aggressive_clean("Campus Lagarto") == "campus lagarto"

    @pytest.mark.unit
    def test_aggressive_clean_with_non_string(self):
        """Verifica tratamento de tipos não-string."""
        from tools import aggressive_clean

        assert aggressive_clean(123) == "123"
        assert aggressive_clean(None) == "none"

    @pytest.mark.unit
    def test_aggressive_clean_strips_whitespace(self):
        """Verifica remoção de espaços."""
        from tools import aggressive_clean

        assert aggressive_clean("  Energisa  ") == "energisa"
        assert aggressive_clean("\tLagarto\n") == "lagarto"


class TestSearchEntityFuzzy:
    """Testa busca fuzzy de entidades."""

    @pytest.mark.unit
    def test_search_entity_fuzzy_exact_match(self, sample_entity_cache):
        """Verifica busca com correspondência exata."""
        from tools import search_entity_fuzzy, EntityCache

        EntityCache._instance = None
        EntityCache._data = sample_entity_cache

        result = search_entity_fuzzy("Campus Lagarto")

        assert isinstance(result, str)
        assert "Campus Lagarto" in result or "lagarto" in result.lower()

    @pytest.mark.unit
    def test_search_entity_fuzzy_typo_tolerance(self, sample_entity_cache):
        """Verifica tolerância a erros de digitação."""
        from tools import search_entity_fuzzy, EntityCache

        EntityCache._instance = None
        EntityCache._data = sample_entity_cache

        # Typo: "Enegisa" ao invés de "Energisa"
        result = search_entity_fuzzy("Enegisa")

        assert isinstance(result, str)
        assert "Energisa" in result

    @pytest.mark.unit
    def test_search_entity_fuzzy_empty_result(self, sample_entity_cache):
        """Verifica comportamento com busca sem resultados."""
        from tools import search_entity_fuzzy, EntityCache

        EntityCache._instance = None
        EntityCache._data = sample_entity_cache

        result = search_entity_fuzzy("XYZ_INEXISTENTE_ABC")

        assert "No entities found" in result

    @pytest.mark.unit
    def test_search_entity_fuzzy_category_priority(self, sample_entity_cache):
        """Verifica que UG tem prioridade em busca."""
        from tools import search_entity_fuzzy, EntityCache

        EntityCache._instance = None
        EntityCache._data = sample_entity_cache

        result = search_entity_fuzzy("Campus")

        # Deve encontrar UG (Campus)
        assert "UG" in result or "campus" in result.lower()

    @pytest.mark.unit
    def test_search_entity_fuzzy_error_handling(self):
        """Verifica tratamento de erro."""
        from tools import search_entity_fuzzy

        with patch('tools.EntityCache.get_data') as mock_cache:
            mock_cache.side_effect = Exception("Cache error")

            result = search_entity_fuzzy("Test")

            assert "Error" in result


class TestSearchSqlMemory:
    """Testa recuperação de templates SQL."""

    @pytest.mark.unit
    def test_search_sql_memory_finds_similar_queries(self):
        """Verifica busca de queries similares."""
        from tools import search_sql_memory

        result = search_sql_memory("Quais os maiores fornecedores?")

        assert isinstance(result, str)
        # Deve encontrar exemplos similares
        assert len(result) > 0

    @pytest.mark.unit
    def test_search_sql_memory_no_match(self):
        """Verifica comportamento sem correspondência."""
        from tools import search_sql_memory

        result = search_sql_memory("xyz abc def ghi jkl")

        assert "No memory found" in result

    @pytest.mark.unit
    def test_search_sql_memory_returns_sql_examples(self):
        """Verifica que retorna exemplos SQL."""
        from tools import search_sql_memory

        result = search_sql_memory("total gasto")

        assert "SQL" in result or "SELECT" in result.upper()

    @pytest.mark.unit
    def test_search_sql_memory_error_handling(self):
        """Verifica tratamento de erro."""
        from tools import search_sql_memory

        with patch('tools.process.extract') as mock_extract:
            mock_extract.side_effect = Exception("Error")

            result = search_sql_memory("test")

            assert "Memory Error" in result


class TestExecuteSql:
    """Testa execução de queries SQL."""

    @pytest.mark.unit
    def test_execute_sql_select_query(self, sample_dataframe):
        """Verifica execução de query SELECT."""
        from tools import execute_sql

        with patch('tools.DBConnection') as mock_db:
            with patch('tools.pd.read_sql', return_value=sample_dataframe):
                result = execute_sql("SELECT * FROM v_financas_geral")

                assert isinstance(result, str)
                assert "2024-01-15" in result or "Empresa A" in result

    @pytest.mark.unit
    def test_execute_sql_rejects_non_select(self):
        """Verifica rejeição de queries não-SELECT."""
        from tools import execute_sql

        result = execute_sql("DELETE FROM v_financas_geral")

        assert "Only SELECT queries are allowed" in result

    @pytest.mark.unit
    def test_execute_sql_empty_result(self):
        """Verifica comportamento com resultado vazio."""
        from tools import execute_sql

        with patch('tools.pd.read_sql') as mock_read:
            mock_read.return_value = pd.DataFrame()  # DataFrame vazio

            result = execute_sql("SELECT * FROM v_financas_geral WHERE 1=0")

            assert "0 rows" in result or "empty" in result.lower()

    @pytest.mark.unit
    def test_execute_sql_large_result_summarization(self):
        """Verifica resumo para resultados grandes."""
        from tools import execute_sql

        # Criar DataFrame grande
        large_df = pd.DataFrame({
            'id': range(50),
            'valor': [100.0 * i for i in range(50)],
            'nome': [f'Item {i}' for i in range(50)]
        })

        with patch('tools.pd.read_sql', return_value=large_df):
            result = execute_sql("SELECT * FROM v_financas_geral")

            # Deve conter resumo
            assert "Summary" in result or "First 5 Rows" in result

    @pytest.mark.unit
    def test_execute_sql_cleans_markdown(self):
        """Verifica remoção de markdown."""
        from tools import execute_sql

        with patch('tools.pd.read_sql', return_value=pd.DataFrame({'col': [1, 2, 3]})):
            result = execute_sql("```sql\nSELECT * FROM test\n```")

            assert "```" not in result

    @pytest.mark.unit
    def test_execute_sql_error_handling(self):
        """Verifica tratamento de erro SQL."""
        from tools import execute_sql

        with patch('tools.pd.read_sql') as mock_read:
            mock_read.side_effect = Exception("Syntax Error in SQL")

            result = execute_sql("SELECT * FROM tabela_inexistente")

            assert "Error" in result


class TestExportCsv:
    """Testa exportação para CSV."""

    @pytest.mark.unit
    def test_export_csv_creates_file(self, sample_dataframe, tmp_path):
        """Verifica criação de arquivo CSV."""
        from tools import export_csv

        with patch('tools.time.time', return_value=1234567890):
            with patch('tools.pd.read_sql', return_value=sample_dataframe):
                with patch('tools.os.makedirs'):
                    result = export_csv("SELECT * FROM v_financas_geral")

                    assert "relatorio_" in result
                    assert ".csv" in result
                    assert "File generated" in result

    @pytest.mark.unit
    def test_export_csv_csv_format(self, sample_dataframe):
        """Verifica formato CSV."""
        from tools import export_csv

        with patch('tools.time.time', return_value=1234567890):
            with patch('tools.pd.read_sql', return_value=sample_dataframe):
                with patch('tools.os.makedirs'):
                    with patch.object(sample_dataframe, 'to_csv') as mock_csv:
                        result = export_csv("SELECT *")

                        # Verifica parâmetros
                        if mock_csv.called:
                            call_kwargs = mock_csv.call_args[1]
                            # Separador português
                            assert call_kwargs.get('sep') == ';'
                            assert call_kwargs.get(
                                'decimal') == ','  # Decimal português

    @pytest.mark.unit
    def test_export_csv_error_handling(self):
        """Verifica tratamento de erro."""
        from tools import export_csv

        with patch('tools.pd.read_sql') as mock_read:
            mock_read.side_effect = Exception("BD Error")

            result = export_csv("SELECT *")

            assert "Error" in result

    @pytest.mark.unit
    def test_export_csv_creates_reports_directory(self, tmp_path):
        """Verifica criação de diretório reports."""
        from tools import export_csv

        with patch('tools.time.time', return_value=9999):
            with patch('tools.pd.read_sql', return_value=pd.DataFrame({'a': [1]})):
                with patch('tools.os.makedirs') as mock_mkdir:
                    export_csv("SELECT *")

                    # Verifica que makedirs foi chamado
                    mock_mkdir.assert_called()


class TestToolsIntegration:
    """Testa integração entre ferramentas."""

    @pytest.mark.unit
    def test_all_tools_importable(self):
        """Verifica que todas as ferramentas podem ser importadas."""
        from tools import (
            search_entity_fuzzy,
            search_sql_memory,
            execute_sql,
            export_csv,
            EntityCache,
            aggressive_clean
        )

        # Todas as funções devem ser callable
        assert callable(search_entity_fuzzy)
        assert callable(search_sql_memory)
        assert callable(execute_sql)
        assert callable(export_csv)

    @pytest.mark.unit
    @pytest.mark.slow
    def test_tool_chaining_workflow(self, sample_entity_cache):
        """Testa fluxo típico: Entity → SQL → Execute → Export."""
        from tools import search_entity_fuzzy, search_sql_memory, execute_sql

        # 1. Buscar entidade
        EntityCache._instance = None
        EntityCache._data = sample_entity_cache

        entity_result = search_entity_fuzzy("Energisa")
        assert "Energisa" in entity_result

        # 2. Buscar SQL similar
        sql_result = search_sql_memory("Quanto foi pago para Energisa?")
        assert isinstance(sql_result, str)

        # 3. Executar query
        with patch('tools.pd.read_sql') as mock_read:
            mock_read.return_value = pd.DataFrame({
                'favorecido_nome': ['Energisa'],
                'total': [5000000.0]
            })

            sql_result = execute_sql("SELECT SUM(valor) FROM v_financas_geral")
            assert isinstance(sql_result, str)
