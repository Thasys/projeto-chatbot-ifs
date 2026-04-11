import unittest
import pandas as pd
import os
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from extractor import DataExtractor
from etl_scripts.transformer_v1 import DataTransformer
from loader import DataLoader


class TestDataExtractor(unittest.TestCase):
    """Testes para a classe DataExtractor."""

    def setUp(self):
        self.extractor = DataExtractor()

    def test_gerar_datas_validas(self):
        """Testa geração de datas válidas."""
        with patch('extractor.Config') as mock_config:
            mock_config.DATA_INICIO = "01/01/2024"
            mock_config.DATA_FIM = "03/01/2024"

            extractor = DataExtractor()
            datas = extractor._gerar_datas()

            self.assertEqual(len(datas), 3)
            self.assertEqual(datas[0], "01/01/2024")

    def test_gerar_datas_invalidas(self):
        """Testa geração com datas inválidas."""
        with patch('extractor.Config') as mock_config:
            mock_config.DATA_INICIO = "31/02/2024"  # Data inválida
            mock_config.DATA_FIM = "01/03/2024"

            extractor = DataExtractor()
            datas = extractor._gerar_datas()

            self.assertEqual(len(datas), 0)

    def test_detectar_duplicatas(self):
        """Testa detecção de duplicatas."""
        dados = [
            {'documento': '001', 'valor': '100.00', 'dataEmissao': '2024-01-01'},
            {'documento': '001', 'valor': '100.00',
                'dataEmissao': '2024-01-01'},  # Duplicata
            {'documento': '002', 'valor': '200.00', 'dataEmissao': '2024-01-02'},
        ]

        dados_unicos, dup_count = self.extractor._detectar_duplicatas(dados)

        self.assertEqual(len(dados_unicos), 2)
        self.assertEqual(dup_count, 1)

    def test_validar_registro_api_valido(self):
        """Testa validação de registro válido."""
        registro = {
            'documento': '001',
            'valor': '100.00',
            'dataEmissao': '2024-01-01',
            'codigoUg': 'UG001',
            'ug': 'Campus Aracaju'
        }

        resultado = self.extractor._validar_registro_api(registro)
        self.assertTrue(resultado)

    def test_validar_registro_api_invalido(self):
        """Testa validação de registro inválido (campo ausente)."""
        registro = {
            'documento': '001',
            'valor': '100.00',
            # dataEmissao ausente
            'codigoUg': 'UG001',
            'ug': 'Campus Aracaju'
        }

        resultado = self.extractor._validar_registro_api(registro)
        self.assertFalse(resultado)

    @patch('requests.get')
    def test_requisicao_com_retry_sucesso(self, mock_get):
        """Testa requisição com retry bem-sucedida."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'documento': '001', 'valor': '100.00'}]
        mock_get.return_value = mock_response

        resultado = self.extractor._requisicao_com_retry(
            {'dataEmissao': '01/01/2024'})

        self.assertIsNotNone(resultado)
        self.assertEqual(len(resultado), 1)

    @patch('requests.get')
    def test_requisicao_com_retry_falha(self, mock_get):
        """Testa requisição com retry após falhas."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with patch('time.sleep'):  # Mock sleep para acelerar teste
            resultado = self.extractor._requisicao_com_retry(
                {'dataEmissao': '01/01/2024'}, max_retries=2
            )

        self.assertIsNone(resultado)


