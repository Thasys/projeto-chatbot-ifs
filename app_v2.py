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
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
/* === BASE === */
:root {
    --green-dark:  #1B4F2A;
    --green-mid:   #2E7D46;
    --green-light: #4CAF72;
    --green-pale:  #E8F5EE;
    --gold:        #F5A623;
    --red:         #C0392B;
    --gray-dark:   #2C2C2C;
    --gray-mid:    #6B7280;
    --gray-light:  #F4F6F8;
    --white:       #FFFFFF;
    --radius-sm:   6px;
    --radius-md:   10px;
    --radius-lg:   16px;
    --shadow:      0 2px 8px rgba(0,0,0,0.08);
}
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
}
.stApp { background-color: var(--gray-light); }
.block-container { padding-top: 1.5rem !important; max-width: 920px !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* === SIDEBAR === */
section[data-testid="stSidebar"] {
    background-color: var(--white) !important;
    border-right: 1px solid #E5E7EB;
}
section[data-testid="stSidebar"] > div { padding-top: 0 !important; }

/* === CHAT BUBBLES === */
[data-testid="stChatMessage"] {
    border-radius: var(--radius-lg) !important;
    padding: 1rem 1.25rem !important;
    margin-bottom: 0.75rem !important;
    box-shadow: var(--shadow);
}

/* === BUTTONS === */
.stButton > button {
    background-color: var(--white) !important;
    color: var(--green-dark) !important;
    border: 1.5px solid var(--green-mid) !important;
    border-radius: var(--radius-md) !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background-color: var(--green-pale) !important;
    border-color: var(--green-dark) !important;
}
.stButton > button[kind="primary"] {
    background-color: var(--green-dark) !important;
    color: var(--white) !important;
    border-color: var(--green-dark) !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: var(--green-mid) !important;
}

/* === METRICS === */
[data-testid="stMetric"] {
    background-color: var(--white);
    border-radius: var(--radius-md);
    padding: 0.75rem 1rem !important;
    box-shadow: var(--shadow);
}
[data-testid="stMetricValue"] {
    color: var(--green-dark) !important;
    font-weight: 700 !important;
}
[data-testid="stMetricLabel"] {
    color: var(--gray-mid) !important;
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* === CUSTOM COMPONENTS === */
.ifs-sidebar-header {
    background: linear-gradient(160deg, var(--green-dark) 0%, var(--green-mid) 100%);
    color: white;
    padding: 1.5rem 1rem 1.25rem 1rem;
    margin: -1rem -1rem 1.25rem -1rem;
    text-align: center;
}
.ifs-sidebar-title { font-size: 1rem; font-weight: 700; margin-top: 0.4rem; }
.ifs-sidebar-subtitle { font-size: 0.65rem; opacity: 0.8; letter-spacing: 0.06em; text-transform: uppercase; }

.ifs-page-header {
    display: flex; align-items: center; gap: 0.75rem;
    padding-bottom: 0.75rem; margin-bottom: 1rem;
    border-bottom: 3px solid var(--green-light);
}
.ifs-page-title { font-size: 1.5rem; font-weight: 700; color: var(--green-dark); margin: 0; }
.ifs-page-subtitle { margin: 0; font-size: 0.8rem; color: var(--gray-mid); }

.ifs-stats-banner {
    background: linear-gradient(135deg, var(--green-dark) 0%, var(--green-mid) 100%);
    color: white;
    border-radius: var(--radius-lg);
    padding: 1.25rem 1.75rem;
    margin-bottom: 1.5rem;
    display: flex; gap: 0; flex-wrap: wrap;
}
.ifs-stat-item {
    flex: 1; min-width: 110px; text-align: center;
    padding: 0 0.75rem;
    border-right: 1px solid rgba(255,255,255,0.2);
}
.ifs-stat-item:last-child { border-right: none; }
.ifs-stat-value { font-size: 1.65rem; font-weight: 700; line-height: 1.1; }
.ifs-stat-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.08em; opacity: 0.8; margin-top: 0.2rem; }

.ifs-badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 10px; border-radius: 999px;
    font-size: 0.72rem; font-weight: 600;
}
.ifs-badge-high   { background: #D4EDDA; color: #155724; }
.ifs-badge-medium { background: #FFF3CD; color: #856404; }
.ifs-badge-low    { background: #F8D7DA; color: #721C24; }

.ifs-period {
    display: inline-flex; align-items: center; gap: 4px;
    color: var(--gray-mid); font-size: 0.72rem;
    background: var(--gray-light); border-radius: 999px;
    padding: 3px 9px;
}

.ifs-response-meta {
    display: flex; align-items: center; flex-wrap: wrap; gap: 6px;
    margin-top: 0.85rem; padding-top: 0.75rem;
    border-top: 1px solid #E5E7EB;
}

.ifs-quick-card {
    background: var(--white);
    border: 1.5px solid #E5E7EB;
    border-radius: var(--radius-md);
    padding: 0.9rem 1rem 0.4rem 1rem;
    margin-bottom: 0;
}
.ifs-quick-icon { font-size: 1.3rem; }
.ifs-quick-title { font-weight: 600; font-size: 0.875rem; color: var(--gray-dark); margin: 0.2rem 0 0.15rem 0; }
.ifs-quick-desc { font-size: 0.73rem; color: var(--gray-mid); }

.ifs-welcome {
    text-align: center; padding: 1.25rem 0 0.75rem 0;
}
.ifs-welcome-title { font-size: 1.1rem; font-weight: 600; color: var(--green-dark); margin-bottom: 0.25rem; }
.ifs-welcome-sub { font-size: 0.85rem; color: var(--gray-mid); }

.ifs-bar-chart {
    background: var(--white);
    border-radius: var(--radius-md);
    padding: 1rem 1.25rem;
    margin-top: 0.75rem;
    box-shadow: var(--shadow);
}
.ifs-bar-label-row {
    display: flex; justify-content: space-between;
    font-size: 0.78rem; margin-bottom: 3px;
}
.ifs-bar-track { background: #E5E7EB; border-radius: 999px; height: 7px; }
.ifs-bar-fill { background: var(--green-mid); height: 7px; border-radius: 999px; }
.ifs-bar-row { margin-bottom: 0.65rem; }

@media (max-width: 768px) {
    .ifs-stats-banner { gap: 0.75rem; }
    .ifs-stat-value { font-size: 1.25rem; }
    .ifs-stat-item { border-right: none; border-bottom: 1px solid rgba(255,255,255,0.15); padding-bottom: 0.5rem; }
    .ifs-stat-item:last-child { border-bottom: none; }
}
</style>
""", unsafe_allow_html=True)

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
        db = get_db_connection()
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
        <span style="font-size:0.68rem; color:var(--gray-mid); margin-left:auto">
            Fonte: Portal da Transparência IFS
        </span>
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
    table_match = re.search(r'\|.+\|[\s\S]*?\|[-| :]+\|[\s\S]*?(?=\n\n|\Z)', result_text)
    if not table_match:
        return False
    try:
        table_str = table_match.group(0)
        df = pd.read_csv(StringIO(table_str), sep='|', skipinitialspace=True)
        df = df.dropna(axis=1, how='all')
        df.columns = [c.strip() for c in df.columns]
        df = df[~df.iloc[:, 0].astype(str).str.contains('---', na=False)].reset_index(drop=True)

        if df.empty or len(df) > 10 or len(df.columns) < 2:
            return False

        numeric_col = None
        num_vals = None
        for col in df.columns[1:]:
            try:
                cleaned = df[col].astype(str).str.replace(r'[R$\s.]', '', regex=True)
                cleaned = cleaned.str.replace(',', '.', regex=False)
                vals = pd.to_numeric(cleaned, errors='coerce')
                if vals.notna().sum() >= len(df) * 0.5:
                    numeric_col = col
                    num_vals = vals
                    break
            except Exception:
                continue

        if numeric_col is None or num_vals is None:
            return False

        max_val = num_vals.max()
        if max_val == 0:
            return False

        label_col = df.columns[0]
        rows_html = ""
        for i, row in df.iterrows():
            val = num_vals.iloc[i] if not pd.isna(num_vals.iloc[i]) else 0
            pct = (val / max_val) * 100
            label = str(row[label_col])[:40]
            val_display = str(row[numeric_col]).strip()
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
            <p style="font-size:0.68rem;color:var(--gray-mid);text-transform:uppercase;
                      letter-spacing:0.07em;margin-bottom:0.75rem">Visualização</p>
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
        <div style="font-size:2.2rem">🏛️</div>
        <div class="ifs-sidebar-title">IFS Transparência</div>
        <div class="ifs-sidebar-subtitle">Instituto Federal de Sergipe</div>
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
    <span style="font-size:1.85rem">🏛️</span>
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

# ========== TELA INICIAL ==========
if len(st.session_state.messages) == 0:
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
                process_input(action['query'])

# ========== HISTÓRICO DO CHAT ==========
else:
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

# ========== INPUT ==========
if prompt := st.chat_input("Faça sua pergunta sobre gastos do IFS... (ex: Maiores fornecedores de 2024)"):
    process_input(prompt)
