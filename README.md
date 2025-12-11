# 🏛️ IFS Transparência Inteligente

Assistente virtual baseado em Agentes de IA (CrewAI) para análise e consulta de dados financeiros públicos do Instituto Federal de Sergipe (IFS). O sistema permite consultas em linguagem natural, convertendo perguntas em SQL seguro e otimizado.

## 🚀 Funcionalidades

- **Consultas Naturais:** "Quanto a Energisa recebeu em 2024?"
- **Busca Fuzzy (Inteligente):** Entende erros de digitação ("Enegisa", "Propria") e normaliza acentos.
- **Detecção de Intenção:** Identifica automaticamente se o usuário quer um Ranking, um Total ou uma Lista detalhada.
- **Proteção (Guardrails):** Bloqueia perguntas vagas que poderiam travar o banco.
- **Relatórios:** Gera arquivos CSV automaticamente para grandes volumes de dados.

## 🛠️ Tecnologias

- **Frontend:** Streamlit
- **Orquestração:** CrewAI (Agentes, Tarefas e Processos)
- **Banco de Dados:** MySQL (com Views Semânticas)
- **Ferramentas:** Pandas, SQLAlchemy, RapidFuzz, Unidecode

## ⚙️ Instalação

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/SEU-USUARIO/nome-do-repo.git
   cd nome-do-repo