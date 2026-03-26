import json
import re
from crewai import Agent, Task, Crew, Process
from tools import search_entity_fuzzy, search_sql_memory, execute_sql, export_csv
from llm_factory import LLMFactory
from datetime import datetime, timedelta


class IFSCrew:
    def __init__(self):
        self.llm_engine = LLMFactory.create_llm()

    def _extract_json_from_text(self, text: str) -> dict:
        """
        Extrai JSON válido do texto da resposta do agente.
        Se não encontrar, retorna um JSON de fallback com a intenção detectada.
        """
        try:
            # Tenta encontrar JSON entre { e }
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
        except (json.JSONDecodeError, AttributeError):
            pass

        # FALLBACK: Se JSON falhar, detecta intenção automaticamente
        text_lower = text.lower()

        fallback = {
            "action": "EXECUTE_SQL",
            "intent": None,
            "entities": [],
            "date_filter": None,
            "raw_response": text
        }

        if any(word in text_lower for word in ['top', 'maiores', 'maior', 'ranking', 'quais']):
            fallback["intent"] = "RANKING"
        elif any(word in text_lower for word in ['total', 'quanto', 'suma', 'somme']):
            fallback["intent"] = "TOTAL"
        else:
            fallback["intent"] = "SEARCH"

        print(
            f"⚠️ JSON parsing failed. Using fallback intent: {fallback['intent']}")
        return fallback

    def get_crew(self, user_question):
        # --- 1. CONTEXTO TEMPORAL ---
        today = datetime.now()
        current_date_str = today.strftime("%Y-%m-%d")
        current_year = today.year
        last_month = (today.replace(day=1) -
                      timedelta(days=1)).strftime("%Y-%m")

        # --- AGENTS ---

        metadata_navigator = Agent(
            role='🔍 Data Detective',
            goal='Extract user intent, find entities using tools, and return structured JSON.',
            backstory=(
                f"You are a precise data extractor. Today is {current_date_str}. Current year is {current_year}.\n"
                "Your ONLY job is to:\n"
                "1. Identify the user INTENT:\n"
                "   - 'RANKING': User asks for 'Top X', 'Maiores', 'Maiores fornecedores'\n"
                "   - 'TOTAL': User asks for 'Quanto', 'Total', 'Soma'\n"
                "   - 'SEARCH': User asks for specific entity details\n"
                "2. Find ENTITIES (if any) using 'Search Entity Fuzzy' tool. Extract proper nouns.\n"
                "3. Detect DATE CONTEXT:\n"
                "   - 'este ano' -> {current_year}\n"
                "   - 'mês passado' -> {last_month}\n"
                "   - 'janeiro' / 'junho' -> current year if not specified\n"
                "4. Output VALID JSON (no markdown, no extra text).\n"
                "\n"
                "CRITICAL: Your output MUST be valid JSON. No extra text before or after."
            ),
            tools=[search_entity_fuzzy],
            verbose=True,
            allow_delegation=False,
            llm=self.llm_engine
        )

        sql_architect = Agent(
            role='🏗️ Senior SQL Architect',
            goal='Translate JSON intent into SQL queries and EXECUTE them.',
            backstory=(
                "You are a SQL execution engine. You receive JSON with intent/entities/filters.\n"
                "DATABASE SCHEMA: v_financas_geral\n"
                "COLUMNS: data, valor, favorecido_nome, unidade_pagadora, id_favorecido, id_ug, tipo_despesa, programa_governo\n"
                "\n"
                "SQL RULES:\n"
                "- RANKING: SELECT favorecido_nome, SUM(valor) as total GROUP BY favorecido_nome ORDER BY total DESC LIMIT 5\n"
                "- TOTAL: SELECT SUM(valor) as total_gasto\n"
                "- SEARCH: SELECT * with specific WHERE filters\n"
                "- DATE FILTER: Use WHERE data BETWEEN 'YYYY-01-01' AND 'YYYY-12-31'\n"
                "- ENTITY FILTER: Use WHERE id_favorecido = X or id_ug = X\n"
                "\n"
                "After generating SQL:\n"
                "1. Use 'Search SQL Memory' to validate syntax\n"
                "2. Use 'Execute SQL Query' to run it\n"
                "3. Format results as Markdown table"
            ),
            tools=[search_sql_memory, execute_sql, export_csv],
            verbose=True,
            allow_delegation=False,
            llm=self.llm_engine
        )

        public_data_analyst = Agent(
            role='📊 Public Transparency Analyst',
            goal='Transform SQL results into clear, helpful Portuguese explanations.',
            backstory=(
                "You are a public sector transparency expert. Your job is to:\n"
                "1. Read the SQL result from the SQL Architect\n"
                "2. Translate technical data into CLEAR PORTUGUESE (PT-BR)\n"
                "3. Format money as 'R$ X.XXX,XX' (Brazilian standard)\n"
                "4. Highlight key insights\n"
                "5. If no data, explain why (e.g., 'No transactions found for this period')\n"
                "\n"
                "Be helpful, honest, and always reference the data shown."
            ),
            verbose=True,
            allow_delegation=False,
            llm=self.llm_engine
        )

        # --- TASKS ---

        task_mapping = Task(
            description=(
                f"Analyze this user question: '{user_question}'\n\n"
                f"CONTEXT:\n"
                f"- Today's date: {current_date_str}\n"
                f"- Current year: {current_year}\n"
                f"- Last month: {last_month}\n\n"
                "INSTRUCTIONS:\n"
                "1. Identify the INTENT (RANKING, TOTAL, or SEARCH)\n"
                "2. Extract any PROPER NOUNS (company names, campus names, etc) - use 'Search Entity Fuzzy' tool\n"
                "3. Detect DATE REFERENCES in the question\n"
                "4. Output ONLY valid JSON with no extra text.\n\n"
                "JSON FORMAT (MANDATORY):\n"
                "{\n"
                '  "intent": "RANKING" | "TOTAL" | "SEARCH",\n'
                '  "entities": [{"type": "UG", "name": "...", "id": ...}, ...],\n'
                '  "date_filter": {"year": 2024, "month": 6} or null,\n'
                '  "action": "EXECUTE_SQL"\n'
                "}"
            ),
            expected_output="Valid JSON object (no markdown, no extra text)",
            agent=metadata_navigator
        )

        task_query = Task(
            description=(
                "You received JSON from the Data Detective with user intent and entities.\n\n"
                "INSTRUCTIONS:\n"
                "1. Parse the JSON carefully\n"
                "2. Based on INTENT, generate SQL:\n"
                "   - RANKING: GROUP BY + ORDER BY DESC + LIMIT 5\n"
                "   - TOTAL: SUM(valor)\n"
                "   - SEARCH: Filter by entity IDs\n"
                "3. Apply DATE FILTER if present\n"
                "4. Use 'Search SQL Memory' to find similar queries as reference\n"
                "5. EXECUTE the SQL using 'Execute SQL Query' tool\n"
                "6. Return the result as a formatted table\n\n"
                "TABLE SCHEMA REMINDER: v_financas_geral (data, valor, favorecido_nome, unidade_pagadora, id_favorecido, id_ug, tipo_despesa, programa_governo)"
            ),
            expected_output="Markdown formatted table with SQL results",
            agent=sql_architect,
            context=[task_mapping]
        )

        task_response = Task(
            description=(
                "You received SQL results from the SQL Architect.\n\n"
                "INSTRUCTIONS:\n"
                "1. Read the table/data provided\n"
                "2. Write a CLEAR PORTUGUESE (PT-BR) explanation of the results\n"
                "3. Format money values as 'R$ X.XXX,XX' (Brazilian format)\n"
                "4. Highlight the TOP insights\n"
                "5. If no data was returned, explain why and suggest alternatives\n"
                "6. Always mention data source: 'Segundo os dados do IFS...'\n\n"
                "Example response:\n"
                "'Segundo os dados do IFS, os 3 maiores fornecedores foram:\n"
                "1. Empresa X - R$ 1.500.000,00\n"
                "2. Empresa Y - R$ 1.200.000,00\n"
                "...'"
            ),
            expected_output="Natural language response in Portuguese (PT-BR) with formatted results",
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
