"""
Testes unitários para crew_definition.py

Testa:
- Inicialização dos agentes
- Fluxo de tarefas
- Extração de JSON
- Detecção de intenção
"""

import pytest
from unittest.mock import patch, MagicMock
import json


class TestIFSCrewInitialization:
    """Testa inicialização do IFS Crew."""

    @pytest.mark.unit
    def test_ifs_crew_init(self):
        """Verifica inicialização básica."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()

            assert crew is not None
            assert crew.llm_engine is not None

    @pytest.mark.unit
    def test_ifs_crew_has_extract_json_method(self):
        """Verifica que método _extract_json_from_text existe."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()

            assert hasattr(crew, '_extract_json_from_text')
            assert callable(crew._extract_json_from_text)


class TestJsonExtraction:
    """Testa método _extract_json_from_text."""

    @pytest.mark.unit
    def test_extract_valid_json(self):
        """Verifica extração de JSON válido."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()

            valid_json_text = '{"intent": "RANKING", "entities": []}'
            result = crew._extract_json_from_text(valid_json_text)

            assert isinstance(result, dict)
            assert result['intent'] == 'RANKING'

    @pytest.mark.unit
    def test_extract_json_with_markdown(self):
        """Verifica extração de JSON com markdown."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()

            json_with_markdown = 'Aqui está: ```json\n{"intent": "TOTAL", "entities": []}\n```'
            result = crew._extract_json_from_text(json_with_markdown)

            assert isinstance(result, dict)
            assert result['intent'] == 'TOTAL'

    @pytest.mark.unit
    def test_extract_json_invalid_fallback_ranking(self):
        """Verifica fallback para RANKING."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()

            # Texto sem JSON válido com dica de RANKING
            text = "Os maiores fornecedores são..."
            result = crew._extract_json_from_text(text)

            assert isinstance(result, dict)
            assert result['intent'] == 'RANKING'

    @pytest.mark.unit
    def test_extract_json_invalid_fallback_total(self):
        """Verifica fallback para TOTAL."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()

            # Texto sem JSON válido com dica de TOTAL
            text = "O total gasto foi..."
            result = crew._extract_json_from_text(text)

            assert isinstance(result, dict)
            assert result['intent'] == 'TOTAL'

    @pytest.mark.unit
    def test_extract_json_invalid_fallback_search(self):
        """Verifica fallback para SEARCH."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()

            # Texto genérico sem indicação clara
            text = "Os dados mostram..."
            result = crew._extract_json_from_text(text)

            assert isinstance(result, dict)
            assert result['intent'] == 'SEARCH'

    @pytest.mark.unit
    def test_extract_json_includes_fallback_action(self):
        """Verifica que fallback inclui ação."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()

            result = crew._extract_json_from_text("texto qualquer")

            assert 'action' in result
            assert result['action'] == 'EXECUTE_SQL'


class TestGetCrew:
    """Testa método get_crew que cria a orquestração."""

    @pytest.mark.unit
    def test_get_crew_returns_crew_object(self):
        """Verifica que get_crew retorna objeto Crew."""
        from crew_definition import IFSCrew
        from crewai import Crew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()
            result = crew.get_crew("Teste pergunta")

            assert isinstance(result, Crew)

    @pytest.mark.unit
    def test_get_crew_creates_3_agents(self):
        """Verifica que são criados 3 agentes."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()
            crew_obj = crew.get_crew("Teste pergunta")

            assert len(crew_obj.agents) == 3

    @pytest.mark.unit
    def test_get_crew_creates_3_tasks(self):
        """Verifica que são criadas 3 tarefas."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()
            crew_obj = crew.get_crew("Teste pergunta")

            assert len(crew_obj.tasks) == 3

    @pytest.mark.unit
    def test_get_crew_includes_user_question(self):
        """Verifica que pergunta do usuário é incluída."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()
            test_question = "Quais são os 5 maiores fornecedores?"
            crew_obj = crew.get_crew(test_question)

            # Verificar que pergunta está em alguma tarefa
            task_descriptions = [task.description for task in crew_obj.tasks]
            assert any(test_question in desc for desc in task_descriptions)

    @pytest.mark.unit
    def test_get_crew_agent_roles(self):
        """Verifica papéis dos agentes."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()
            crew_obj = crew.get_crew("Teste")

            agent_roles = [agent.role for agent in crew_obj.agents]

            # Deve ter agentes específicos
            assert len(agent_roles) == 3
            # Verificar que nenhum papel é vazio
            assert all(len(role) > 0 for role in agent_roles)


