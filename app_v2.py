import streamlit as st
import os
import time
import glob
import re
import pandas as pd
import json
import logging
from io import StringIO
from datetime import datetime
from typing import Tuple, Optional
from crew_definition_v2 import IFSCrewV2
from llm_factory import LLMFactory
from db_connection import DBConnection
from audit_logger import log_to_audit, create_audit_table
from guardrails import Guardrails

# ========== LOGGING ==========
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ========== CONFIGURAÇÃO ==========
st.set_page_config(
    page_title="IFS Transparência IA",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== DESIGN SYSTEM ==========
# st.html() renderiza HTML puro sem processar como Markdown — necessário para <style>
st.html("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
/* === VARIÁVEIS — TEMA ESCURO === */
:root {
    --green-dark:   #1B4F2A;
    --green-mid:    #2E7D46;
    --green-light:  #4CAF72;
    --green-glow:   #3DBA63;
    --green-pale:   #0D2E16;

    --bg-base:      #0F1117;
    --bg-card:      #1A1D27;
    --bg-elevated:  #22263A;
    --bg-hover:     #2A2F45;

    --border:       #2D3148;
    --border-light: #383D5A;

    --text-primary:   #F0F2F8;
    --text-secondary: #9BA3BF;
    --text-muted:     #5C6280;

    --radius-sm:  6px;
    --radius-md:  12px;
    --radius-lg:  18px;
    --shadow-sm:  0 1px 4px rgba(0,0,0,0.4);
    --shadow-md:  0 4px 16px rgba(0,0,0,0.5);
    --shadow-glow: 0 0 20px rgba(61,186,99,0.15);
}

/* === BASE === */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
    color: var(--text-primary) !important;
}
.stApp { background-color: var(--bg-base) !important; }
.block-container {
    padding: 1.75rem 2rem 3rem 2rem !important;
    max-width: 960px !important;
}
#MainMenu, footer, header { visibility: hidden; }

/* Força texto claro em elementos Streamlit nativos */
p, span, label, div, h1, h2, h3, h4, li { color: var(--text-primary); }

/* === SIDEBAR === */
section[data-testid="stSidebar"] {
    background-color: var(--bg-card) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .stMarkdown p {
    font-size: 0.85rem;
    color: var(--text-secondary) !important;
}

/* === SIDEBAR HEADER === */
.ifs-sidebar-header {
    background: linear-gradient(150deg, #0D2E16 0%, var(--green-dark) 50%, var(--green-mid) 100%);
    color: white;
    padding: 1.75rem 1.25rem 1.5rem;
    text-align: center;
    margin-bottom: 1.25rem;
    border-bottom: 1px solid var(--border);
}
.ifs-sidebar-logo { font-size: 2.4rem; line-height: 1; margin-bottom: 0.5rem; }
.ifs-sidebar-title { font-size: 1.05rem; font-weight: 700; margin: 0; letter-spacing: -0.01em; color: #fff !important; }
.ifs-sidebar-subtitle { font-size: 0.62rem; opacity: 0.7; letter-spacing: 0.08em; text-transform: uppercase; margin-top: 0.2rem; color: #fff !important; }

/* === MÉTRICAS DA SIDEBAR === */
div[data-testid="stMetric"] {
    background: var(--bg-elevated) !important;
    border-radius: var(--radius-md) !important;
    padding: 0.65rem 0.85rem !important;
    border: 1px solid var(--border) !important;
}
div[data-testid="stMetricValue"] {
    color: var(--green-glow) !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    line-height: 1.2 !important;
}
div[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 0.65rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* === BOTÕES === */
.stButton > button {
    background-color: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
    border: 1.5px solid var(--border-light) !important;
    border-radius: var(--radius-md) !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    padding: 0.45rem 1rem !important;
    transition: all 0.15s ease !important;
    box-shadow: var(--shadow-sm) !important;
}
.stButton > button:hover {
    background-color: var(--bg-hover) !important;
    border-color: var(--green-glow) !important;
    color: var(--green-glow) !important;
    box-shadow: var(--shadow-glow) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--green-dark), var(--green-mid)) !important;
    color: #fff !important;
    border-color: transparent !important;
    box-shadow: 0 2px 12px rgba(61,186,99,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 4px 20px rgba(61,186,99,0.45) !important;
    transform: translateY(-1px) !important;
}

/* === CHAT === */
div[data-testid="stChatMessage"] {
    background-color: var(--bg-card) !important;
    border-radius: var(--radius-lg) !important;
    padding: 1rem 1.25rem !important;
    margin-bottom: 0.6rem !important;
    box-shadow: var(--shadow-sm) !important;
    border: 1px solid var(--border) !important;
}
div[data-testid="stChatInput"] textarea {
    background-color: var(--bg-card) !important;
    border-radius: var(--radius-lg) !important;
    border-color: var(--border-light) !important;
    color: var(--text-primary) !important;
    font-size: 0.9rem !important;
}
div[data-testid="stChatInput"] textarea:focus {
    border-color: var(--green-glow) !important;
    box-shadow: 0 0 0 3px rgba(61,186,99,0.15) !important;
}

/* === PAGE HEADER === */
.ifs-page-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding-bottom: 1rem;
    margin-bottom: 1.25rem;
    border-bottom: 1px solid var(--border);
}
.ifs-page-header-icon {
    width: 48px; height: 48px;
    background: linear-gradient(135deg, var(--green-dark), var(--green-mid));
    border-radius: var(--radius-md);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.6rem; flex-shrink: 0;
    box-shadow: 0 2px 12px rgba(61,186,99,0.3);
}
.ifs-page-title { font-size: 1.45rem; font-weight: 800; color: var(--text-primary) !important; margin: 0; letter-spacing: -0.02em; }
.ifs-page-subtitle { margin: 0.15rem 0 0 0; font-size: 0.8rem; color: var(--text-secondary) !important; }

/* === BANNER DE ESTATÍSTICAS === */
.ifs-stats-banner {
    background: linear-gradient(135deg, #0D2E16 0%, var(--green-dark) 60%, #255c38 100%);
    color: white;
    border-radius: var(--radius-lg);
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0;
    border: 1px solid rgba(61,186,99,0.2);
    box-shadow: 0 4px 24px rgba(0,0,0,0.4), 0 0 0 1px rgba(61,186,99,0.1);
}
.ifs-stat-item {
    text-align: center;
    padding: 0.25rem 0.5rem;
    border-right: 1px solid rgba(255,255,255,0.12);
}
.ifs-stat-item:last-child { border-right: none; }
.ifs-stat-value {
    font-size: 1.6rem; font-weight: 800; line-height: 1.1;
    letter-spacing: -0.02em; color: #fff !important;
}
.ifs-stat-label {
    font-size: 0.62rem; text-transform: uppercase;
    letter-spacing: 0.09em; opacity: 0.65; margin-top: 0.25rem; color: #fff !important;
}

/* === CARDS DE CONSULTA RÁPIDA === */
.ifs-quick-card {
    background: var(--bg-card);
    border: 1.5px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1rem 1rem 0.75rem 1rem;
    transition: border-color 0.15s, box-shadow 0.15s, background 0.15s;
    height: 100%;
}
.ifs-quick-card:hover {
    border-color: var(--green-glow);
    background: var(--bg-elevated);
    box-shadow: var(--shadow-glow);
}
.ifs-quick-icon { font-size: 1.4rem; }
.ifs-quick-title { font-weight: 700; font-size: 0.88rem; color: var(--text-primary) !important; margin: 0.3rem 0 0.2rem 0; }
.ifs-quick-desc { font-size: 0.74rem; color: var(--text-secondary) !important; margin-bottom: 0.6rem; }

div[data-testid="column"] .stButton > button {
    font-size: 0.8rem !important;
    padding: 0.35rem 0.75rem !important;
    color: var(--green-glow) !important;
    border-color: rgba(61,186,99,0.35) !important;
    background: transparent !important;
}
div[data-testid="column"] .stButton > button:hover {
    background: rgba(61,186,99,0.1) !important;
    border-color: var(--green-glow) !important;
}

/* === TELA DE BOAS-VINDAS === */
.ifs-welcome { text-align: center; padding: 1rem 0 1.25rem 0; }
.ifs-welcome-title { font-size: 1.15rem; font-weight: 700; color: var(--text-primary) !important; margin-bottom: 0.3rem; }
.ifs-welcome-sub { font-size: 0.85rem; color: var(--text-secondary) !important; }

/* === BADGES E META === */
.ifs-badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 10px; border-radius: 999px;
    font-size: 0.71rem; font-weight: 600;
}
.ifs-badge-high   { background: rgba(61,186,99,0.15); color: #4ADE80; border: 1px solid rgba(61,186,99,0.3); }
.ifs-badge-medium { background: rgba(251,191,36,0.12); color: #FCD34D; border: 1px solid rgba(251,191,36,0.25); }
.ifs-badge-low    { background: rgba(248,113,113,0.12); color: #F87171; border: 1px solid rgba(248,113,113,0.25); }

.ifs-period {
    display: inline-flex; align-items: center; gap: 4px;
    color: var(--text-secondary); font-size: 0.71rem;
    background: var(--bg-elevated); border-radius: 999px;
    padding: 3px 10px; border: 1px solid var(--border);
}

.ifs-response-meta {
    display: flex; align-items: center; flex-wrap: wrap; gap: 6px;
    margin-top: 0.9rem; padding-top: 0.75rem;
    border-top: 1px solid var(--border);
}
.ifs-response-source { font-size: 0.67rem; color: var(--text-muted); margin-left: auto; }

/* === GRÁFICO DE BARRAS === */
.ifs-bar-chart {
    background: var(--bg-elevated);
    border-radius: var(--radius-md);
    padding: 1rem 1.25rem;
    margin-top: 0.75rem;
    border: 1px solid var(--border);
}
.ifs-bar-section-label {
    font-size: 0.65rem; color: var(--text-muted);
    text-transform: uppercase; letter-spacing: 0.07em;
    margin-bottom: 0.75rem; font-weight: 600;
}
.ifs-bar-label-row {
    display: flex; justify-content: space-between; align-items: baseline;
    font-size: 0.78rem; margin-bottom: 4px;
    color: var(--text-primary);
}
.ifs-bar-track { background: var(--border); border-radius: 999px; height: 6px; overflow: hidden; }
.ifs-bar-fill { background: linear-gradient(90deg, var(--green-mid), var(--green-glow)); height: 6px; border-radius: 999px; }
.ifs-bar-row { margin-bottom: 0.7rem; }
.ifs-bar-row:last-child { margin-bottom: 0; }

/* === STATUS / SPINNER === */
div[data-testid="stStatus"] {
    background: var(--bg-card) !important;
    border-radius: var(--radius-md) !important;
    border-color: var(--border) !important;
    color: var(--text-secondary) !important;
    font-size: 0.85rem !important;
}

/* === EXPANDERS === */
details[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
}
details[data-testid="stExpander"] summary {
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
}

/* === DIVISOR === */
hr { border-color: var(--border) !important; margin: 0.75rem 0 !important; }

/* === SCROLLBAR === */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border-light); border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* === RESPONSIVO === */
@media (max-width: 768px) {
    .block-container { padding: 1rem !important; }
    .ifs-stats-banner {
        grid-template-columns: repeat(2, 1fr);
        gap: 0.75rem;
        padding: 1.25rem;
    }
    .ifs-stat-item { border-right: none; }
    .ifs-stat-value { font-size: 1.3rem; }
    .ifs-page-title { font-size: 1.2rem; }
}
</style>
""")

# ========== MENSAGENS DE ERRO ==========
ERRO_MENSAGENS = {
    'SQL_ERROR': '❌ Erro ao consultar banco de dados. Tente reformular sua pergunta.',
    'ENTITY_NOT_FOUND': '🔍 Entidade não encontrada. Verifique o nome ou tente outro termo.',
    'TIMEOUT': '⏱️ Operação demorou muito. Tente uma pergunta mais específica.',
    'INVALID_INPUT': '⚠️ Pergunta muito curta ou muito longa. Use entre 5 e 500 caracteres.',
    'GENERIC_ERROR': '❌ Algo deu errado. Entre em contato: admin@ifs.edu.br',
}

# ========== CONSULTAS RÁPIDAS ==========
QUICK_ACTIONS = [
    {
        "icon": "🏆",
        "title": "Top 5 Fornecedores",
        "description": "Quem mais recebeu pagamentos do IFS",
        "query": "Quais são os 5 maiores fornecedores de 2024?"
    },
    {
        "icon": "🏫",
        "title": "Gastos por Campus",
        "description": "Total de despesas por unidade do IFS",
        "query": "Qual o gasto total de cada campus em 2024?"
    },
    {
        "icon": "⚡",
        "title": "Energia Elétrica",
        "description": "Pagamentos ao fornecedor de energia",
        "query": "Quanto foi pago para Energisa em 2024?"
    },
    {
        "icon": "📊",
        "title": "Volume Total IFS",
        "description": "Soma de todas as despesas do período",
        "query": "Qual o valor total gasto pelo IFS em 2024?"
    }
]

# ========== CACHE E SINGLETONS ==========

@st.cache_resource
def get_db_connection():
    return DBConnection()


@st.cache_resource
def get_crew():
    return IFSCrewV2(use_json_mode=True, cache_ttl=300)


@st.cache_resource
def get_guardrails():
    return Guardrails("config/respostas_prontas.json")


@st.cache_resource
def init_audit_logging():
    try:
        create_audit_table()
        return True
    except Exception as e:
        logger.warning(f"Erro ao inicializar auditoria: {e}")
        return False


@st.cache_data(ttl=3600)
def get_db_stats():
    """Busca estatísticas do banco para o banner. Cache de 1 hora."""
    try:
        db = DBConnection()  # singleton — não chama cache_resource dentro de cache_data
        result = db.execute_query("""
            SELECT
                COUNT(*)          AS total_transacoes,
                COALESCE(SUM(valor), 0) AS total_valor,
                MIN(YEAR(data))   AS ano_inicio,
                MAX(YEAR(data))   AS ano_fim,
                COUNT(DISTINCT id_ug) AS total_campi
            FROM v_financas_geral
        """)
        if result and result[0].get('total_transacoes'):
            return result[0]
    except Exception as e:
        logger.warning(f"Erro ao carregar stats: {e}")
    return {
        'total_transacoes': 13194,
        'total_valor': 424940126.35,
        'ano_inicio': 2024,
        'ano_fim': 2025,
        'total_campi': 10
    }

# ========== HELPERS DE RENDERIZAÇÃO ==========

MONTHS_PT = ["Jan","Fev","Mar","Abr","Mai","Jun",
             "Jul","Ago","Set","Out","Nov","Dez"]


def render_confidence_badge(confidence: float) -> str:
    if confidence >= 80:
        cls, icon, label = "ifs-badge-high", "✓", f"Alta confiança ({confidence:.0f}%)"
    elif confidence >= 50:
        cls, icon, label = "ifs-badge-medium", "~", f"Confiança média ({confidence:.0f}%)"
    else:
        cls, icon, label = "ifs-badge-low", "!", f"Baixa confiança ({confidence:.0f}%)"
    return f'<span class="ifs-badge {cls}">{icon} {label}</span>'


def render_period_chip(period_start: Optional[str], period_end: Optional[str]) -> str:
    if not period_start:
        return ""
    try:
        ps = datetime.strptime(period_start, "%Y-%m-%d")
        pe = datetime.strptime(period_end, "%Y-%m-%d")
        s = f"{MONTHS_PT[ps.month-1]} {ps.year}"
        e = f"{MONTHS_PT[pe.month-1]} {pe.year}"
        label = s if s == e else f"{s} – {e}"
    except Exception:
        label = f"{period_start} até {period_end}"
    return f'<span class="ifs-period">📅 {label}</span>'


def render_response_meta(confidence: float, period_start: Optional[str], period_end: Optional[str]) -> None:
    badge = render_confidence_badge(confidence)
    period = render_period_chip(period_start, period_end)
    st.markdown(f"""
    <div class="ifs-response-meta">
        {badge}
        {period}
        <span class="ifs-response-source">Fonte: Portal da Transparência IFS</span>
    </div>
    """, unsafe_allow_html=True)


def render_feedback_buttons(message_index: int) -> None:
    current = st.session_state.feedback.get(message_index)
    if current is None:
        col1, col2, col3 = st.columns([1, 1, 6])
        with col1:
            if st.button("👍", key=f"pos_{message_index}", help="Resposta útil"):
                st.session_state.feedback[message_index] = "positive"
                st.rerun()
        with col2:
            if st.button("👎", key=f"neg_{message_index}", help="Resposta não útil"):
                st.session_state.feedback[message_index] = "negative"
                st.rerun()
    elif current == "positive":
        st.markdown('<span style="font-size:0.75rem;color:#155724">👍 Obrigado pelo feedback!</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span style="font-size:0.75rem;color:#856404">👎 Obrigado! Vamos melhorar.</span>', unsafe_allow_html=True)


def try_render_bar_chart(result_text: str) -> bool:
    """Detecta tabela markdown no resultado e renderiza gráfico de barras CSS."""
    lines = result_text.split('\n')
    table_start = -1
    sep_line = -1

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('|') and stripped.endswith('|') and table_start == -1:
            table_start = idx
        elif table_start != -1 and re.match(r'^\|[\s\-:|]+\|$', stripped):
            sep_line = idx
            break

    if table_start == -1 or sep_line == -1:
        return False

    try:
        # Parsear cabeçalho
        headers = [h.strip() for h in lines[table_start].strip().split('|')[1:-1]]
        if len(headers) < 2:
            return False

        # Parsear linhas de dados
        rows = []
        for line in lines[sep_line + 1:]:
            stripped = line.strip()
            if not stripped.startswith('|'):
                break
            cols = [c.strip() for c in stripped.split('|')[1:-1]]
            if len(cols) == len(headers):
                rows.append(dict(zip(headers, cols)))

        if not rows or len(rows) > 10:
            return False

        # Encontrar coluna numérica
        numeric_col = None
        num_vals = []
        for col in headers[1:]:
            try:
                vals = []
                for row in rows:
                    cleaned = re.sub(r'[R$\s]', '', row.get(col, ''))
                    # Formato BR: 1.234.567,89 → remover pontos de milhar, trocar vírgula
                    cleaned = re.sub(r'\.(?=\d{3})', '', cleaned)
                    cleaned = cleaned.replace(',', '.')
                    vals.append(float(cleaned))
                if vals and max(vals) > 0:
                    numeric_col = col
                    num_vals = vals
                    break
            except (ValueError, TypeError, AttributeError):
                continue

        if not numeric_col or not num_vals:
            return False

        max_val = max(num_vals)
        label_col = headers[0]
        rows_html = ""
        for row, val in zip(rows, num_vals):
            pct = (val / max_val) * 100
            label = row.get(label_col, '')[:42]
            val_display = row.get(numeric_col, '')
            rows_html += f"""
            <div class="ifs-bar-row">
                <div class="ifs-bar-label-row">
                    <span style="color:var(--gray-dark)">{label}</span>
                    <span style="color:var(--green-dark);font-weight:600">{val_display}</span>
                </div>
                <div class="ifs-bar-track">
                    <div class="ifs-bar-fill" style="width:{pct:.1f}%"></div>
                </div>
            </div>
            """

        st.markdown(f"""
        <div class="ifs-bar-chart">
            <p class="ifs-bar-section-label">Visualização</p>
            {rows_html}
        </div>
        """, unsafe_allow_html=True)
        return True
    except Exception:
        return False

# ========== VALIDAÇÃO E RATE LIMITING ==========

def validar_input(user_input: str) -> Tuple[bool, str]:
    if not user_input or len(user_input.strip()) < 5:
        return False, ERRO_MENSAGENS['INVALID_INPUT']
    if len(user_input) > 500:
        return False, ERRO_MENSAGENS['INVALID_INPUT']
    return True, ""


def verificar_rate_limit() -> Tuple[bool, str]:
    if 'last_request_time' not in st.session_state:
        st.session_state.last_request_time = 0
    decorrido = time.time() - st.session_state.last_request_time
    if decorrido < 2:
        return False, f"⏳ Aguarde {int(2 - decorrido)}s antes da próxima pergunta..."
    st.session_state.last_request_time = time.time()
    return True, ""

# ========== PROCESSAMENTO ==========

def process_input(user_input: str):
    valido, erro = validar_input(user_input)
    if not valido:
        st.error(erro)
        return

    guardrails = get_guardrails()
    resposta_pronta = guardrails.check_intent(user_input)
    if resposta_pronta:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
        with st.chat_message("assistant", avatar="🏛️"):
            st.warning(resposta_pronta)
        st.session_state.messages.append({"role": "assistant", "content": resposta_pronta})
        return

    permitido, msg_rate = verificar_rate_limit()
    if not permitido:
        st.warning(msg_rate)
        return

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🏛️"):
        try:
            with st.status("Consultando dados do IFS...", expanded=False) as status:
                inicio = time.time()
                crew = get_crew()
                crew_instance = crew.get_crew(user_input)
                crew_response = crew.execute_with_confidence(crew_instance, user_input)
                tempo_decorrido = time.time() - inicio
                status.update(
                    label=f"Concluído em {tempo_decorrido:.1f}s",
                    state="complete",
                    expanded=False
                )

            result = crew_response['resposta']
            confidence = crew_response['confidence']
            metadata = crew_response['metadata']

            # Auditoria
            log_to_audit(
                pergunta=user_input,
                resposta=str(result)[:5000],
                status="SUCCESS" if "Erro" not in str(result) else "ERROR",
                tempo_ms=int(tempo_decorrido * 1000),
                user_ip=st.session_state.get('user_ip', 'STREAMLIT'),
                json_intent={},
                confidence=confidence,
                periodo_dados_inicio=metadata.period_start,
                periodo_dados_fim=metadata.period_end,
            )

            # Resposta
            st.markdown(result)
            try_render_bar_chart(result)
            render_response_meta(confidence, metadata.period_start, metadata.period_end)

            if metadata.warning_messages:
                for w in metadata.warning_messages:
                    st.warning(w)

            # Salvar com metadata
            msg_index = len(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": result})
            st.session_state.message_meta[msg_index] = {
                "confidence": confidence,
                "period_start": metadata.period_start,
                "period_end": metadata.period_end,
            }
            render_feedback_buttons(msg_index)

        except Exception as e:
            st.error(ERRO_MENSAGENS['GENERIC_ERROR'])
            logger.error(f"Erro crítico: {e}")

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("""
    <div class="ifs-sidebar-header">
        <div class="ifs-sidebar-logo">🏛️</div>
        <p class="ifs-sidebar-title">IFS Transparência</p>
        <p class="ifs-sidebar-subtitle">Instituto Federal de Sergipe</p>
    </div>
    """, unsafe_allow_html=True)

    # Estatísticas do banco
    try:
        stats_sidebar = get_db_stats()
        valor_m = stats_sidebar['total_valor'] / 1_000_000
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Transações", f"{int(stats_sidebar['total_transacoes']):,}".replace(",", "."))
            st.metric("Período", f"{stats_sidebar['ano_inicio']}–{stats_sidebar['ano_fim']}")
        with col_b:
            st.metric("Volume", f"R${valor_m:.0f}M")
            st.metric("Unidades", int(stats_sidebar['total_campi']))
    except Exception:
        pass

    st.markdown("---")

    with st.expander("📚 Como Perguntar?", expanded=False):
        st.markdown("""
O sistema entende português natural, inclusive com erros de digitação.

**Perguntas que funcionam bem:**
- "Quais os 5 maiores fornecedores de 2024?"
- "Quanto foi pago para Energisa este ano?"
- "Gastos do Campus Lagarto em junho"
- "Total de diárias pagas pela Reitoria"

**Dicas:**
- Mencione o ano para dados específicos
- Use nomes aproximados — o sistema encontra mesmo com erros
- Perguntas sobre totais, rankings e comparações funcionam melhor
        """)

    with st.expander("📂 Relatórios Gerados", expanded=False):
        files = sorted(glob.glob("reports/*.csv"), key=os.path.getmtime, reverse=True)
        if files:
            for idx, arquivo in enumerate(files[:5]):
                nome = os.path.basename(arquivo)
                data_mod = datetime.fromtimestamp(os.path.getmtime(arquivo)).strftime("%d/%m %H:%M")
                with open(arquivo, "rb") as f:
                    st.download_button(
                        label=f"⬇️ {nome[:22]}... ({data_mod})",
                        data=f,
                        file_name=nome,
                        mime="text/csv",
                        key=f"dl_{idx}"
                    )
        else:
            st.caption("Nenhum relatório ainda. Resultados tabulares poderão ser exportados aqui.")

    st.markdown("---")

    if st.button("🧹 Nova Conversa", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.session_state.message_meta = {}
        st.session_state.feedback = {}
        st.rerun()

    # Analytics da sessão
    st.markdown("---")
    total_q = len([m for m in st.session_state.get('messages', []) if m['role'] == 'user'])
    confidences = [v['confidence'] for v in st.session_state.get('message_meta', {}).values()]
    avg_conf = sum(confidences) / len(confidences) if confidences else 0
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("Perguntas", total_q)
    with col_s2:
        st.metric("Confiança", f"{avg_conf:.0f}%" if avg_conf else "—")

# ========== ÁREA PRINCIPAL ==========
init_audit_logging()

# Inicializar estado
if "messages" not in st.session_state:
    st.session_state.messages = []
if "message_meta" not in st.session_state:
    st.session_state.message_meta = {}
if "feedback" not in st.session_state:
    st.session_state.feedback = {}

# Header
st.markdown("""
<div class="ifs-page-header">
    <div class="ifs-page-header-icon">🏛️</div>
    <div>
        <p class="ifs-page-title">IFS Transparência Inteligente</p>
        <p class="ifs-page-subtitle">Consulte gastos públicos do Instituto Federal de Sergipe em linguagem natural</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Banner de estatísticas
try:
    stats = get_db_stats()
    valor_fmt   = f"R$ {stats['total_valor']/1_000_000:.1f}M"
    trans_fmt   = f"{int(stats['total_transacoes']):,}".replace(",", ".")
    periodo_fmt = f"{stats['ano_inicio']}–{stats['ano_fim']}"
    campi_fmt   = str(int(stats['total_campi']))

    st.markdown(f"""
    <div class="ifs-stats-banner">
        <div class="ifs-stat-item">
            <div class="ifs-stat-value">{valor_fmt}</div>
            <div class="ifs-stat-label">Volume Total</div>
        </div>
        <div class="ifs-stat-item">
            <div class="ifs-stat-value">{trans_fmt}</div>
            <div class="ifs-stat-label">Transações</div>
        </div>
        <div class="ifs-stat-item">
            <div class="ifs-stat-value">{periodo_fmt}</div>
            <div class="ifs-stat-label">Período</div>
        </div>
        <div class="ifs-stat-item">
            <div class="ifs-stat-value">{campi_fmt}</div>
            <div class="ifs-stat-label">Campi e Unidades</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
except Exception:
    pass

# ========== CAPTURAR QUERY PENDENTE (antes de qualquer coluna) ==========
# Quick actions salvam a query aqui para ser processada fora do contexto de coluna
_pending_query = None
if 'pending_query' in st.session_state:
    _pending_query = st.session_state['pending_query']
    del st.session_state['pending_query']

# ========== TELA INICIAL ==========
if len(st.session_state.messages) == 0 and not _pending_query:
    st.markdown("""
    <div class="ifs-welcome">
        <p class="ifs-welcome-title">👋 Como posso ajudar?</p>
        <p class="ifs-welcome-sub">Digite sua pergunta abaixo ou escolha uma das consultas populares:</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="small")
    cols = [col1, col2, col1, col2]

    for i, action in enumerate(QUICK_ACTIONS):
        with cols[i]:
            st.markdown(f"""
            <div class="ifs-quick-card">
                <span class="ifs-quick-icon">{action['icon']}</span>
                <p class="ifs-quick-title">{action['title']}</p>
                <p class="ifs-quick-desc">{action['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Consultar →", key=f"qa_{i}", use_container_width=True):
                # Salva e faz rerun — process_input será chamado fora das colunas
                st.session_state['pending_query'] = action['query']
                st.rerun()

# ========== HISTÓRICO DO CHAT ==========
elif len(st.session_state.messages) > 0:
    for i, message in enumerate(st.session_state.messages):
        avatar = "👤" if message["role"] == "user" else "🏛️"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                meta = st.session_state.message_meta.get(i, {})
                if meta:
                    render_response_meta(
                        meta.get("confidence", 0),
                        meta.get("period_start"),
                        meta.get("period_end")
                    )
                render_feedback_buttons(i)

# ========== INPUT — fora de qualquer coluna ==========
if _pending_query:
    process_input(_pending_query)
elif prompt := st.chat_input("Faça sua pergunta sobre gastos do IFS... (ex: Maiores fornecedores de 2024)"):
    process_input(prompt)
