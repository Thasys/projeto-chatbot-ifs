import json
import re
from crewai import Agent, Task, Crew, Process
from tools import search_entity_fuzzy, search_sql_memory, execute_sql, export_csv
from llm_factory import LLMFactory
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, field
from typing import Optional, List

logger = logging.getLogger(__name__)


# ========== P0.3: CONFIDENCE SCORES ==========
@dataclass
class ResponseMetadata:
    """Metadados de resposta com confidence score."""
    confidence: float = 0.0  # 0-100%
    period_start: Optional[str] = None  # YYYY-MM-DD
    period_end: Optional[str] = None    # YYYY-MM-DD
    data_freshness_date: Optional[str] = None  # Última coleta
    warning_messages: List[str] = field(default_factory=list)
    confidence_factors: dict = field(
        default_factory=dict)  # Detalhes do cálculo


def calculate_confidence(
    has_entities: bool,
    entities_count: int,
    has_results: bool,
    data_is_recent: bool,
    fuzzy_match: bool = False,
    query_type: str = "generic"
) -> float:
    """
    Calcula score de confiança de 0-100%.

    Fatores de redução:
    - Entidades não encontradas: -30%
    - Dados antigos (>30 dias): -20%
    - Resultado vazio: -50%
    - Múltiplos matches fuzzy: -15%

    Args:
        has_entities: Se econtrou as entidades procuradas
        entities_count: Quantas entidades foram encontradas
        has_results: Se a query retornou resultados
        data_is_recent: Se dados foram coletados recentemente
        fuzzy_match: Se usou busca fuzzy (menos preciso)
        query_type: Tipo de query (generic, sum, ranking, etc)

    Returns:
        float: Score de 0-100%
    """

    base_confidence = 100.0
    penalties = {}

    # Penalidade 1: Entidades não encontradas
    if not has_entities or entities_count == 0:
        penalties['no_entities'] = 30
        base_confidence -= 30
    elif entities_count == 1:
        penalties['single_entity'] = 5  # Menos confiante com 1 entidade
        base_confidence -= 5

    # Penalidade 2: Dados antigos
    if not data_is_recent:
        penalties['old_data'] = 20
        base_confidence -= 20

    # Penalidade 3: Resultado vazio
    if not has_results:
        penalties['no_results'] = 50
        base_confidence -= 50

    # Penalidade 4: Busca fuzzy (menos preciso)
    if fuzzy_match:
        penalties['fuzzy_match'] = 15
        base_confidence -= 15

    # Query type bonus
    if query_type == "ranking":
        base_confidence += 5  # Rankings são mais confiáveis

    # Garantir que não fica negativo
    final_confidence = max(10, min(100, base_confidence))  # Min 10%, Max 100%

    logger.debug(
        f"Confiança calculada: {final_confidence}% (penalidades: {penalties})")

    return final_confidence


