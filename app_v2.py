import streamlit as st
import os
import time
import glob
import pandas as pd
import json
import logging
from datetime import datetime
from typing import Tuple
from crew_definition_v2 import IFSCrewV2
from llm_factory import LLMFactory
from db_connection import DBConnection
from audit_logger import log_to_audit, create_audit_table

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

# ========== CSS PERSONALIZADO ==========
st.markdown("""
<style>
    .stChatMessage { background-color: #f8f9fa; border-radius: 12px; padding: 15px; }
    .success-box { background-color: #d4edda; border-left: 4px solid #28a745; padding: 10px; }
    .error-box { background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 10px; }
    .warning-box { background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; }
    .loading-spinner { text-align: center; }
</style>
""", unsafe_allow_html=True)

# ========== MENSAGENS DE ERRO AMIGÁVEIS ==========
ERRO_MENSAGENS = {
    'SQL_ERROR': '❌ Erro ao consultar banco de dados. Tente reformular sua pergunta.',
    'ENTITY_NOT_FOUND': '🔍 Entidade não encontrada. Verifique o nome ou tente outro termo.',
    'TIMEOUT': '⏱️ Operação demorou muito. Tente uma pergunta mais específica.',
    'INVALID_INPUT': '⚠️ Pergunta muito curta ou muito longa. Use entre 5 e 500 caracteres.',
    'GENERIC_ERROR': '❌ Algo deu errado. Contato com administrador: admin@ifs.edu.br',
}

# ========== CACHE E SINGLETONS ==========


@st.cache_resource
def get_db_connection():
    return DBConnection()


@st.cache_resource
def get_crew():
    return IFSCrewV2(use_json_mode=True, cache_ttl=300)


@st.cache_resource
def init_audit_logging():
    """Inicializa tabela de auditoria na primeira execução."""
    try:
        create_audit_table()
        logger.info("✅ Auditoria inicializada")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Erro ao inicializar auditoria: {e}")
        return False

# ========== VALIDAÇÃO DE INPUT ==========


def validar_input(user_input: str) -> Tuple[bool, str]:
    """Valida input do usuário."""
    if not user_input or len(user_input.strip()) < 5:
        return False, ERRO_MENSAGENS['INVALID_INPUT']

    if len(user_input) > 500:
        return False, ERRO_MENSAGENS['INVALID_INPUT']

    return True, ""

# ========== RATE LIMITING ==========


def verificar_rate_limit() -> Tuple[bool, str]:
    """Verifica se usuário não está fazendo requisições muito rápidas."""
    if 'last_request_time' not in st.session_state:
        st.session_state.last_request_time = 0

    tempo_decorrido = time.time() - st.session_state.last_request_time

    if tempo_decorrido < 2:
        tempo_espera = int(2 - tempo_decorrido)
        return False, f"⏳ Aguarde {tempo_espera}s antes da próxima pergunta..."

    st.session_state.last_request_time = time.time()
    return True, ""

# ========== PROCESSAMENTO DE MENSAGEM (MELHORADO) ==========


def process_input(user_input: str):
    """Processa entrada com tratamento robusto de erros."""

    # VALIDAÇÃO 1: Input válido
    valido, erro = validar_input(user_input)
    if not valido:
        st.error(erro)
        return

    # VALIDAÇÃO 2: Rate limiting
    permitido, msg_rate = verificar_rate_limit()
    if not permitido:
        st.warning(msg_rate)
        return

    # Adicionar ao histórico
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Resposta do assistente
    with st.chat_message("assistant"):
        try:
            # ========== ETAPAS COM FEEDBACK REAL ==========
            status_box = st.status("🧠 Processando...", expanded=True)

            # Etapa 1
            status_box.write("🔍 **Etapa 1:** Analisando pergunta...")
            time.sleep(0.5)  # Visual feedback

            # Etapa 2
            status_box.write("🔎 **Etapa 2:** Buscando entidades...")
            time.sleep(0.5)

            # Etapa 3
            status_box.write("🏗️ **Etapa 3:** Construindo query SQL...")
            time.sleep(0.5)

            # Etapa 4
            status_box.write("📊 **Etapa 4:** Executando query...")

            inicio = time.time()

            # EXECUTAR COM TIMEOUT + CONFIDENCE SCORE (P0.3)
            crew = get_crew()
            crew_instance = crew.get_crew(user_input)

            # Usar novo método com confidence score
            crew_response = crew.execute_with_confidence(
                crew_instance, user_input)
            result = crew_response['resposta']
            confidence = crew_response['confidence']
            metadata = crew_response['metadata']

            tempo_decorrido = time.time() - inicio

            # ========== AUDITORIA: Registrar interação com CONFIANÇA ==========
            tempo_ms = int(tempo_decorrido * 1000)
            status_auditoria = "SUCCESS" if result != ERRO_MENSAGENS['GENERIC_ERROR'] else "ERROR"

            log_to_audit(
                pergunta=user_input,
                resposta=result[:5000],
                status=status_auditoria,
                tempo_ms=tempo_ms,
                user_ip=st.session_state.get('user_ip', 'STREAMLIT'),
                json_intent={},
                confidence=confidence,  # ✅ P0.3: Score de confiança agora registrado!
                periodo_dados_inicio=metadata.period_start,
                periodo_dados_fim=metadata.period_end,
            )

            # Finalizar status
            status_box.write(f"📊 **Etapa 5:** Formatando resposta...")
            status_box.update(
                label=f"✅ Concluído em {tempo_decorrido:.2f}s",
                state="complete",
                expanded=False
            )

            # ========== P0.3: MOSTRAR RESPOSTA COM CONFIDENCE BADGE ==========
            st.markdown(result)
            
            # Badge de confiança com cores
            if confidence >= 80:
                badge_color = "🟢"
                badge_text = f"Confiança Alta ({confidence:.0f}%)"
            elif confidence >= 50:
                badge_color = "🟡"
                badge_text = f"Confiança Média ({confidence:.0f}%)"
            else:
                badge_color = "🔴"
                badge_text = f"Confiança Baixa ({confidence:.0f}%)"
            
            st.markdown(f"{badge_color} **{badge_text}** | Período: {metadata.period_start} até {metadata.period_end}")
            
            # Mostrar aviso se houver
            if metadata.warning_messages:
                for warning in metadata.warning_messages:
                    st.warning(warning)

            # ========== MELHORIA: FEEDBACK DO USUÁRIO ==========
            col1, col2, col3 = st.columns([1, 1, 3])

            with col1:
                if st.button("👍 Útil"):
                    st.session_state.feedback = "positive"
                    st.success("Obrigado! Sua opinião nos ajuda.")

            with col2:
                if st.button("👎 Não"):
                    st.session_state.feedback = "negative"
                    st.info("Desculpe. Tentaremos melhorar.")

            # Salvar resultado no histórico
            st.session_state.messages.append(
                {"role": "assistant", "content": result}
            )

        except Exception as e:
            error_msg = ERRO_MENSAGENS['GENERIC_ERROR']
            st.error(error_msg)
            logger.error(f"Erro crítico: {e}")


