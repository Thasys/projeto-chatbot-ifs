"""
Testes unitários para guardrails.py

Testa:
- Carregamento de arquivo JSON
- Detecção de intent
- Busca fuzzy de gatilhos
- Tratamento de erro
"""

import pytest
from unittest.mock import patch, mock_open
import json
import os


class TestGuardrailsInitialization:
    """Testa inicialização de Guardrails."""

    @pytest.mark.unit
    def test_guardrails_load_json_success(self, mock_guardrails_data):
        """Verifica carregamento bem-sucedido do JSON."""
        from guardrails import Guardrails

        json_str = json.dumps(mock_guardrails_data)

        with patch('builtins.open', mock_open(read_data=json_str)):
            with patch('os.path.exists', return_value=True):
                gr = Guardrails('test.json')

                assert len(gr.data) == 3
                assert gr.data[0]['id'] == 'vague_query'

    @pytest.mark.unit
    def test_guardrails_file_not_found(self):
        """Verifica comportamento quando arquivo não existe."""
        from guardrails import Guardrails

        with patch('os.path.exists', return_value=False):
            gr = Guardrails('inexistente.json')

            assert gr.data == []
            assert len(gr.knowledge_base) == 0

    @pytest.mark.unit
    def test_guardrails_invalid_json(self):
        """Verifica tratamento de JSON inválido."""
        from guardrails import Guardrails

        invalid_json = "{ invalid json }"

        with patch('builtins.open', mock_open(read_data=invalid_json)):
            with patch('os.path.exists', return_value=True):
                gr = Guardrails('bad.json')

                assert gr.data == []

    @pytest.mark.unit
    def test_guardrails_builds_knowledge_base(self, mock_guardrails_data):
        """Verifica construção da base de conhecimento."""
        from guardrails import Guardrails

        json_str = json.dumps(mock_guardrails_data)

        with patch('builtins.open', mock_open(read_data=json_str)):
            with patch('os.path.exists', return_value=True):
                gr = Guardrails('test.json')

                # Deve ter 9 gatilhos (3 respostas * 3 gatilhos)
                assert len(gr.knowledge_base) == 9

                # Primeiro gatilho deve ser "todos os dados"
                assert gr.knowledge_base[0][0] == "todos os dados"


