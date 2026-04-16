# setup_views.py
import sys
import io
from sqlalchemy import text
from db_connection import DBConnection

# Fix Unicode encoding on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def create_semantic_views():
    db = DBConnection()
    engine = db.get_engine()

    # ── View 1: base ──────────────────────────────────────────────────────────
    print("[INICIO] Criando view 'v_financas_geral'...")

    sql_view_geral = """
    CREATE OR REPLACE VIEW v_financas_geral AS
    SELECT
        f.data_emissao          AS data,
        f.valor_transacao       AS valor,
        fav.id_favorecido,
        fav.nomeFavorecido      AS favorecido_nome,
        u.id_ug,
        u.ug                    AS unidade_pagadora,
        n.id_natureza,
        n.elemento              AS tipo_despesa,
        p.id_programa,
        p.programa              AS programa_governo,
        f.observacao            AS historico_detalhado
    FROM fato_execucao f
    LEFT JOIN dim_favorecido fav ON f.id_favorecido = fav.id_favorecido
    LEFT JOIN dim_ug         u   ON f.id_ug         = u.id_ug
    LEFT JOIN dim_natureza   n   ON f.id_natureza   = n.id_natureza
    LEFT JOIN dim_programa   p   ON f.id_programa   = p.id_programa
    """

    # ── View 2: classificada ──────────────────────────────────────────────────
    # Critérios de classificação:
    #   FOLHA_DE_PAGAMENTO  — tipo_despesa com códigos de pessoal (01,03,04,11,13,46,47,92)
    #                         ou pagamento com tipo '-4 - Múltiplo' para instituição financeira
    #   REPASSE_INTERNO     — favorecido é a própria instituição IFS
    #   FORNECEDOR          — todo o resto (bens, serviços, obras, bolsas, etc.)
    print("[INICIO] Criando view 'v_financas_classificada'...")

    sql_view_classificada = """
    CREATE OR REPLACE VIEW v_financas_classificada AS
    SELECT
        data,
        valor,
        id_favorecido,
        favorecido_nome,
        id_ug,
        unidade_pagadora,
        id_natureza,
        tipo_despesa,
        id_programa,
        programa_governo,
        historico_detalhado,
        CASE
            WHEN tipo_despesa REGEXP '^(01|03|04|11|13|46|47|92) '
              OR (
                tipo_despesa LIKE '%-4 - Multiplo%'
                AND (
                  favorecido_nome LIKE '%BANCO%'
                  OR favorecido_nome LIKE '%CAIXA ECONOMICA%'
                  OR favorecido_nome LIKE '%BRADESCO%'
                  OR favorecido_nome LIKE '%SANTANDER%'
                  OR favorecido_nome LIKE '%ITAU%'
                )
              )
            THEN 'FOLHA_DE_PAGAMENTO'
            WHEN favorecido_nome LIKE '%INST.FED%'
              OR favorecido_nome LIKE '%INST FED%'
              OR favorecido_nome LIKE '%INSTIT FED%'
              OR favorecido_nome LIKE '%INSTITUTO FED%'
            THEN 'REPASSE_INTERNO'
            ELSE 'FORNECEDOR'
        END AS categoria
    FROM v_financas_geral
    """

    try:
        with engine.connect() as conn:
            conn.execute(text(sql_view_geral))
            conn.commit()
        print("[OK] v_financas_geral criada.")

        with engine.connect() as conn:
            conn.execute(text(sql_view_classificada))
            conn.commit()
        print("[OK] v_financas_classificada criada.")
        print("     Use: SELECT * FROM v_financas_classificada WHERE categoria = 'FORNECEDOR'")

    except Exception as e:
        print(f"[ERRO] Falha ao criar views: {e}")


if __name__ == "__main__":
    create_semantic_views()
