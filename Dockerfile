# Multi-stage Dockerfile para IFS Transparência Chatbot v2.0
# Usa Python 3.13-slim para otimização e performance

FROM python:3.13-slim AS builder

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
FROM python:3.13-slim

WORKDIR /app

# Metadados
LABEL maintainer="IFS Chatbot Team"
LABEL version="2.0.0"
LABEL description="IFS Chatbot v2.0 - AI-powered financial transparency system"

# Variáveis de ambiente importantes
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_LOGGER_LEVEL=warning \
    PYTHONOPTIMIZE=2

# Criar diretórios necessários
RUN mkdir -p /app/reports /app/dados_brutos /app/etl_scripts /app/.streamlit

# Copiar dependências do builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

# Copiar código da app
COPY . .

# Permissões de acesso
RUN chmod -R 755 /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501').read(); exit(0)" || exit 1

# Exposer porta
EXPOSE 8501

# Default command: executar Streamlit
CMD ["streamlit", "run", "app_v2.py", "--server.address=0.0.0.0", "--server.port=8501"]
