from crewai import Agent, Task, Crew, Process
from tools import DatabaseTools
from llm_factory import LLMFactory
from datetime import datetime  # <--- IMPORTANTE


class IFSCrew:
    def __init__(self):
        self.llm_engine = LLMFactory.create_llm()

    def get_crew(self, user_question):

        # --- 1. CONTEXTO TEMPORAL ---
        # Pegamos a data de hoje para o agente não se perder no tempo
        today = datetime.now()
        current_date_str = today.strftime("%Y-%m-%d")
        current_year = today.year

        # --- AGENTS ---

        metadata_navigator = Agent(
            role='Data Detective',
            goal='Extract keywords, EXECUTE "Search Entity Fuzzy" tool, and return a strict JSON object.',
            backstory=(
                # Injeção de Contexto
                f"You are a precise data extractor. Today is {current_date_str}.\n"
                "You DO NOT chat. You output JSON.\n\n"
                "PRIORITY FLOW:\n"
                "1. CHECK INTENT (Ranking/Total): If 'Top', 'Maiores', 'Total' -> output intent.\n"
                "2. CHECK ENTITIES: Use 'Search Entity Fuzzy'.\n"
                "3. OUTPUT JSON: {'action': 'EXECUTE_SQL', ...}\n"
            ),
            tools=[DatabaseTools.search_entity_fuzzy],
            verbose=True,
            allow_delegation=False,
            llm=self.llm_engine
        )

        sql_architect = Agent(
            role='Senior SQL Architect',
            goal='Receive JSON and FORCE EXECUTION of SQL queries.',
            backstory=(
                "You are a SQL Engine. You receive JSON and EXECUTE.\n"
                "SCHEMA: v_financas_geral (data, valor, favorecido_nome, unidade_pagadora, id_favorecido, id_ug, tipo_despesa, programa_governo).\n"
                "EXECUTE rules:\n"
                "- RANKING: Use GROUP BY and ORDER BY DESC.\n"
                "- TOTAL: Use SUM(valor).\n"
                "- FILTERS: Use WHERE clause with IDs.\n"
                "- DATES: Resolve 'this year', 'last month' based on current date."
            ),
            tools=[DatabaseTools.search_sql_memory,
                   DatabaseTools.execute_sql, DatabaseTools.export_csv],
            verbose=True,
            allow_delegation=False,
            llm=self.llm_engine
        )

        public_data_analyst = Agent(
            role='Public Transparency Analyst',
            goal='Translate technical results into clear Portuguese (PT-BR).',
            backstory=(
                "Answer based ONLY on SQL results. Format money as R$. Be helpful."
            ),
            verbose=True,
            allow_delegation=False,
            llm=self.llm_engine
        )

        # --- TASKS (COM INJEÇÃO DE DATA) ---

        task_mapping = Task(
            description=(
                f"Analyze query: '{user_question}'.\n"
                f"CONTEXT: Today is {current_date_str}.\n"
                "1. If user says 'este ano' (this year), set 'date': '{current_year}'.\n"
                "2. If user says 'mês passado', calculate the YYYY-MM based on today.\n"
                "3. Use 'Search Entity Fuzzy' if proper nouns exist.\n"
                "4. Output JSON with intent/entities/date."
            ),
            expected_output="JSON Object string.",
            agent=metadata_navigator
        )

        task_query = Task(
            description=(
                "Read JSON input.\n"
                "1. IF 'intent': 'RANKING':\n"
                "   - Construct SQL: SELECT favored_name, SUM(valor) FROM v_financas_geral ... GROUP BY ... ORDER BY 2 DESC LIMIT 5.\n"
                "   - Apply date filter if present in JSON.\n"
                "2. IF 'intent': 'TOTAL':\n"
                "   - Construct SQL: SELECT SUM(valor) ...\n"
                "3. IF 'entities':\n"
                "   - Filter by IDs.\n"
                "4. EXECUTE using 'Execute SQL Query'."
            ),
            expected_output="Markdown Table.",
            agent=sql_architect,
            context=[task_mapping]
        )

        task_response = Task(
            description="Provide final answer in PT-BR.",
            expected_output="Natural language response.",
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
