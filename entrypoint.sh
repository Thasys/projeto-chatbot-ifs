#!/bin/bash
# Script robusto com diagnóstico completo

echo "============================================"
echo "Diagnóstico de Inicialização do Chatbot IFS"
echo "============================================"

# 1. Verificar valores das variáveis
echo ""
echo "1. Variáveis de Ambiente:"
echo "   PORT = [$PORT]"
echo "   HOME = [$HOME]"
echo "   PWD = [$PWD]"
echo "   PATH = [$PATH]"

# 2. Verificar se Python está instalado
echo ""
echo "2. Verificação de Python:"
which python3
python3 --version
which python
python --version 2>/dev/null || echo "   python (alias) não encontrado"

# 3. Verificar se streamlit está instalado
echo ""
echo "3. Verificação de Streamlit:"
python3 -m pip list | grep -i streamlit

# 4. Definir PORT com fallback
: ${PORT:=8501}
echo ""
echo "4. Porta Final que será usada:"
echo "   PORT=$PORT (tipo: $([[ $PORT =~ ^[0-9]+$ ]] && echo 'INTEGER OK' || echo 'ERROR: NOT INTEGER'))"

# 5. Listar arquivos no app
echo ""
echo "5. Arquivos no /app:"
ls -la /app/*.py 2>/dev/null | head -5
echo "   ... (truncado)"

# 6. Iniciar Streamlit com informações
echo ""
echo "============================================"
echo "Iniciando Streamlit..."
echo "Comando: python3 -m streamlit run app_v2.py --server.address=0.0.0.0 --server.port=$PORT --server.headless=true"
echo "============================================"
echo ""

exec python3 -m streamlit run app_v2.py \
    --server.address=0.0.0.0 \
    --server.port=$PORT \
    --server.headless=true