class TestDataTransformer(unittest.TestCase):
    """Testes para a classe DataTransformer."""

    def setUp(self):
        self.transformer = DataTransformer()

    def test_clean_currency_valido(self):
        """Testa limpeza de moeda válida."""
        resultado = DataTransformer.clean_currency("1.234,56")
        self.assertEqual(resultado, 1234.56)

    def test_clean_currency_negativo(self):
        """Testa limpeza de moeda negativa."""
        resultado = DataTransformer.clean_currency("- 100,50")
        self.assertEqual(resultado, -100.50)

    def test_clean_currency_nulo(self):
        """Testa limpeza de moeda nula."""
        resultado = DataTransformer.clean_currency(None)
        self.assertEqual(resultado, 0.0)

    def test_clean_currency_invalido(self):
        """Testa limpeza de moeda inválida."""
        resultado = DataTransformer.clean_currency("INVALIDO")
        self.assertEqual(resultado, 0.0)

    def test_split_cod_desc_valido(self):
        """Testa separação código/descrição válida."""
        cod, desc = DataTransformer.split_cod_desc("01 - DESPESA CORRENTE")
        self.assertEqual(cod, "01")
        self.assertEqual(desc, "DESPESA CORRENTE")

    def test_split_cod_desc_multiplos_hifens(self):
        """Testa separação com múltiplos hífens."""
        cod, desc = DataTransformer.split_cod_desc(
            "01 - DESCRIÇÃO - COM - VÁRIOS - HÍFENS")
        self.assertEqual(cod, "01")
        self.assertEqual(desc, "DESCRIÇÃO - COM - VÁRIOS - HÍFENS")

    def test_split_cod_desc_sem_hifen(self):
        """Testa separação sem hífen."""
        cod, desc = DataTransformer.split_cod_desc("APENAS_TEXTO")
        self.assertEqual(cod, "APENAS_TEXTO")
        self.assertEqual(desc, "APENAS_TEXTO")

    def test_validar_dados_entrada(self):
        """Testa validação de dados de entrada."""
        df = pd.DataFrame({
            'valor': ['100,00', '200,00', None],
            'data': ['01/01/2024', '02/01/2024', '03/01/2024'],
            'codigoFavorecido': ['FAV001', 'FAV002', ''],
            'nomeFavorecido': ['Empresa A', 'Empresa B', 'Empresa C'],
            'codigoUg': ['UG001', 'UG002', 'UG003'],
            'ug': ['Campus 1', 'Campus 2', 'Campus 3'],
            'categoria': ['01 - CAT A', '02 - CAT B', '03 - CAT C'],
            'grupo': ['01 - GRP A', '01 - GRP B', '01 - GRP C'],
            'modalidade': ['01 - MOD A', '01 - MOD B', '01 - MOD C'],
            'elemento': ['01 - ELE A', '01 - ELE B', '01 - ELE C']
        })

        df_valido, rejeicoes = self.transformer._validar_dados_entrada(df)

        # Deve rejeitar a linha 3 (codigoFavorecido vazio)
        self.assertEqual(len(rejeicoes), 1)
        self.assertEqual(len(df_valido), 2)

    def test_detectar_duplicatas_dimensao(self):
        """Testa detecção de duplicatas em dimensão."""
        df = pd.DataFrame({
            'codigoFavorecido': ['FAV001', 'FAV001', 'FAV002'],
            'nomeFavorecido': ['Empresa A', 'Empresa A', 'Empresa B'],
            'ufFavorecido': ['BA', 'BA', 'SE']
        })

        resultado = self.transformer._detectar_duplicatas_dimensao(
            df, 'dim_favorecido', ['codigoFavorecido']
        )

        self.assertEqual(resultado['total_duplicatas'], 1)


class TestDataLoader(unittest.TestCase):
    """Testes para a classe DataLoader."""

    def setUp(self):
        self.loader = DataLoader()

    def test_validar_dados_validos(self):
        """Testa validação de dados válidos."""
        df = pd.DataFrame({
            'codigoFavorecido': ['FAV001', 'FAV002'],
            'nomeFavorecido': ['Empresa A', 'Empresa B'],
            'valor': [100.0, 200.0],
            'data': ['2024-01-01', '2024-01-02']
        })

        df_valido, rejeicoes = self.loader._validar_dados(
            df, 'dim_favorecido', 'codigoFavorecido'
        )

        self.assertEqual(len(df_valido), 2)
        self.assertEqual(len(rejeicoes), 0)

    def test_validar_dados_chave_vazia(self):
        """Testa validação com chave única vazia."""
        df = pd.DataFrame({
            'codigoFavorecido': ['FAV001', '', 'FAV003'],
            'nomeFavorecido': ['Empresa A', 'Empresa B', 'Empresa C'],
        })

        df_valido, rejeicoes = self.loader._validar_dados(
            df, 'dim_favorecido', 'codigoFavorecido'
        )

        self.assertEqual(len(rejeicoes), 1)
        self.assertEqual(len(df_valido), 2)


