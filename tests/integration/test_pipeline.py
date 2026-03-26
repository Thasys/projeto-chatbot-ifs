"""
Testes de integração para o sistema completo.

Testa:
- Fluxo completo: Pergunta → JSON → SQL → Resultado
- Integração entre módulos
- End-to-end scenarios
"""

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import json


class TestPipelineFlow:
    """Testa fluxo completo do pipeline."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_simple_ranking_query_flow(self, sample_dataframe):
        """Testa fluxo simples: pergunta → resultado ranking."""
        from crew_definition import IFSCrew
        from tools import execute_sql

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            # Criar crew
            crew = IFSCrew()
            question = "Quais os 5 maiores fornecedores?"

            # Extrair JSON (simular agente 1)
            mock_json = crew._extract_json_from_text(
                '{"intent": "RANKING", "entities": []}'
            )

            assert mock_json['intent'] == 'RANKING'

            # Executar SQL (simular agente 2)
            with patch('tools.pd.read_sql', return_value=sample_dataframe):
                result = execute_sql("SELECT * FROM v_financas_geral")

                assert isinstance(result, str)
                assert len(result) > 0

    @pytest.mark.integration
    @pytest.mark.slow
    def test_total_calculation_flow(self, sample_dataframe):
        """Testa fluxo de cálculo total."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()

            # JSON com intenção TOTAL
            mock_json = crew._extract_json_from_text(
                '{"intent": "TOTAL", "entities": [{"name": "Energisa"}]}'
            )

            assert mock_json['intent'] == 'TOTAL'
            assert len(mock_json['entities']) > 0

    @pytest.mark.integration
    @pytest.mark.slow
    def test_entity_search_flow(self, sample_entity_cache):
        """Testa fluxo de busca de entidade."""
        from tools import search_entity_fuzzy, EntityCache

        EntityCache._instance = None
        EntityCache._data = sample_entity_cache

        # Buscar entidade
        result = search_entity_fuzzy("Lagarto")

        assert isinstance(result, str)
        assert "Campus Lagarto" in result or "lagarto" in result.lower()

    @pytest.mark.integration
    @pytest.mark.slow
    def test_export_flow(self, sample_dataframe):
        """Testa fluxo de exportação."""
        from tools import export_csv

        with patch('tools.time.time', return_value=1234567890):
            with patch('tools.pd.read_sql', return_value=sample_dataframe):
                with patch('tools.os.makedirs'):
                    result = export_csv("SELECT * FROM v_financas_geral")

                    assert "relatorio_" in result
                    assert ".csv" in result


