# knowledge_base.py

SQL_EXAMPLES = [
    # --- GRUPO 1: TOTAIS POR ENTIDADE ESPECÍFICA (O Básico) ---
    {
        "question": "Quanto foi pago para a empresa Energisa?",
        "sql": "SELECT SUM(valor) as total_pago FROM v_financas_geral WHERE id_favorecido = {ID_DETECTADO}",
        "explanation": "Soma simples filtrando pelo ID do favorecido."
    },
    {
        "question": "Qual o gasto total do Campus Lagarto?",
        "sql": "SELECT SUM(valor) as total_gasto FROM v_financas_geral WHERE id_ug = {ID_DETECTADO}",
        "explanation": "Soma simples filtrando pelo ID da Unidade Gestora (Campus)."
    },
    {
        "question": "Quanto foi gasto com o programa de Assistência Estudantil?",
        "sql": "SELECT SUM(valor) as total_programa FROM v_financas_geral WHERE id_programa = {ID_DETECTADO}",
        "explanation": "Soma filtrando pelo ID do Programa de Governo."
    },

    # --- GRUPO 2: RANKINGS E "TOP X" (Agregações) ---
    {
        "question": "Quais são os 5 maiores fornecedores por valor recebido?",
        "sql": "SELECT favorecido_nome, SUM(valor) as total FROM v_financas_geral GROUP BY favorecido_nome ORDER BY total DESC LIMIT 5",
        "explanation": "Ranking decrescente agrupado por nome do favorecido."
    },
    {
        "question": "Quais campi gastaram mais em 2024?",
        "sql": "SELECT unidade_pagadora, SUM(valor) as total FROM v_financas_geral WHERE data BETWEEN '2024-01-01' AND '2024-12-31' GROUP BY unidade_pagadora ORDER BY total DESC",
        "explanation": "Ranking de unidades gestoras filtrado por ano."
    },
    {
        "question": "Liste as 10 maiores despesas individuais (transações únicas).",
        "sql": "SELECT data, favorecido_nome, valor, historico_detalhado FROM v_financas_geral ORDER BY valor DESC LIMIT 10",
        "explanation": "Lista as transações com maiores valores unitários, sem agrupar."
    },
    {
        "question": "Quais os tipos de despesa mais comuns (maior valor)?",
        "sql": "SELECT tipo_despesa, SUM(valor) as total FROM v_financas_geral GROUP BY tipo_despesa ORDER BY total DESC LIMIT 10",
        "explanation": "Agrupa por natureza da despesa (ex: Diárias, Material) para ver onde vai o dinheiro."
    },

    # --- GRUPO 3: FILTROS CRUZADOS (Complexidade Média) ---
    {
        "question": "Quanto o Campus Estância pagou para a Deso?",
        "sql": "SELECT SUM(valor) as total FROM v_financas_geral WHERE id_ug = {ID_UG} AND id_favorecido = {ID_FAVORECIDO}",
        "explanation": "Filtro duplo: Uma unidade específica pagando a um fornecedor específico."
    },
    {
        "question": "Gastos com Diárias no Campus Aracaju em 2024.",
        "sql": "SELECT SUM(valor) as total_diarias FROM v_financas_geral WHERE id_ug = {ID_UG} AND tipo_despesa LIKE '%DIARIAS%' AND data BETWEEN '2024-01-01' AND '2024-12-31'",
        "explanation": "Combina ID da unidade, busca textual na natureza (Diárias) e filtro de ano."
    },
    {
        "question": "Liste os pagamentos da Reitoria para a Energisa em Março.",
        "sql": "SELECT data, valor, historico_detalhado FROM v_financas_geral WHERE id_ug = {ID_UG} AND id_favorecido = {ID_FAVORECIDO} AND data BETWEEN '2024-03-01' AND '2024-03-31'",
        "explanation": "Lista detalhada com 3 filtros: Unidade, Favorecido e Mês."
    },

    # --- GRUPO 4: RECORTE TEMPORAL (Datas) ---
    {
        "question": "Qual o gasto total em Março de 2024?",
        "sql": "SELECT SUM(valor) as total_mes FROM v_financas_geral WHERE data BETWEEN '2024-03-01' AND '2024-03-31'",
        "explanation": "Soma global de um mês específico."
    },
    {
        "question": "Mostre a evolução dos gastos por mês em 2024.",
        "sql": "SELECT MONTH(data) as mes, SUM(valor) as total FROM v_financas_geral WHERE YEAR(data) = 2024 GROUP BY MONTH(data) ORDER BY mes",
        "explanation": "Agrupamento mensal para análise de tendência."
    },
    {
        "question": "Liste os pagamentos realizados hoje (ou data recente).",
        "sql": "SELECT * FROM v_financas_geral ORDER BY data DESC LIMIT 20",
        "explanation": "Lista os registros mais recentes inseridos no banco."
    },

    # --- GRUPO 5: BUSCA TEXTUAL INTELIGENTE (Sem ID) ---
    # Útil quando o usuário pergunta sobre algo que não é uma Entidade Oficial, mas está na descrição.
    {
        "question": "Quanto foi gasto com café ou lanches?",
        "sql": "SELECT data, unidade_pagadora, valor, historico_detalhado FROM v_financas_geral WHERE historico_detalhado LIKE '%CAFE%' OR historico_detalhado LIKE '%LANCHE%' OR historico_detalhado LIKE '%ALIMENTACAO%'",
        "explanation": "Busca por palavras-chave dentro da coluna de histórico/observação."
    },
    {
        "question": "Gastos com material de limpeza.",
        "sql": "SELECT SUM(valor) as total FROM v_financas_geral WHERE tipo_despesa LIKE '%LIMPEZA%' OR historico_detalhado LIKE '%LIMPEZA%'",
        "explanation": "Busca ampla por 'Limpeza' tanto na categoria quanto no detalhe."
    },
    {
        "question": "Pagamentos referentes a aluguel.",
        "sql": "SELECT data, favorecido_nome, valor FROM v_financas_geral WHERE tipo_despesa LIKE '%LOCACAO%' OR historico_detalhado LIKE '%ALUGUEL%'",
        "explanation": "Busca semântica por aluguéis/locações."
    },

    # --- GRUPO 6: DETALHAMENTO DE PROGRAMAS ---
    {
        "question": "Liste as despesas do programa Educação Profissional.",
        "sql": "SELECT data, favorecido_nome, valor, unidade_pagadora FROM v_financas_geral WHERE id_programa = {ID_DETECTADO} ORDER BY data DESC LIMIT 50",
        "explanation": "Detalhamento de um programa específico."
    },

    # --- GRUPO 7: CONTAGENS E ESTATÍSTICAS ---
    {
        "question": "Quantos pagamentos foram feitos para a Kalunga?",
        "sql": "SELECT COUNT(*) as quantidade_pagamentos, AVG(valor) as valor_medio FROM v_financas_geral WHERE id_favorecido = {ID_DETECTADO}",
        "explanation": "Conta a frequência de pagamentos e a média de valor."
    },
    {
        "question": "Quantas empresas diferentes receberam pagamentos este ano?",
        "sql": "SELECT COUNT(DISTINCT id_favorecido) as total_empresas FROM v_financas_geral WHERE YEAR(data) = 2024",
        "explanation": "Contagem de distintos (Cardinalidade)."
    },

    # --- GRUPO 8: FORNECEDORES REAIS (exclui folha e repasses internos) ---
    # IMPORTANTE: sempre use v_financas_classificada e filtre categoria = 'FORNECEDOR'
    # quando o usuário perguntar sobre fornecedores, empresas, prestadores ou contratos.
    {
        "question": "Quais são os 5 maiores fornecedores do IFS?",
        "sql": "SELECT favorecido_nome, SUM(valor) as total FROM v_financas_classificada WHERE categoria = 'FORNECEDOR' GROUP BY favorecido_nome ORDER BY total DESC LIMIT 5",
        "explanation": "Ranking de fornecedores reais excluindo bancos que operam como intermediários de folha e repasses internos. Usa v_financas_classificada com filtro categoria = 'FORNECEDOR'."
    },
    {
        "question": "Quais empresas receberam mais dinheiro do Campus Lagarto?",
        "sql": "SELECT favorecido_nome, SUM(valor) as total FROM v_financas_classificada WHERE categoria = 'FORNECEDOR' AND id_ug = {ID_UG} GROUP BY favorecido_nome ORDER BY total DESC LIMIT 10",
        "explanation": "Fornecedores reais de um campus específico, sem incluir folha de pagamento."
    },
    {
        "question": "Quanto o IFS gastou com fornecedores (excluindo folha)?",
        "sql": "SELECT SUM(valor) as total_fornecedores FROM v_financas_classificada WHERE categoria = 'FORNECEDOR'",
        "explanation": "Total pago a fornecedores reais de bens e serviços, sem contar folha de pagamento nem repasses internos."
    },

    # --- GRUPO 9: FOLHA DE PAGAMENTO ---
    # Use v_financas_classificada com categoria = 'FOLHA_DE_PAGAMENTO'
    # quando o usuário perguntar sobre salários, folha, servidores, vencimentos, etc.
    {
        "question": "Qual o total gasto com folha de pagamento?",
        "sql": "SELECT SUM(valor) as total_folha FROM v_financas_classificada WHERE categoria = 'FOLHA_DE_PAGAMENTO'",
        "explanation": "Soma todos os repasses de folha (salários, aposentadorias, pensões, contratos temporários). Usa categoria = 'FOLHA_DE_PAGAMENTO' na v_financas_classificada."
    },
    {
        "question": "Quanto cada campus gasta com folha de pagamento?",
        "sql": "SELECT unidade_pagadora, SUM(valor) as total_folha FROM v_financas_classificada WHERE categoria = 'FOLHA_DE_PAGAMENTO' GROUP BY unidade_pagadora ORDER BY total_folha DESC",
        "explanation": "Ranking de gastos com pessoal por campus, usando a categoria de folha de pagamento."
    },
    {
        "question": "Qual a evolução mensal da folha de pagamento em 2025?",
        "sql": "SELECT MONTH(data) as mes, SUM(valor) as total_folha FROM v_financas_classificada WHERE categoria = 'FOLHA_DE_PAGAMENTO' AND YEAR(data) = 2025 GROUP BY MONTH(data) ORDER BY mes",
        "explanation": "Tendência mensal dos gastos com pessoal, filtrando apenas folha de pagamento."
    },
    {
        "question": "Qual banco recebeu mais repasses de folha de pagamento?",
        "sql": "SELECT favorecido_nome, SUM(valor) as total FROM v_financas_classificada WHERE categoria = 'FOLHA_DE_PAGAMENTO' GROUP BY favorecido_nome ORDER BY total DESC LIMIT 5",
        "explanation": "Mostra quais bancos intermediaram mais pagamentos de folha, útil para entender a distribuição bancária dos servidores."
    },

    # --- GRUPO 10: VISÃO GERAL CLASSIFICADA ---
    {
        "question": "Qual o resumo geral dos gastos do IFS por categoria?",
        "sql": "SELECT categoria, COUNT(*) as transacoes, SUM(valor) as total FROM v_financas_classificada GROUP BY categoria ORDER BY total DESC",
        "explanation": "Breakdown do total de gastos separando Folha de Pagamento, Fornecedores e Repasses Internos."
    },
    {
        "question": "Como se divide o orçamento do IFS entre folha e custeio?",
        "sql": "SELECT categoria, SUM(valor) as total, ROUND(SUM(valor) * 100.0 / SUM(SUM(valor)) OVER (), 1) as percentual FROM v_financas_classificada GROUP BY categoria ORDER BY total DESC",
        "explanation": "Proporção percentual de cada categoria no orçamento total do IFS."
    }
]
