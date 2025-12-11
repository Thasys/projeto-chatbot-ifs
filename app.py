import streamlit as st
import os
import time
import glob
import pandas as pd
from crew_definition import IFSCrew
from llm_factory import LLMFactory
from db_connection import DBConnection

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="IFS Transparência IA",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS PERSONALIZADO (UX/UI) ---
st.markdown("""
<style>
    /* Estilo do Chat */
    .stChatMessage {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #e9ecef;
        margin-bottom: 10px;
    }
    /* Destaque para tabelas */
    div[data-testid="stMarkdownContainer"] table {
        width: 100%;
        border-collapse: collapse;
    }
    div[data-testid="stMarkdownContainer"] th {
        background-color: #004a80; /* Cor Institucional Azul */
        color: white;
        padding: 8px;
    }
    div[data-testid="stMarkdownContainer"] td {
        border-bottom: 1px solid #ddd;
        padding: 8px;
    }
    /* Cards de Sugestão */
    .suggestion-btn {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        transition: 0.3s;
    }
    .suggestion-btn:hover {
        background-color: #f0f8ff;
        border-color: #004a80;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CACHE E SINGLETONS ---


@st.cache_resource
def get_db_connection():
    return DBConnection()

# --- 4. LÓGICA DE PROCESSAMENTO ---


def process_input(user_input):
    """Gerencia o fluxo de envio de mensagem para a CrewAI."""
    if not user_input:
        return

    # 1. Adiciona pergunta ao histórico
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Resposta do Assistente
    with st.chat_message("assistant"):
        status_box = st.status(
            "🧠 **Processando solicitação...**", expanded=True)

        try:
            # Timer
            start_time = time.time()

            # Inicializa a Crew
            status_box.write(
                "🕵️‍♂️ **Detetive de Dados:** Identificando entidades e intenção...")
            ifs_crew = IFSCrew()
            crew_instance = ifs_crew.get_crew(user_input)

            status_box.write(
                "👷 **Arquiteto SQL:** Consultando base de dados financeira...")

            # Execução
            result = crew_instance.kickoff()

            # Finalização
            end_time = time.time()
            duration = end_time - start_time

            status_box.write("📊 **Analista Público:** Formatando resposta...")
            status_box.update(
                label=f"✅ Concluído em {duration:.2f}s", state="complete", expanded=False)

            # Exibe resposta
            st.markdown(result)
            st.session_state.messages.append(
                {"role": "assistant", "content": result})

            # Verifica se gerou CSV para oferecer download
            check_for_downloads(str(result))

        except Exception as e:
            status_box.update(label="❌ Erro no processamento", state="error")
            st.error(f"Ocorreu um erro inesperado: {str(e)}")


def check_for_downloads(result_text):
    """Verifica se o agente mencionou um arquivo gerado e atualiza a interface."""
    if "relatorio_" in result_text or ".csv" in result_text:
        time.sleep(0.5)
        st.rerun()


# --- 5. SIDEBAR (GUIA E CONFIGURAÇÃO) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1200px-Python-logo-notext.svg.png", width=50)
    st.title("Painel de Controle")

    st.markdown("---")

    # Guia de Uso
    with st.expander("📚 **Como perguntar?**", expanded=True):
        st.info("💡 **Dica:** O sistema entende erros de digitação!")
        st.markdown("""
        **1. Rankings e Totais:**
        - "Quais os 3 maiores fornecedores?"
        - "Qual o total gasto em 2024?"
        
        **2. Busca Específica:**
        - "Pagamentos para a Energisa"
        - "Despesas do Campus Lagarto em Junho"
        
        **3. Detalhes:**
        - "Liste os gastos da unidade Propria"
        """)

    st.markdown("---")

    # Seleção de Modelo
    st.subheader("⚙️ Configuração IA")
    provider = st.radio(
        "Modelo:", ["OpenAI (GPT-4o)", "Ollama (Local)"], index=0)

    if "OpenAI" in provider:
        os.environ["LLM_PROVIDER"] = "openai"
    else:
        os.environ["LLM_PROVIDER"] = "ollama"

    # Área de Downloads
    st.markdown("---")
    st.subheader("📂 Relatórios")
    files = glob.glob("reports/*.csv")
    files.sort(key=os.path.getmtime, reverse=True)

    if files:
        latest_file = files[0]
        file_name = os.path.basename(latest_file)
        with open(latest_file, "rb") as f:
            st.download_button(
                label="⬇️ Baixar Último CSV",
                data=f,
                file_name=file_name,
                mime="text/csv"
            )
    else:
        st.caption("Nenhum relatório gerado ainda.")

    # Botão de Limpeza
    if st.button("🧹 Nova Conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 6. INTERFACE PRINCIPAL ---

st.title("🏛️ IFS Transparência Inteligente")
st.markdown(
    "#### *Seu assistente virtual para análise de dados públicos financeiros.*")

# Inicializa Histórico
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- TELA DE ONBOARDING (APARECE SE NÃO HÁ MENSAGENS) ---
if len(st.session_state.messages) == 0:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👋 Olá! Eu sou seu Agente de Transparência. Não precisa saber SQL. Apenas pergunte em português natural.")
    st.markdown("##### 🚀 Experimente uma destas consultas:")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🏆 Quais os 3 maiores fornecedores?", use_container_width=True):
            process_input(
                "Quais são os 3 maiores fornecedores pelo valor total recebido?")

        if st.button("🏫 Gastos do Campus Lagarto (Junho/24)", use_container_width=True):
            process_input(
                "Liste os pagamentos do Campus Lagarto em Junho de 2024.")

    with col2:
        if st.button("🏢 Quanto foi pago a Energisa?", use_container_width=True):
            process_input("Quanto foi pago para a Energisa este ano?")

        if st.button("💰 Qual o Gasto Total do IFS?", use_container_width=True):
            process_input("Qual o valor total gasto pelo IFS em 2024?")

# --- RENDERIZA O CHAT ---
else:
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# --- INPUT DO USUÁRIO ---
if prompt := st.chat_input("Digite sua pergunta aqui (ex: Gastos com Diárias em 2024)..."):
    process_input(prompt)
