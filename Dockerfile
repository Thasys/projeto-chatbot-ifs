# Multi-stage Dockerfile para IFS Transparência Chatbot v2.0
# Otimizado para Railway + Python 3.12

FROM python:3.12-slim AS builder

WORKDIR /app

# Instalar dependências do sistema (compilação)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production image
FROM python:3.12-slim

WORKDIR /app

# Metadados
LABEL maintainer="IFS Chatbot Team"
LABEL version="2.0.0"
LABEL description="IFS Chatbot v2.0 - AI-powered financial transparency system"

# Variáveis de ambiente importantes
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_LOGGER_LEVEL=warning \
    PYTHONOPTIMIZE=2

# Criar diretórios necessários
RUN mkdir -p /app/reports /app/dados_brutos /app/etl_scripts /app/.streamlit

# Copiar dependências do builder (CORRIGIDO: python3.12, não python3.13)
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copiar código da app
COPY . .

# Permissões de acesso
RUN chmod -R 755 /app

# Exposer porta (dinâmica para Railway)
EXPOSE 8501

# Default command: executar Streamlit com porta dinâmica
# Railway injeta PORT via variável de environment
# Usar 'sh -c' para compatibilidade com substituição de variáveis
CMD sh -c "python -m streamlit run app_v2.py --server.address=0.0.0.0 --server.port=\${PORT:-8501} --server.headless=true"