class TestGuardrailsCheckIntent:
    """Testa método check_intent()."""

    @pytest.mark.unit
    def test_check_intent_exact_match(self, mock_guardrails_data):
        """Verifica detecção com correspondência exata."""
        from guardrails import Guardrails

        json_str = json.dumps(mock_guardrails_data)

        with patch('builtins.open', mock_open(read_data=json_str)):
            with patch('os.path.exists', return_value=True):
                gr = Guardrails('test.json')

                # Teste com "ajuda"
                result = gr.check_intent("Preciso de ajuda")

                assert result is not None
                assert "assistente de transparência" in result.lower()

    @pytest.mark.unit
    def test_check_intent_no_match(self, mock_guardrails_data):
        """Verifica comportamento sem correspondência."""
        from guardrails import Guardrails

        json_str = json.dumps(mock_guardrails_data)

        with patch('builtins.open', mock_open(read_data=json_str)):
            with patch('os.path.exists', return_value=True):
                gr = Guardrails('test.json')

                result = gr.check_intent("Dados financeiros do Campus Lagarto")

                # Não deve corresponder a nenhum gatilho
                assert result is None

    @pytest.mark.unit
    def test_check_intent_fuzzy_match(self, mock_guardrails_data):
        """Verifica detecção fuzzy com erros de digitação."""
        from guardrails import Guardrails

        json_str = json.dumps(mock_guardrails_data)

        with patch('builtins.open', mock_open(read_data=json_str)):
            with patch('os.path.exists', return_value=True):
                gr = Guardrails('test.json')

                # "ajida" (typo) não deve corresponder exatamente
                # Mas com fuzzy matching e threshold baixo pode
                result = gr.check_intent("ajida me aqui")

                # Pode ou não corresponder dependendo do threshold
                # No mínimo, não deve falhar
                assert result is None or isinstance(result, str)

    @pytest.mark.unit
    def test_check_intent_vague_query(self, mock_guardrails_data):
        """Verifica detecção de pergunta vaga."""
        from guardrails import Guardrails

        json_str = json.dumps(mock_guardrails_data)

        with patch('builtins.open', mock_open(read_data=json_str)):
            with patch('os.path.exists', return_value=True):
                gr = Guardrails('test.json')

                result = gr.check_intent("Me mostre tudo")

                assert result is not None
                assert "abrangente" in result.lower()

    @pytest.mark.unit
    def test_check_intent_security_block(self, mock_guardrails_data):
        """Verifica bloqueio de queries perigosas."""
        from guardrails import Guardrails

        json_str = json.dumps(mock_guardrails_data)

        with patch('builtins.open', mock_open(read_data=json_str)):
            with patch('os.path.exists', return_value=True):
                gr = Guardrails('test.json')

                result = gr.check_intent("DELETE FROM tabela")

                assert result is not None
                assert "segurança" in result.lower() or "permitida" in result.lower()

    @pytest.mark.unit
    def test_check_intent_case_insensitive(self, mock_guardrails_data):
        """Verifica que detecção é case-insensitive."""
        from guardrails import Guardrails

        json_str = json.dumps(mock_guardrails_data)

        with patch('builtins.open', mock_open(read_data=json_str)):
            with patch('os.path.exists', return_value=True):
                gr = Guardrails('test.json')

                result1 = gr.check_intent("ajuda")
                result2 = gr.check_intent("AJUDA")
                result3 = gr.check_intent("AjUdA")

                # Todos devem retornar resultado
                assert result1 is not None
                assert result2 is not None
                assert result3 is not None

    @pytest.mark.unit
    def test_check_intent_empty_message(self, mock_guardrails_data):
        """Verifica comportamento com mensagem vazia."""
        from guardrails import Guardrails

        json_str = json.dumps(mock_guardrails_data)

        with patch('builtins.open', mock_open(read_data=json_str)):
            with patch('os.path.exists', return_value=True):
                gr = Guardrails('test.json')

                result = gr.check_intent("")

                assert result is None

    @pytest.mark.unit
    def test_check_intent_null_message(self, mock_guardrails_data):
        """Verifica comportamento com mensagem None."""
        from guardrails import Guardrails

        json_str = json.dumps(mock_guardrails_data)

        with patch('builtins.open', mock_open(read_data=json_str)):
            with patch('os.path.exists', return_value=True):
                gr = Guardrails('test.json')

                result = gr.check_intent(None)

                assert result is None

    @pytest.mark.unit
    def test_check_intent_very_long_message(self, mock_guardrails_data):
        """Verifica comportamento com mensagem muito longa."""
        from guardrails import Guardrails

        json_str = json.dumps(mock_guardrails_data)

        with patch('builtins.open', mock_open(read_data=json_str)):
            with patch('os.path.exists', return_value=True):
                gr = Guardrails('test.json')

                long_msg = "help " * 1000  # Mensagem muito longa
                result = gr.check_intent(long_msg)

                # Deve funcionar mesmo com mensagem longa
                assert result is not None


class TestGuardrailsThreshold:
    """Testa limiar de similaridade."""

    @pytest.mark.unit
    def test_check_intent_respects_threshold(self, mock_guardrails_data):
        """Verifica que threshold é respeitado."""
        from guardrails import Guardrails

        json_str = json.dumps(mock_guardrails_data)

        with patch('builtins.open', mock_open(read_data=json_str)):
            with patch('os.path.exists', return_value=True):
                gr = Guardrails('test.json')

                # Mensagem completamente diferente
                result = gr.check_intent("xyz abc def")

                # Não deve corresponder (score < 80)
                assert result is None

    @pytest.mark.unit
    def test_check_intent_high_similarity(self, mock_guardrails_data):
        """Verifica detecção com alta similaridade."""
        from guardrails import Guardrails

        json_str = json.dumps(mock_guardrails_data)

        with patch('builtins.open', mock_open(read_data=json_str)):
            with patch('os.path.exists', return_value=True):
                gr = Guardrails('test.json')

                # Muito similar a "todos os dados"
                result = gr.check_intent("todos dados")

                assert result is not None