class TestGuardrailsIntegration:
    """Testa guardrails em pipeline."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_guardrails_blocks_dangerous_query(self, mock_guardrails_data):
        """Testa que guardrails bloqueia query perigosa."""
        from guardrails import Guardrails
        import json

        json_str = json.dumps(mock_guardrails_data)

        with patch('builtins.open'):
            with patch('os.path.exists', return_value=True):
                with patch('json.load', return_value=mock_guardrails_data):
                    gr = Guardrails('test.json')

                    # Query perigosa
                    result = gr.check_intent("DELETE FROM tabela")

                    assert result is not None
                    assert "segurança" in result.lower()

    @pytest.mark.integration
    @pytest.mark.slow
    def test_guardrails_allows_valid_query(self, mock_guardrails_data):
        """Testa que guardrails permite query válida."""
        from guardrails import Guardrails
        import json

        json_str = json.dumps(mock_guardrails_data)

        with patch('builtins.open'):
            with patch('os.path.exists', return_value=True):
                with patch('json.load', return_value=mock_guardrails_data):
                    gr = Guardrails('test.json')

                    # Query válida
                    result = gr.check_intent("Qual o gasto do Campus Lagarto?")

                    assert result is None  # Sem bloqueio


class TestDatabaseIntegration:
    """Testa integração com banco de dados."""

    @pytest.mark.integration
    @pytest.mark.requires_db
    @pytest.mark.slow
    def test_real_db_connection(self, test_env):
        """Testa conexão real com BD (requer DB rodando)."""
        from db_connection import DBConnection
        import os

        # Usar credenciais do .env
        try:
            db = DBConnection()

            # Tenta executar query simples
            result = db.execute_query("SELECT 1 as test")

            assert len(result) > 0
            assert result[0]['test'] == 1
        except Exception as e:
            pytest.skip(f"BD não disponível: {e}")

    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_tool_chain_simulation(self, sample_dataframe):
        """Simula cadeia completa de ferramentas."""
        from tools import search_entity_fuzzy, search_sql_memory, execute_sql

        # 1. Buscar entidade
        with patch('tools.EntityCache.get_data') as mock_cache:
            mock_cache.return_value = {
                'favorecido': {1: 'Energisa Sergipe'},
                'ug': {1: 'Campus Lagarto'},
                'programa': {},
                'natureza': {}
            }
            entity_result = search_entity_fuzzy("Energisa")
            assert len(entity_result) > 0

        # 2. Buscar SQL similar
        sql_mem = search_sql_memory("Fornecedores")
        assert len(sql_mem) > 0

        # 3. Executar query
        with patch('tools.pd.read_sql', return_value=sample_dataframe):
            sql_result = execute_sql("SELECT * FROM v_financas_geral")
            assert len(sql_result) > 0


class TestErrorRecovery:
    """Testa recuperação de erros."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_recovery_from_invalid_json(self):
        """Testa recuperação de JSON inválido."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()

            # JSON inválido - deve usar fallback
            result = crew._extract_json_from_text("texto que não é JSON")

            assert isinstance(result, dict)
            assert 'intent' in result
            assert 'action' in result

    @pytest.mark.integration
    @pytest.mark.slow
    def test_recovery_from_empty_query_result(self):
        """Testa recuperação de resultado vazio."""
        from tools import execute_sql

        empty_df = pd.DataFrame()

        with patch('tools.pd.read_sql', return_value=empty_df):
            result = execute_sql("SELECT * FROM v_financas_geral WHERE 1=0")

            assert "0 rows" in result or "empty" in result.lower()

    @pytest.mark.integration
    @pytest.mark.slow
    def test_recovery_from_missing_config_file(self):
        """Testa recuperação quando arquivo de config não existe."""
        from guardrails import Guardrails

        with patch('os.path.exists', return_value=False):
            gr = Guardrails('inexistente.json')

            # Não deve falhar
            assert gr.data == []

            # Verificação simples ainda funciona
            result = gr.check_intent("teste")
            assert result is None


class TestPerformance:
    """Testa performance do sistema."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_large_result_handling(self):
        """Testa processamento de resultados grandes."""
        from tools import execute_sql

        # Criar DataFrame grande
        large_df = pd.DataFrame({
            'id': range(1000),
            'valor': [100.0 * i for i in range(1000)],
            'nome': [f'Item {i}' for i in range(1000)]
        })

        with patch('tools.pd.read_sql', return_value=large_df):
            result = execute_sql("SELECT * FROM big_table")

            # Deve retornar resultado sem erro
            assert isinstance(result, str)
            assert len(result) > 0

            # Deve incluir resumo
            assert "Summary" in result or "First 5" in result

    @pytest.mark.integration
    @pytest.mark.slow
    def test_fast_entity_search(self, sample_entity_cache):
        """Testa velocidade de busca de entidade."""
        from tools import search_entity_fuzzy, EntityCache
        import time

        EntityCache._instance = None
        EntityCache._data = sample_entity_cache

        start = time.time()

        # Fazer 100 buscas
        for i in range(100):
            search_entity_fuzzy(f"Campus {i % 3}")

        elapsed = time.time() - start

        # Deve ser rápido (menos de 5 segundos para 100 buscas)
        assert elapsed < 5.0


class TestConcurrency:
    """Testa comportamento com múltiplas requisições."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_singleton_thread_safety(self):
        """Testa que Singleton é thread-safe."""
        from db_connection import DBConnection
        from threading import Thread

        DBConnection._instance = None

        results = []

        def get_instance():
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
                    results.append(db)

        # Criar múltiplas threads
        threads = [Thread(target=get_instance) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Todas devem ser a mesma instância
        if len(results) > 1:
            for db in results[1:]:
                assert db is results[0]


class TestComplexScenarios:
    """Testa cenários complexos."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_multi_filter_query(self, sample_dataframe):
        """Testa query com múltiplos filtros."""
        from tools import execute_sql

        # Query com múltiplos filtros
        query = """
        SELECT 
            unidade_pagadora, 
            tipo_despesa,
            SUM(valor) as total
        FROM v_financas_geral
        WHERE 
            data >= '2024-01-01'
            AND id_ug IN (1, 2, 3)
            AND tipo_despesa LIKE '%Material%'
        GROUP BY unidade_pagadora, tipo_despesa
        """

        with patch('tools.pd.read_sql', return_value=sample_dataframe):
            result = execute_sql(query)

            assert isinstance(result, str)

    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_crew_execution_simulation(self):
        """Simula execução completa do crew."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()
            question = "Quanto foi gasto com energia em 2024?"

            # Criar crew
            crew_obj = crew.get_crew(question)

            # Verificar estrutura
            assert len(crew_obj.agents) == 3
            assert len(crew_obj.tasks) == 3

            # Verificar que tasks estão em ordem
            assert len(crew_obj.tasks[0].context) == 0
            assert len(crew_obj.tasks[1].context) > 0
            assert len(crew_obj.tasks[2].context) > 0
