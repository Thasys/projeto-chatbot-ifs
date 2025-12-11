import pandas as pd
import os
import time
from crewai.tools import tool
from db_connection import DBConnection
from rapidfuzz import process, fuzz, utils
from unidecode import unidecode  # <--- NOVA IMPORTAÇÃO CRUCIAL
from knowledge_base import SQL_EXAMPLES

# --- SISTEMA DE CACHE SINGLETON ---


class EntityCache:
    _instance = None
    _data = {}

    @classmethod
    def get_data(cls):
        if cls._instance is None:
            print("🔄 (Cache) Iniciando Carga de Entidades...")
            cls._instance = cls()
            cls._instance._load_cache()
        return cls._data

    def _load_cache(self):
        db = DBConnection()
        engine = db.get_engine()

        try:
            # Carregando tabelas
            print("   📦 Indexando UGs (Campi/Reitoria)...")
            df_ug = pd.read_sql("SELECT id_ug, ug FROM dim_ug", engine)
            self._data['ug'] = df_ug.set_index('id_ug')['ug'].to_dict()

            print("   📦 Indexando Favorecidos...")
            df_fav = pd.read_sql(
                "SELECT id_favorecido, nomeFavorecido FROM dim_favorecido LIMIT 50000", engine)
            self._data['favorecido'] = df_fav.set_index(
                'id_favorecido')['nomeFavorecido'].to_dict()

            print("   📦 Indexando Programas...")
            df_prog = pd.read_sql(
                "SELECT id_programa, desc_programa FROM dim_programa", engine)
            self._data['programa'] = df_prog.set_index(
                'id_programa')['desc_programa'].to_dict()

            print("   📦 Indexando Naturezas...")
            df_nat = pd.read_sql(
                "SELECT id_natureza, desc_elemento FROM dim_natureza", engine)
            self._data['natureza'] = df_nat.set_index(
                'id_natureza')['desc_elemento'].to_dict()

            print("✅ Cache Pronto!")
        except Exception as e:
            print(f"❌ Erro de Cache: {e}")


