#!/bin/bash
# Entrypoint script para Railway
# Lida com a porta dinâmica injetada pelo Railway

# Se PORT não estiver definida, usa 8501 por padrão
PORT=${PORT:-8501}

# Exportar para que seja visível ao processo filho
export PORT

# Executar Streamlit com a porta correta
exec python -m streamlit run app_v2.py \
  --server.address=0.0.0.0 \
  --server.port=$PORT \
  --server.headless=true