# ========== SIDEBAR (MELHORADO) ==========
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1200px-Python-logo-notext.svg.png", width=50)
    st.title("⚙️ Painel de Controle")

    st.markdown("---")

    # Guia de Uso
    with st.expander("📚 Como Perguntar?", expanded=True):
        st.info("💡 **Dica:** O sistema entende erros de digitação!")
        st.markdown("""
        **Exemplos válidos:**
        - "Quais os 5 maiores fornecedores?"
        - "Quanto foi pago para Energisa em 2024?"
        - "Gastos do Campus Lagarto em junho"
        """)

    st.markdown("---")

    # Configuração
    st.subheader("⚙️ Configuração IA")
    provider = st.radio(
        "Modelo:", ["OpenAI (GPT-4o)", "Ollama (Local)"], index=0)
    os.environ["LLM_PROVIDER"] = "openai" if "OpenAI" in provider else "ollama"

    st.markdown("---")

    # Downloads
    st.subheader("📂 Relatórios")
    files = sorted(glob.glob("reports/*.csv"),
                   key=os.path.getmtime, reverse=True)

    if files:
        for idx, arquivo in enumerate(files[:5]):  # Top 5 arquivos
            nome = os.path.basename(arquivo)
            with open(arquivo, "rb") as f:
                st.download_button(
                    label=f"⬇️ {nome[:30]}...",
                    data=f,
                    file_name=nome,
                    key=f"download_{idx}"
                )
    else:
        st.caption("Nenhum relatório ainda")

    st.markdown("---")

    # Nova conversa
    if st.button("🧹 Nova Conversa", use_container_width=True):
        st.session_state.messages = []
        st.session_state.feedback = None
        st.rerun()

    # ========== MELHORIA: ANALYTICS ==========
    st.markdown("---")
    st.subheader("📊 Sessão Atual")
    total_mensagens = len([m for m in st.session_state.get(
        'messages', []) if m['role'] == 'user'])
    st.metric("Perguntas", total_mensagens)


# ========== INTERFACE PRINCIPAL ==========
st.title("🏛️ IFS Transparência Inteligente")
st.markdown("#### *Seu assistente virtual para análise de dados públicos.*")

# ========== INICIALIZAÇÃO ==========
init_audit_logging()  # Criar tabela de auditoria se necessário

# Inicializar histórico
if "messages" not in st.session_state:
    st.session_state.messages = []

if "feedback" not in st.session_state:
    st.session_state.feedback = None

# ========== TELA INICIAL ==========
if len(st.session_state.messages) == 0:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        "👋 Olá! Faça perguntas sobre os gastos públicos do IFS em português natural.")
    st.markdown("##### 🚀 Tente uma dessas consultas:")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🏆 Top 5 Fornecedores", use_container_width=True):
            process_input("Quais são os 5 maiores fornecedores?")

        if st.button("🏫 Gastos Campus Lagarto", use_container_width=True):
            process_input("Qual o gasto total do Campus Lagarto em 2024?")

    with col2:
        if st.button("💰 Total Pago Energisa", use_container_width=True):
            process_input("Quanto foi pago para Energisa este ano?")

        if st.button("📊 Gasto Total IFS", use_container_width=True):
            process_input("Qual o valor total gasto pelo IFS?")

# ========== RENDERIZAR CHAT ==========
else:
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# ========== INPUT DO USUÁRIO ==========
if prompt := st.chat_input("Digite sua pergunta (ex: Maiores fornecedores...)"):
    process_input(prompt)
