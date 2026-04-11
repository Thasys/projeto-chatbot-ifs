import pandas as pd
import os
import time
from datetime import datetime
from crewai.tools import tool
from db_connection import DBConnection
from rapidfuzz import process, fuzz, utils
from unidecode import unidecode
from knowledge_base import SQL_EXAMPLES

# --- SISTEMA DE CACHE SINGLETON ---


class EntityCache:
    _instance = None
    _data = {}
    _load_time: datetime = None
    CACHE_TTL = 3600  # Recarregar após 1 hora (alinhado ao ETL diário)

    @classmethod
    def get_data(cls):
        now = datetime.now()
        cache_expired = (
            cls._load_time is None or
            (now - cls._load_time).total_seconds() > cls.CACHE_TTL
        )
        if cls._instance is None or cache_expired:
            print("🔄 (Cache) Iniciando Carga de Entidades...")
            cls._instance = cls()
            cls._instance._load_cache()
            cls._load_time = now
        return cls._data

    def _load_cache(self):
        db = DBConnection()
        engine = db.get_engine()

        try:
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
                "SELECT id_programa, programa FROM dim_programa", engine)
            self._data['programa'] = df_prog.set_index(
                'id_programa')['programa'].to_dict()

            print("   📦 Indexando Naturezas...")
            df_nat = pd.read_sql(
                "SELECT id_natureza, elemento FROM dim_natureza", engine)
            self._data['natureza'] = df_nat.set_index(
                'id_natureza')['elemento'].to_dict()

            print("✅ Cache Pronto!")
        except Exception as e:
            print(f"❌ Erro de Cache: {e}")


def aggressive_clean(text):
    """
    Remove acentos, pontuação e coloca em minúsculas.
    Ex: 'São Cristóvão' -> 'sao cristovao'
    Ex: 'INST. FED. PROPRIA' -> 'inst fed propria'
    """
    if not isinstance(text, str):
        return str(text)
    clean = unidecode(text)
    return clean.lower().strip()


@tool
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

        term_clean = aggressive_clean(search_term)

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

        SCORER = fuzz.token_set_ratio
        SCORE_CUTOFF = 60

        for category in search_order:
            if category not in data_cache:
                continue
            items_dict = data_cache[category]

            matches = process.extract(
                search_term,
                items_dict,
                limit=5,
                scorer=SCORER,
                processor=aggressive_clean
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
                        "found_name": match_name,
                        "id": match_id,
                        "table_mapping": {
                            "table": table_name,
                            "id_column": id_col
                        }
                    })

        results.sort(key=lambda x: x['similarity_score'], reverse=True)

        if not results:
            print("   ❌ Nenhum resultado válido.")
            import logging
            logger = logging.getLogger(__name__)
            logger.info(
                f"[FUZZY SEARCH] Nenhuma entidade encontrada para: '{search_term}'")
            return "No entities found."

        # ===== FIX 4.3: LOGGING DOS MATCHES ENCONTRADOS =====
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"[FUZZY SEARCH] Total de matches: {len(results)} para '{search_term}'")
        for i, result in enumerate(results[:3]):
            logger.info(
                f"[FUZZY SEARCH] Match #{i+1}: {result['found_name']} ({result['similarity_score']}% - {result['type']})")

        return str(results[:3])

    except Exception as e:
        return f"Error in Fuzzy Search: {str(e)}"


@tool
def search_sql_memory(user_question: str):
    """Retrieves similar SQL templates."""
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


@tool
def execute_sql(sql_query: str):
    """
    Executes a SELECT SQL query on the 'v_financas_geral' view.
    Input must be a valid SQL string starting with SELECT.

    Returns:
        str: Markdown formatted result or error message
    """
    import logging
    logger = logging.getLogger(__name__)

    db = DBConnection()
    try:
        # Limpar input
        sql_query = sql_query.strip().replace("```sql", "").replace("```", "")

        # ===== FIX 4.2: LOGGING DETALHADO DA SQL EXECUTADA =====
        logger.info(f"[SQL EXEC] ===== QUERY COMPLETA =====")
        logger.info(f"[SQL EXEC] {sql_query}")
        logger.info(f"[SQL EXEC] ===== FIM QUERY =====")

        # Validar segurança
        if not sql_query.upper().startswith("SELECT"):
            error_msg = "❌ Error: Only SELECT queries are allowed for safety."
            logger.warning(error_msg)
            return error_msg

        # Executar query
        logger.info(f"[SQL EXEC] Iniciando execução...")
        df = pd.read_sql(sql_query, db.get_engine())
        logger.info(f"[SQL EXEC] Sucesso! Retornou {len(df)} linhas")

        if df.empty:
            msg = "✅ Query executada com sucesso, mas retornou 0 linhas (nenhum dado encontrado)."
            logger.info(msg)
            return msg

        total_rows = len(df)
        LIMIT_For_LLM = 20

        logger.debug(f"📊 Resultado: {total_rows} linhas")

        try:
            # Resultado pequeno: retornar tudo
            if total_rows <= LIMIT_For_LLM:
                resultado = df.to_markdown(index=False)
                logger.debug(
                    f"📋 Retornando tabela completa ({total_rows} linhas)")
                return resultado
            else:
                # Resultado grande: retornar resumo
                summary = f"⚠️ **Resultado grande** ({total_rows} linhas). Mostrando resumo:\n\n"

                # Calcular totais de colunas numéricas
                cols = []
                numeric_cols = df.select_dtypes(include=['number']).columns
                if not numeric_cols.empty:
                    cols = [c for c in numeric_cols if not c.startswith('id_')]
                    if cols:
                        try:
                            totals_df = df[cols].sum()
                            summary += f"### Totais:\n{totals_df.to_markdown()}\n\n"
                            logger.debug(
                                f"📈 Totais calculados para {len(cols)} colunas")
                        except Exception as total_err:
                            logger.warning(
                                f"⚠️ Erro ao calcular totais: {total_err}")
                            summary += f"### Totais:\n{df[cols].sum().to_string()}\n\n"

                # Primeiras linhas
                try:
                    summary += f"### Primeiras 5 linhas:\n{df.head(5).to_markdown(index=False)}"
                    logger.debug("📋 Primeiras linhas adicionadas")
                except ImportError:
                    summary += f"### Primeiras 5 linhas:\n{df.head(5).to_string(index=False)}"

                summary += "\n\n**Dica:** Use 'Export Query to CSV' para exportar todos os dados."
                logger.info(
                    f"📊 Retornando resumo com {len(cols) if cols else 0} colunas numéricas")
                return summary

        except ImportError as ie:
            logger.warning(f"⚠️ Pandas markdown não disponível, usando string")
            return df.to_string(index=False)
        except Exception as format_err:
            logger.warning(f"⚠️ Erro ao formatar resultado: {format_err}")
            return df.to_string(index=False)

    except Exception as e:
        error_msg = f"❌ SQL Error: {type(e).__name__}: {str(e)[:200]}"
        logger.error(error_msg)
        return error_msg


@tool
def export_csv(sql_query: str):
    """Exports data to CSV."""
    db = DBConnection()
    try:
        sql_query = sql_query.strip().replace("```sql", "").replace("```", "")
        if not sql_query.upper().startswith("SELECT"):
            return "❌ Error: Only SELECT queries are allowed for safety."
        filename = f"reports/relatorio_{int(time.time())}.csv"
        os.makedirs("reports", exist_ok=True)
        df = pd.read_sql(sql_query, db.get_engine())
        df.to_csv(filename, index=False, sep=';', decimal=',')
        return f"File generated: {filename}"
    except Exception as e:
        return f"Error: {e}"