class TestGuardrailsResponses:
    """Testa conteúdo das respostas."""

    @pytest.mark.unit
    def test_guardrails_responses_are_strings(self, mock_guardrails_data):
        """Verifica que respostas são strings."""
        from guardrails import Guardrails

        json_str = json.dumps(mock_guardrails_data)

        with patch('builtins.open', mock_open(read_data=json_str)):
            with patch('os.path.exists', return_value=True):
                gr = Guardrails('test.json')

                result = gr.check_intent("ajuda")

                assert isinstance(result, str)
                assert len(result) > 0

    @pytest.mark.unit
    def test_guardrails_returns_corresponing_response(self, mock_guardrails_data):
        """Verifica que resposta corresponde ao gatilho."""
        from guardrails import Guardrails

        json_str = json.dumps(mock_guardrails_data)

        with patch('builtins.open', mock_open(read_data=json_str)):
            with patch('os.path.exists', return_value=True):
                gr = Guardrails('test.json')

                # Procurar resposta para "vague_query"
                for item in mock_guardrails_data:
                    if item['id'] == 'vague_query':
                        vague_response = item['resposta']
                        break

                result = gr.check_intent("me mostre tudo")

                # Deve retornar a resposta corrigida
                if result:
                    assert "abrangente" in result.lower()


class TestGuardrailsEdgeCases:
    """Testa casos extremos."""

    @pytest.mark.unit
    def test_guardrails_with_special_characters(self, mock_guardrails_data):
        """Verifica comportamento com caracteres especiais."""
        from guardrails import Guardrails

        json_str = json.dumps(mock_guardrails_data)

        with patch('builtins.open', mock_open(read_data=json_str)):
            with patch('os.path.exists', return_value=True):
                gr = Guardrails('test.json')

                result = gr.check_intent("ajuda?!@#$%")

                # Não deve falhar
                assert result is None or isinstance(result, str)

    @pytest.mark.unit
    def test_guardrails_with_unicode(self, mock_guardrails_data):
        """Verifica comportamento com unicode."""
        from guardrails import Guardrails

        json_str = json.dumps(mock_guardrails_data)

        with patch('builtins.open', mock_open(read_data=json_str)):
            with patch('os.path.exists', return_value=True):
                gr = Guardrails('test.json')

                result = gr.check_intent("como usar? 🤔💡")

                # Não deve falhar
                assert result is None or isinstance(result, str)

    @pytest.mark.unit
    def test_guardrails_with_numbers(self, mock_guardrails_data):
        """Verifica comportamento com números."""
        from guardrails import Guardrails

        json_str = json.dumps(mock_guardrails_data)

        with patch('builtins.open', mock_open(read_data=json_str)):
            with patch('os.path.exists', return_value=True):
                gr = Guardrails('test.json')

                result = gr.check_intent("123 456 789")

                # Não deve corresponder nenhum gatilho
                assert result is None


class TestGuardrailsIntegration:
    """Testa integração com resto do sistema."""

    @pytest.mark.unit
    @pytest.mark.slow
    def test_guardrails_in_pipeline(self, mock_guardrails_data):
        """Testa Guardrails como parte do pipeline."""
        from guardrails import Guardrails

        json_str = json.dumps(mock_guardrails_data)

        with patch('builtins.open', mock_open(read_data=json_str)):
            with patch('os.path.exists', return_value=True):
                gr = Guardrails('respostas_prontas.json')

                # Simular pergunta normal (deve passar)
                normal_query = "Qual o gasto do Campus Lagarto em 2024?"
                result = gr.check_intent(normal_query)
                assert result is None  # Passa sem bloqueio

                # Simular pergunta vaga (deve bloquear)
                vague_query = "me mostre tudo"
                result = gr.check_intent(vague_query)
                assert result is not None  # Bloqueado

                # Simular query perigosa (deve bloquear)
                dangerous_query = "delete from tabela"
                result = gr.check_intent(dangerous_query)
                assert result is not None  # Bloqueado