class DatabaseTools:

    @staticmethod
    def aggressive_clean(text):
        """
        Remove acentos, pontuação e coloca em minúsculas.
        Ex: 'São Cristóvão' -> 'sao cristovao'
        Ex: 'INST. FED. PROPRIA' -> 'inst fed propria'
        """
        if not isinstance(text, str):
            return str(text)
        # Remove acentos e converte para ASCII aproximado
        clean = unidecode(text)
        return clean.lower().strip()

    @tool("Search Entity Fuzzy")
    def search_entity_fuzzy(search_term: str):
        """
        Semantic Search: Finds entities ignoring accents and case.
        Args:
            search_term: Name to find (e.g., 'Propriá', 'Campus Lagarto').
        """
        try:
            print(f"\n🔍 DEBUG TOOL: Buscando por '{search_term}'...")
            data_cache = EntityCache.get_data()
            results = []

            # Normaliza o termo de busca para log
            term_clean = DatabaseTools.aggressive_clean(search_term)

            # Lógica de Prioridade
            priority_categories = []
            if any(x in term_clean for x in ['campus', 'reitoria', 'instituto', 'unidade', 'polo']):
                priority_categories = ['ug']

            all_categories = ['ug', 'favorecido', 'programa', 'natureza']
            search_order = priority_categories + \
                [c for c in all_categories if c not in priority_categories]

            category_map = {
                'favorecido': ('dim_favorecido', 'id_favorecido'),
                'programa':   ('dim_programa',   'id_programa'),
                'ug':         ('dim_ug',         'id_ug'),
                'natureza':   ('dim_natureza',   'id_natureza')
            }

            # 🔥 O SEGREDO ESTÁ AQUI: PROCESSOR CUSTOMIZADO
            # Passamos a função 'aggressive_clean' para o RapidFuzz.
            # Ele vai aplicar essa função tanto no termo quanto na lista antes de comparar.
            # 'Propriá' vira 'propria'. 'PROPRIA' vira 'propria'. Match = 100%.

            SCORER = fuzz.token_set_ratio
            SCORE_CUTOFF = 60

            for category in search_order:
                if category not in data_cache:
                    continue
                items_dict = data_cache[category]

                matches = process.extract(
                    search_term,  # Passamos o termo original
                    items_dict,
                    limit=5,
                    scorer=SCORER,
                    processor=DatabaseTools.aggressive_clean  # 🔥 Normalização automática
                )

                for match_name, score, match_id in matches:
                    if score >= SCORE_CUTOFF:
                        final_score = score + 10 if category in priority_categories else score

                        if final_score > 75:
                            print(
                                f"   🎯 MATCH ({final_score}%): {match_name} [{category.upper()}]")

                        table_name, id_col = category_map[category]
                        results.append({
                            "type": category.upper(),
                            "similarity_score": round(final_score, 1),
                            "found_name": match_name,  # Retorna o nome original bonito
                            "id": match_id,
                            "table_mapping": {
                                "table": table_name,
                                "id_column": id_col
                            }
                        })

            results.sort(key=lambda x: x['similarity_score'], reverse=True)

            if not results:
                print("   ❌ Nenhum resultado válido.")
                return "No entities found."

            return str(results[:3])

        except Exception as e:
            return f"Error in Fuzzy Search: {str(e)}"

    @tool("Search SQL Memory")
    def search_sql_memory(user_question: str):
        """Retrieves similar SQL templates."""
        from knowledge_base import SQL_EXAMPLES
        try:
            questions = [item['question'] for item in SQL_EXAMPLES]
            matches = process.extract(
                user_question, questions, limit=3, scorer=fuzz.token_sort_ratio)
            results = []
            for match_question, score, index in matches:
                if score > 40:
                    example = SQL_EXAMPLES[index]
                    results.append(
                        f"Context: {example['explanation']}\nSQL: {example['sql']}\n")
            return "\n".join(results) if results else "No memory found."
        except Exception:
            return "Memory Error"

    @tool("Execute SQL Query")
    def execute_sql(sql_query: str):
        """
        Executes a SELECT SQL query on the 'v_financas_geral' view.
        Input must be a valid SQL string starting with SELECT.
        """
        db = DBConnection()
        try:
            # Limpeza e Segurança
            sql_query = sql_query.strip().replace("```sql", "").replace("```", "")

            if not sql_query.upper().startswith("SELECT"):
                return "Error: Only SELECT queries are allowed for safety."

            # Execução via Pandas
            df = pd.read_sql(sql_query, db.get_engine())

            if df.empty:
                return "Query executed successfully but returned 0 rows."

            total_rows = len(df)
            LIMIT_For_LLM = 20

            # Tenta converter para Markdown (formatação bonita)
            # Se falhar (falta de tabulate), usa string padrão (feia mas funcional)
            try:
                if total_rows <= LIMIT_For_LLM:
                    return df.to_markdown(index=False)
                else:
                    # Resumo inteligente para grandes volumes
                    summary = f"⚠️ Result too large ({total_rows} rows). Showing Summary:\n\n"

                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if not numeric_cols.empty:
                        cols = [
                            c for c in numeric_cols if not c.startswith('id_')]
                        if cols:
                            try:
                                summary += f"### Totals:\n{df[cols].sum().to_markdown()}\n\n"
                            except ImportError:
                                summary += f"### Totals:\n{df[cols].sum().to_string()}\n\n"

                    try:
                        summary += f"### First 5 Rows Sample:\n{df.head(5).to_markdown(index=False)}"
                    except ImportError:
                        summary += f"### First 5 Rows Sample:\n{df.head(5).to_string(index=False)}"

                    summary += "\n\nTIP: Use 'Export Query to CSV' if the user wants the full list."
                    return summary

            except ImportError:
                # FALLBACK: Se não tiver tabulate, usa to_string()
                return df.to_string(index=False)
            except Exception:
                # FALLBACK GERAL
                return df.to_string(index=False)

        except Exception as e:
            return f"SQL Syntax Error: {str(e)}"

    @tool("Export Query to CSV")
    def export_csv(sql_query: str):
        """Exports data to CSV."""
        db = DBConnection()
        try:
            filename = f"reports/relatorio_{int(time.time())}.csv"
            os.makedirs("reports", exist_ok=True)
            df = pd.read_sql(sql_query, db.get_engine())
            df.to_csv(filename, index=False, sep=';', decimal=',')
            return f"File generated: {filename}"
        except Exception as e:
            return f"Error: {e}"