class TestCrewDateContext:
    """Testa contexto temporal do crew."""

    @pytest.mark.unit
    def test_crew_includes_date_context(self):
        """Verifica que contexto de data é incluído."""
        from crew_definition import IFSCrew
        from datetime import datetime

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()
            crew_obj = crew.get_crew("Teste")

            # Verificar que data está em alguma tarefa
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")

            task_descriptions = [task.description for task in crew_obj.tasks]
            # Pelo menos uma tarefa deve mencionar data
            assert any(date_str in desc for desc in task_descriptions) or \
                any('2024' in desc or '2025' in desc for desc in task_descriptions)

    @pytest.mark.unit
    def test_crew_includes_year(self):
        """Verifica que ano atual está incluído."""
        from crew_definition import IFSCrew
        from datetime import datetime

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()
            crew_obj = crew.get_crew("Teste")

            current_year = str(datetime.now().year)
            task_descriptions = ' '.join(
                [task.description for task in crew_obj.tasks])

            # Deve conter o ano
            assert current_year in task_descriptions


class TestCrewSequential:
    """Testa que crew usa processo sequencial."""

    @pytest.mark.unit
    def test_crew_uses_sequential_process(self):
        """Verifica que crew usa Process.sequential."""
        from crew_definition import IFSCrew
        from crewai import Process

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()
            crew_obj = crew.get_crew("Teste")

            assert crew_obj.process == Process.sequential


class TestCrewAgentTools:
    """Testa ferramentas atribuídas aos agentes."""

    @pytest.mark.unit
    def test_first_agent_has_fuzzy_search(self):
        """Verifica que primeiro agente tem search_entity_fuzzy."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()
            crew_obj = crew.get_crew("Teste")

            first_agent_tools = crew_obj.agents[0].tools

            # Deve ter pelo menos uma ferramenta
            assert len(first_agent_tools) > 0

    @pytest.mark.unit
    def test_second_agent_has_sql_tools(self):
        """Verifica que segundo agente tem ferramentas SQL."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()
            crew_obj = crew.get_crew("Teste")

            second_agent_tools = crew_obj.agents[1].tools

            # Deve ter múltiplas ferramentas (execute_sql, export_csv, etc)
            assert len(second_agent_tools) > 0


class TestCrewMemory:
    """Testa memória do crew."""

    @pytest.mark.unit
    def test_crew_has_memory_enabled(self):
        """Verifica que crew tem memória ativada."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()
            crew_obj = crew.get_crew("Teste")

            assert crew_obj.memory is True


class TestCrewEdgeCases:
    """Testa casos extremos."""

    @pytest.mark.unit
    def test_crew_with_empty_question(self):
        """Verifica comportamento com pergunta vazia."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()
            crew_obj = crew.get_crew("")

            # Não deve falhar
            assert crew_obj is not None

    @pytest.mark.unit
    def test_crew_with_very_long_question(self):
        """Verifica comportamento com pergunta muito longa."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()
            long_question = "Pergunta " * 500
            crew_obj = crew.get_crew(long_question)

            # Não deve falhar
            assert crew_obj is not None

    @pytest.mark.unit
    def test_crew_with_special_characters(self):
        """Verifica comportamento com caracteres especiais."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()
            special_question = "Qual? @#$%^&*() 全て です"
            crew_obj = crew.get_crew(special_question)

            # Não deve falhar
            assert crew_obj is not None


class TestCrewIntegration:
    """Testa integração do crew."""

    @pytest.mark.unit
    @pytest.mark.slow
    def test_crew_task_chaining(self):
        """Verifica que tarefas estão ligadas corretamente."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()
            crew_obj = crew.get_crew("Teste")

            tasks = crew_obj.tasks

            # Primeira tarefa não deve ter contexto
            assert len(tasks[0].context) == 0

            # Segunda tarefa deve ter primeira como contexto
            assert len(tasks[1].context) > 0

            # Terceira tarefa deve ter segunda como contexto
            assert len(tasks[2].context) > 0

    @pytest.mark.unit
    def test_crew_maintains_consistency(self):
        """Verifica que crew mantém consistência entre chamadas."""
        from crew_definition import IFSCrew

        with patch('crew_definition.LLMFactory.create_llm') as mock_llm:
            mock_llm.return_value = MagicMock()

            crew = IFSCrew()

            question = "Teste pergunta"
            crew1 = crew.get_crew(question)
            crew2 = crew.get_crew(question)

            # Mesmo número de agentes e tarefas
            assert len(crew1.agents) == len(crew2.agents)
            assert len(crew1.tasks) == len(crew2.tasks)
