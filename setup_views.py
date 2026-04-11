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

    print("[INICIO] Criando view 'v_financas_geral' no banco de dados...")

    sql_view = """
    CREATE OR REPLACE VIEW v_financas_geral AS
    SELECT
        f.data_emissao AS data,
        f.valor_transacao AS valor,
        fav.id_favorecido,
        fav.nomeFavorecido AS favorecido_nome,
        u.id_ug,
        u.ug AS unidade_pagadora,
        n.id_natureza,
        n.elemento AS tipo_despesa,
        p.id_programa,
        p.programa AS programa_governo,
        f.observacao AS historico_detalhado
    FROM fato_execucao f
    LEFT JOIN dim_favorecido fav ON f.id_favorecido = fav.id_favorecido
    LEFT JOIN dim_ug u ON f.id_ug = u.id_ug
    LEFT JOIN dim_natureza n ON f.id_natureza = n.id_natureza
    LEFT JOIN dim_programa p ON f.id_programa = p.id_programa;
    """

    try:
        with engine.connect() as conn:
            conn.execute(text(sql_view))
            conn.commit()

        print("[OK] View 'v_financas_geral' criada com sucesso.")
        print("     Agentes SQL podem usar: SELECT sum(valor) FROM v_financas_geral WHERE ...")

    except Exception as e:
        print(f"[ERRO] Falha ao criar View: {e}")


if __name__ == "__main__":
    create_semantic_views()