class IFSCrewV2:
    """
    Versão melhorada com:
    - JSON mode (validação automática)
    - Timeout
    - Cache de queries
    - Mensagens de erro amigáveis
    """

    def __init__(self, use_json_mode: bool = True, cache_ttl: int = 300):
        self.llm_engine = LLMFactory.create_llm()
        self.use_json_mode = use_json_mode
        self.cache_ttl = cache_ttl
        self.query_cache = {}  # Cache simples em memória

    # ========== MELHORIA 1: JSON MODE DO OPENAI ==========
    def _extract_json_safe(self, text: str) -> dict:
        """
        Extrai JSON com múltiplos fallbacks.
        """
        try:
            # Tentativa 1: JSON puro
            return json.loads(text)
        except:
            pass

        try:
            # Tentativa 2: Regex para JSON
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except:
            pass

        # Fallback 3: Criar JSON de fallback com detecção automática
        text_lower = text.lower()
        fallback = {
            "intent": "SEARCH",
            "entities": [],
            "date_filter": None,
            "action": "EXECUTE_SQL"
        }

        if any(w in text_lower for w in ['top', 'maiores', 'ranking']):
            fallback['intent'] = 'RANKING'
        elif any(w in text_lower for w in ['total', 'quanto', 'soma']):
            fallback['intent'] = 'TOTAL'

        logger.warning(f"⚠️ JSON parsing com fallback: {fallback['intent']}")
        return fallback

    # ========== MELHORIA 2: CACHE DE QUERIES ==========
    def _obter_query_cached(self, user_question: str) -> str:
        """
        Retorna query do cache se existir e ainda for válida.
        """
        cache_key = hash(user_question) % 10000

        if cache_key in self.query_cache:
            cached_query, timestamp = self.query_cache[cache_key]

            # Verificar TTL
            if (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                logger.info(f"✅ Query do cache: {user_question[:50]}...")
                return cached_query

        return None

    def _cache_query(self, user_question: str, query: str):
        """Salva query no cache."""
        cache_key = hash(user_question) % 10000
        self.query_cache[cache_key] = (query, datetime.now())

    # ========== MELHORIA 3: PROMPTS MAIS ESPECÍFICOS ==========
    def get_crew(self, user_question: str):
        """Crew com melhorias de confiabilidade."""

        today = datetime.now()
        current_date_str = today.strftime("%Y-%m-%d")
        current_year = today.year
        last_month = (today.replace(day=1) -
                      timedelta(days=1)).strftime("%Y-%m")

        # ========== AGENTE 1: Data Detective (MELHORADO) ==========
        metadata_navigator = Agent(
            role='🔍 Data Detective',
            goal='Extract user intent, find entities using tools, and return VALID JSON.',
            backstory=(
                f"You are a JSON-outputting data extractor. Today: {current_date_str}. Year: {current_year}.\n"
                "CRITICAL RULES:\n"
                "1. ALWAYS output ONLY a valid JSON object (no text before/after)\n"
                "2. Identify intent: RANKING (user asks for 'top', 'maiores'), TOTAL (user asks for 'quanto', 'total'), or SEARCH\n"
                "3. Use 'Search Entity Fuzzy' tool to find entities\n"
                "4. Return JSON with these EXACT fields:\n"
                '   {"intent": "RANKING"|"TOTAL"|"SEARCH", "entities": [...], "date_filter": null, "action": "EXECUTE_SQL"}\n'
                "5. If entity not found, still return JSON\n"
                "\nExamples:\n"
                '- User: "Top 5 fornecedores" → {"intent": "RANKING", ...}\n'
                '- User: "Quanto para Energisa" → {"intent": "TOTAL", "entities": [...], ...}\n'
            ),
            tools=[search_entity_fuzzy],
            verbose=True,
            allow_delegation=False,
            llm=self.llm_engine
        )

        # ========== AGENTE 2: SQL Architect (MELHORADO) ==========
        sql_architect = Agent(
            role='🏗️ SQL Expert',
            goal='Generate and execute SQL queries based on JSON input.',
            backstory=(
                "You are a SQL execution engine. You receive JSON and build queries.\n"
                "SCHEMA: v_financas_geral (data, valor, favorecido_nome, id_favorecido, id_ug, tipo_despesa, id_programa, id_natureza)\n"
                "PATTERNS:\n"
                "- RANKING: SELECT col, SUM(valor) ... GROUP BY ... ORDER BY DESC LIMIT 5\n"
                "- TOTAL: SELECT SUM(valor)\n"
                "- Check 'Search SQL Memory' for similar queries\n"
                "- ALWAYS execute with 'Execute SQL Query' tool\n"
            ),
            tools=[search_sql_memory, execute_sql, export_csv],
            verbose=True,
            allow_delegation=False,
            llm=self.llm_engine
        )

        # ========== AGENTE 3: Analyst (MELHORADO) ==========
        public_data_analyst = Agent(
            role='📊 Public Transparency Analyst',
            goal='Explain SQL results in clear Portuguese.',
            backstory=(
                "You are a transparency expert. Transform SQL results into PT-BR explanations.\n"
                "RULES:\n"
                "- Format money: R$ X.XXX,XX\n"
                "- Highlight top insights\n"
                "- If no data: explain why\n"
                "- Always cite source: 'Segundo os dados do IFS...'\n"
            ),
            verbose=True,
            allow_delegation=False,
            llm=self.llm_engine
        )

        # ========== TASKS (COM TIMEOUTS E ESPECIFICIDADE) ==========
        task_mapping = Task(
            description=(
                f"Analyze: '{user_question}'\n"
                f"Date context: {current_date_str} | Year: {current_year} | Last month: {last_month}\n"
                "OUTPUT ONLY VALID JSON (no markdown, no text)"
            ),
            expected_output="Valid JSON object with intent, entities, date_filter",
            agent=metadata_navigator
        )

        task_query = Task(
            description=(
                "Parse JSON from Data Detective.\n"
                "Generate SQL based on intent:\n"
                "- RANKING: GROUP BY + ORDER BY DESC + LIMIT 5\n"
                "- TOTAL: SUM(valor)\n"
                "- SEARCH: WHERE filters\n"
                "Use 'Search SQL Memory' for reference.\n"
                "Execute with 'Execute SQL Query'."
            ),
            expected_output="Markdown table with results",
            agent=sql_architect,
            context=[task_mapping]
        )

        task_response = Task(
            description=(
                "Translate SQL results to PT-BR.\n"
                "Format: R$ X.XXX,XX for money.\n"
                "Start with: 'Segundo os dados do IFS...'"
            ),
            expected_output="Clear Portuguese explanation",
            agent=public_data_analyst,
            context=[task_query]
        )

        return Crew(
            agents=[metadata_navigator, sql_architect, public_data_analyst],
            tasks=[task_mapping, task_query, task_response],
            process=Process.sequential,
            verbose=True,
            memory=True
        )

    def execute_with_timeout(self, crew, user_question: str, timeout: int = 60):
        """
        Executa crew com timeout.
        Nota: Timeout via signal.SIGALRM não funciona no Windows.
        No Windows, apenas executa normalmente sem timeout.
        """
        import platform
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError(f"Query timeout após {timeout}s")

        try:
            # SIGALRM só existe em Unix/Linux, não no Windows
            if platform.system() != 'Windows':
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout)

            resultado = crew.kickoff()

            if platform.system() != 'Windows':
                signal.alarm(0)  # Cancelar alarm

            return resultado

        except TimeoutError as e:
            logger.error(f"❌ {e}")
            return f"⏱️ Operação demorou muito. Tente uma pergunta mais específica."

        except Exception as e:
            logger.error(f"❌ Erro: {e}")
            return f"❌ Erro na processamento. Detalhes: {str(e)[:100]}"

    def execute_with_confidence(self, crew, user_question: str, timeout: int = 60) -> dict:
        """
        Executa crew e retorna resposta com score de confiança (P0.3).

        Returns:
            dict: {
                'resposta': str,
                'confidence': float (0-100),
                'metadata': ResponseMetadata,
                'periodo_inicio': str (YYYY-MM-DD),
                'periodo_fim': str (YYYY-MM-DD),
                'warnings': list
            }
        """

        import signal
        import platform
        from datetime import datetime, timedelta

        def timeout_handler(signum, frame):
            raise TimeoutError(f"Query timeout após {timeout}s")

        # SIGALRM só existe em Unix/Linux, não no Windows
        use_alarm = platform.system() != 'Windows'
        
        try:
            # Inicia alarm (apenas Unix/Linux)
            if use_alarm:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout)
                logger.debug(f"⏰ Signal alarm ativado para {timeout}s")

            # Executar crew
            logger.info(f"🚀 Crew iniciando para: {user_question[:50]}...")
            resultado = crew.kickoff()
            logger.info(f"✅ Crew completado com sucesso")

            # ========== P0.3: EXTRAIR METADADOS ==========
            # Analisar resposta para determinar confiança
            resposta_lower = str(resultado).lower()

            # Verificar fatores de confiança
            tem_dados = not any(word in resposta_lower for word in [
                'nenhum', 'não encontr', 'sem resulta', 'vazio', 'nada'
            ])

            dados_recentes = not any(word in resposta_lower for word in [
                'antigo', 'ultrapassado', 'obsoleto', 'atualiz'
            ]) or 'atualizado' in resposta_lower

            tem_valores = any(char in str(resultado)
                              for char in ['R$', '0123456789'])

            # Calcular confiança
            confidence = calculate_confidence(
                has_entities=tem_valores,
                entities_count=1 if tem_valores else 0,
                has_results=tem_dados,
                data_is_recent=dados_recentes,
                fuzzy_match=False,
                query_type="generic"
            )

            # Criar metadados
            now = datetime.now()
            metadata = ResponseMetadata(
                confidence=confidence,
                period_start=now.replace(month=1, day=1).strftime('%Y-%m-%d'),
                period_end=now.strftime('%Y-%m-%d'),
                data_freshness_date=now.strftime('%Y-%m-%d'),
                warning_messages=[]
            )

            # Adicionar avisos se necessário
            if confidence < 50:
                metadata.warning_messages.append(
                    "⚠️ Baixa confiança na resposta")
            if not dados_recentes:
                metadata.warning_messages.append(
                    "⚠️ Dados podem estar desatualizados")

            logger.info(f"✅ Resposta com confiança: {confidence}%")

            return {
                'resposta': resultado,
                'confidence': confidence,
                'metadata': metadata,
                'periodo_inicio': metadata.period_start,
                'periodo_fim': metadata.period_end,
                'warnings': metadata.warning_messages
            }

        except TimeoutError as e:
            logger.error(f"❌ Timeout: {e}")
            resposta_erro = "⏱️ Operação demorou muito. Tente uma pergunta mais específica."
            return {
                'resposta': resposta_erro,
                'confidence': 10.0,
                'metadata': ResponseMetadata(confidence=10.0),
                'periodo_inicio': None,
                'periodo_fim': None,
                'warnings': ['Operação com timeout']
            }

        except Exception as e:
            logger.error(f"❌ Erro na execução do crew: {type(e).__name__}: {str(e)[:500]}")
            resposta_erro = f"❌ Erro no processamento. Detalhes: {str(e)[:100]}"
            return {
                'resposta': resposta_erro,
                'confidence': 0.0,
                'metadata': ResponseMetadata(confidence=0.0),
                'periodo_inicio': None,
                'periodo_fim': None,
                'warnings': [f'Erro: {type(e).__name__}']
            }
        
        finally:
            # ✅ CRÍTICO: SEMPRE cancelar o alarm, mesmo em exceção
            if use_alarm:
                try:
                    signal.alarm(0)  # Cancela o alarm
                    logger.debug("✅ Signal alarm cancelado")
                except Exception as cancel_error:
                    logger.warning(f"⚠️ Erro ao cancelar alarm: {cancel_error}")