class TestIntegrationETL(unittest.TestCase):
    """Testes de integração do pipeline ETL."""

    @patch('extractor.DataExtractor.carregar_backup_local')
    @patch('loader.DataLoader.carregar_mysql')
    def test_pipeline_completo(self, mock_loader, mock_extractor):
        """Testa pipeline ETL completo."""
        # Mock dos dados de entrada
        df_entrada = pd.DataFrame({
            'valor': ['100,00', '200,00'],
            'data': ['01/01/2024', '02/01/2024'],
            'codigoFavorecido': ['FAV001', 'FAV002'],
            'nomeFavorecido': ['Empresa A', 'Empresa B'],
            'ufFavorecido': ['BA', 'SE'],
            'codigoUg': ['UG001', 'UG002'],
            'ug': ['Campus Aracaju', 'Campus Lagarto'],
            'codigoOrgao': ['ORG001', 'ORG002'],
            'orgao': ['Reitoria', 'Campus'],
            'funcao': ['01 - EDUCAÇÃO', '01 - EDUCAÇÃO'],
            'subfuncao': ['001 - SUPERIOR', '001 - SUPERIOR'],
            'programa': ['001 - PROGRAMA', '001 - PROGRAMA'],
            'acao': ['0001 - AÇÃO', '0001 - AÇÃO'],
            'categoria': ['01 - CAT', '01 - CAT'],
            'grupo': ['001 - GRP', '001 - GRP'],
            'modalidade': ['01 - MOD', '01 - MOD'],
            'elemento': ['01 - ELE', '01 - ELE'],
            'documento': ['DOC001', 'DOC002'],
            'numeroProcesso': ['PROC001', 'PROC002'],
            'observacao': ['Obs 1', 'Obs 2'],
            'dataEmissao': ['2024-01-01', '2024-01-02']
        })

        mock_extractor.return_value = df_entrada

        # Executar transformação
        transformer = DataTransformer()
        dados_transformados = transformer.processar(df_entrada)

        # Validações
        self.assertIsNotNone(dados_transformados)
        self.assertIn('dim_favorecido', dados_transformados)
        self.assertIn('fato_execucao', dados_transformados)
        self.assertEqual(len(dados_transformados['dim_favorecido']), 2)
        self.assertEqual(len(dados_transformados['fato_execucao']), 2)


class TestETLPerformance(unittest.TestCase):
    """Testes de performance do ETL."""

    def test_transformer_performance_1000_registros(self):
        """Testa performance com 1000 registros."""
        import time

        df_grande = pd.DataFrame({
            'valor': ['100,00'] * 1000,
            'data': ['01/01/2024'] * 1000,
            'codigoFavorecido': [f'FAV{i:03d}' for i in range(1000)],
            'nomeFavorecido': [f'Empresa {i}' for i in range(1000)],
            'ufFavorecido': ['BA'] * 1000,
            'codigoUg': ['UG001'] * 1000,
            'ug': ['Campus'] * 1000,
            'codigoOrgao': ['ORG001'] * 1000,
            'orgao': ['Reitoria'] * 1000,
            'funcao': ['01 - EDUCAÇÃO'] * 1000,
            'subfuncao': ['001 - SUPERIOR'] * 1000,
            'programa': ['001 - PROGRAMA'] * 1000,
            'acao': ['0001 - AÇÃO'] * 1000,
            'categoria': ['01 - CAT'] * 1000,
            'grupo': ['001 - GRP'] * 1000,
            'modalidade': ['01 - MOD'] * 1000,
            'elemento': ['01 - ELE'] * 1000,
            'documento': [f'DOC{i:04d}' for i in range(1000)],
            'numeroProcesso': [f'PROC{i:04d}' for i in range(1000)],
            'observacao': ['Obs'] * 1000,
            'dataEmissao': ['2024-01-01'] * 1000
        })

        transformer = DataTransformer()

        inicio = time.time()
        resultado = transformer.processar(df_grande)
        tempo_decorrido = time.time() - inicio

        print(
            f"\n⏱️ Tempo para transformar 1000 registros: {tempo_decorrido:.2f}s")
        self.assertLess(tempo_decorrido, 10)  # Deve ser menor que 10 segundos


def run_tests():
    """Executa todos os testes."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Adicionar testes
    suite.addTests(loader.loadTestsFromTestCase(TestDataExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestDataTransformer))
    suite.addTests(loader.loadTestsFromTestCase(TestDataLoader))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationETL))
    suite.addTests(loader.loadTestsFromTestCase(TestETLPerformance))

    # Executar
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    sucesso = run_tests()
    exit(0 if sucesso else 1)
