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
    STREAMLIT_LOGGER_LEVEL=warning

# Criar diretórios necessários
RUN mkdir -p /app/reports /app/data/raw /app/etl /app/logs /app/.streamlit

# Copiar dependências do builder (CORRIGIDO: python3.12, não python3.13)
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copiar código da app
COPY . .

# Copiar e preparar entrypoint script com diagnóstico
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh && \
    # Garantir que usa LF ao invés de CRLF (importante em Windows)
    sed -i 's/\r$//' /app/entrypoint.sh

# Permissões de acesso
RUN chmod -R 755 /app

# Exposer porta (dinâmica para Railway)
EXPOSE 8501

# Usar entrypoint script com diagnóstico completo
# ENTRYPOINT passa o controle para o script
# Script vai loguear PORT e verificar variáveis antes de iniciar Streamlit
ENTRYPOINT ["/app/entrypoint.sh"]
