# 📖 GUIA COMPLETO - IFS TRANSPARÊNCIA IA

## Sistema de Análise Inteligente de Dados Públicos

**Versão:** 2.0 Production-Ready  
**Data:** 27 de Março de 2026  
**Status:** ✅ Pronto para Uso  

---

# 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Requisitos](#requisitos)
3. [Opção 1: Usar Online (Local)](#opção-1-usar-online-local)
4. [Opção 2: Usar com Docker](#opção-2-usar-com-docker)
5. [Como Usar o Sistema](#como-usar-o-sistema)
6. [Exemplos Práticos](#exemplos-práticos)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

# 🎯 VISÃO GERAL

O **IFS Transparência IA** é um assistente virtual inteligente que responde perguntas sobre gastos públicos do Instituto Federal do Sertão (IFS) usando:

- 🤖 **CrewAI** - Agentes inteligentes
- 🧠 **OpenAI GPT-4** - Modelo de linguagem
- 🗄️ **MySQL** - Banco de dados
- 🌐 **Streamlit** - Interface web
- 📊 **ETL Automático** - Coleta de dados diária
- 📋 **Auditoria** - Rastreamento completo (Lei LAI)
- 🟢 **Confidence Scores** - Transparência de confiança
- 🐳 **Docker** - Containerização (produção)
- ⚖️ **Nginx** - Load balancer (alta disponibilidade)

---

# 📦 REQUISITOS

## Opção 1: Online (Desenvolvimento Local)

```
✅ Requerido:
  • Python 3.9+
  • MySQL 8.0+
  • Git
  • ~2 GB RAM disponível
  
✅ Recomendado:
  • VS Code
  • 4+ GB RAM total
  • Conexão internet estável
```

## Opção 2: Docker (Recomendado para Produção)

```
✅ Requerido:
  • Docker Desktop (Windows/Mac) ou Docker (Linux)
  • Docker Compose
  • ~4 GB RAM disponível
  • ~5 GB espaço em disco
  
✅ Recomendado:
  • 8+ GB RAM total
  • SSD (mais rápido)
  • Conexão internet estável
```

---

# 🌐 OPÇÃO 1: USAR ONLINE (LOCAL)

## Passo 1: Clonar Repositório

```bash
# Abrir terminal/PowerShell
git clone https://github.com/Thasys/projeto-chatbot-ifs.git
cd projeto-chatbot-ifs
```

## Passo 2: Configurar Variáveis de Ambiente

```bash
# Editar arquivo .env (abrir com editor de texto)
# Adicionar suas credenciais:

DB_HOST=localhost
DB_PORT=3306
DB_NAME=dw_ifs_gastos
DB_USER=root
DB_PASS=sua_senha_mysql
API_KEY=sua_api_key_transparencia
OPENAI_API_KEY=sk-xxxxxxxxxxx

LLM_PROVIDER=openai
OPENAI_MODEL_NAME=gpt-4o
```

### Onde Encontrar as Credenciais?

**DB_HOST, DB_PORT, DB_USER, DB_PASS:**
- Se tem MySQL local: `localhost`, `3306`, `root`, `sua_senha`
- Se tem servidor: `IP_do_servidor`, `3306`, `usuario`, `senha`

**API_KEY:**
- Obtém em: https://dadosabertos.ifs.edu.br (Portal da Transparência)

**OPENAI_API_KEY:**
- Obtém em: https://platform.openai.com/api-keys
- Formato: `sk-...` (64 caracteres)

## Passo 3: Instalar Dependências

```bash
# Criar ambiente virtual (recomendado)
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Mac/Linux)
source venv/bin/activate

# Instalar packages
pip install -r requirements.txt
```

⏰ **Tempo esperado:** 5-10 minutos

## Passo 4: Inicializar Banco de Dados

```bash
# Criar tabela de auditoria (primeira execução)
python audit_logger.py
```

**Output esperado:**
```
✅ Tabela chat_audit_log criada/verificada com sucesso
```

## Passo 5: Rodar Streamlit

```bash
streamlit run app_v2.py
```

**Output esperado:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.X:8501
```

## Passo 6: Acessar a App

Abrir no navegador:
```
http://localhost:8501
```

✅ **Pronto! A app está rodando localmente.**

---

### Parar a App

```bash
# Pressionar Ctrl+C no terminal
^C

# Ou fechar o terminal
```

---

# 🐳 OPÇÃO 2: USAR COM DOCKER

## ✅ Vantagens do Docker

```
✅ Nenhuma instalação local necessária
✅ Ambiente isolado e reproducível
✅ Fácil de escalar (2+ instâncias)
✅ Load balancer automático
✅ Backup e restore simplificados
✅ Compatível com qualquer OS
```

## Passo 1: Instalar Docker

### Windows
```
1. Baixar: https://www.docker.com/products/docker-desktop
2. Executar installer
3. Reiniciar PC
4. Abrir PowerShell
5. Verificar: docker --version
```

### Mac
```bash
# Via Homebrew (recomendado)
brew install docker

# Ou baixar: https://www.docker.com/products/docker-desktop
```

### Linux (Ubuntu/Debian)
```bash
# Instalar Docker
sudo apt update
sudo apt install docker.io docker-compose

# Adicionar permissões (sem sudo)
sudo usermod -aG docker $USER
newgrp docker
```

**Verificar instalação:**
```bash
docker --version
docker-compose --version
```

## Passo 2: Clonar Repositório

```bash
git clone https://github.com/Thasys/projeto-chatbot-ifs.git
cd projeto-chatbot-ifs
```

## Passo 3: Configurar .env

Mesmo que acima, mas agora:

```bash
# IMPORTANTE: DB_HOST deve ser "mysql" (nome do serviço Docker)
DB_HOST=mysql          # ← NÃO localhost!
DB_PORT=3306
DB_NAME=dw_ifs_gastos
DB_USER=root
DB_PASS=meupasse123456
API_KEY=sua_api_key
OPENAI_API_KEY=sk-xxxx
```

## Passo 4: Build das Imagens

```bash
# Construir imagens Docker
docker-compose build
```

⏰ **Tempo esperado:** 3-5 minutos (primeira vez)  
⚠️ **Importante:** Precisa estar no diretório com `docker-compose.yml`

**Output esperado:**
```
[+] Building 45.2s (15/15) FINISHED
 => [app1 stage-1 8/8] COMPLETE
 => [app2 stage-1 8/8] COMPLETE
```

## Passo 5: Iniciar Serviços

```bash
# Rodar no background (-d = detached)
docker-compose up -d
```

⏰ **Tempo esperado:** 30-60 segundos

**Output esperado:**
```
[+] Running 5/5
 ✔ Container ifs_mysql      Running
 ✔ Container ifs_app1       Running
 ✔ Container ifs_app2       Running
 ✔ Container ifs_nginx      Running
 ✔ Container ifs_etl        Running
```

## Passo 6: Verificar Status

```bash
# Ver todos os containers
docker-compose ps

# Ver logs detalhados
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f app1
```

## Passo 7: Acessar a App

Abrir no navegador:
```
http://localhost:80       ← Load balancer (recomendado)
http://localhost:8501     ← App 1 (direto)
http://localhost:8502     ← App 2 (direto)
```

✅ **Pronto! A app está rodando com Docker.**

---

### Parar os Serviços

```bash
# Parar containers (mantém dados)
docker-compose down

# Parar e remover volumes (CUIDADO: perde dados!)
docker-compose down -v

# Apenas pausar (sem parar)
docker-compose pause

# Resumir
docker-compose unpause
```

---

### Ver Logs em Tempo Real

```bash
# Todos os serviços
docker-compose logs -f

# Apenas app1
docker-compose logs -f app1

# Apenas nginx
docker-compose logs -f nginx

# Apenas MySQL
docker-compose logs -f mysql

# Últimas 100 linhas
docker-compose logs --tail=100 app1
```

---

### Escalar (Adicionar mais apps)

```bash
# Aumentar para 3 instâncias de app
docker-compose scale app=3

# Nginx automaticamente balanceia entre todas
```

---

# 💬 COMO USAR O SISTEMA

## Interface Principal

```
┌─────────────────────────────────────────┐
│     IFS TRANSPARÊNCIA INTELIGENTE       │
│   Seu assistente para dados públicos    │
└─────────────────────────────────────────┘

[Caixa de Texto para Pergunta]
```

## Fazer uma Pergunta

### 1️⃣ Digite sua Pergunta

Exemplos:
```
"Quanto Energisa recebeu em 2023?"
"Quais foram os 5 maiores fornecedores?"
"Gastos do Campus Lagarto em junho"
"Total de despesas com pessoal"
```

### 2️⃣ Pressione Enter (ou clique Enviar)

O sistema vai:
1. 🔍 Analisar sua pergunta
2. 🔎 Buscar as entidades (Energisa, Campus, etc)
3. 🏗️ Construir a query SQL
4. 📊 Executar no banco
5. 📝 Formatar resposta em português
6. 🟢 Mostrar score de confiança

### 3️⃣ Veja a Resposta com Metadados

```
R$ 1.500.000,00

🟢 Confiança Alta (95%)
Período: 2023-01-01 até 2023-12-31
```

---

## Componentes da Interface

### Histórico de Conversa
- ✅ Todas as perguntas/respostas anteriores
- ✅ Clique "🧹 Nova Conversa" para limpar

### Configurações (Sidebar Esquerda)
- 📚 Como Perguntar? (exemplos)
- ⚙️ Modelo IA (OpenAI vs Ollama)
- 📂 Relatórios (download de CSVs)
- 📊 Métricas da sessão

### Badges de Confiança

```
🟢 Confiança Alta (80-100%)       Resposta muito confiável
🟡 Confiança Média (50-79%)       Responder com cuidado
🔴 Confiança Baixa (<50%)         Verificar dados adicionais
```

---

# 📚 EXEMPLOS PRÁTICOS

## Exemplo 1: Pergunta Simples

**Entrada:**
```
"Quanto Energisa gastou em 2023?"
```

**Saída esperada:**
```
Segundo os dados do IFS, Energisa recebeu R$ 1.500.000,00 
durante o ano de 2023 em contratos com a instituição.

🟢 Confiança Alta (92%)
Período: 2023-01-01 até 2023-12-31
```

---

## Exemplo 2: Ranking (Top 5)

**Entrada:**
```
"Quais foram os 5 maiores fornecedores em 2024?"
```

**Saída esperada:**
```
Os 5 maiores fornecedores do IFS em 2024 foram:

1. Energisa Alagoas - R$ 2.500.000,00
2. Telebrás - R$ 1.800.000,00
3. Instituto de Pesquisa - R$ 1.200.000,00
4. Metalúrgica X - R$ 950.000,00
5. Serviços Gerais Y - R$ 750.000,00

🟢 Confiança Alta (89%)
Período: 2024-01-01 até 2024-12-31
```

---

## Exemplo 3: Filtro por Campus

**Entrada:**
```
"Qual foi o gasto do Campus Lagarto em junho de 2024?"
```

**Saída esperada:**
```
O Campus Lagarto gastou R$ 125.000,00 em junho de 2024.

Principais categorias:
- Pessoal: R$ 80.000,00
- Custeio: R$ 35.000,00
- Capital: R$ 10.000,00

🟡 Confiança Média (72%)
Período: 2024-06-01 até 2024-06-30
```

---

## Exemplo 4: Pergunta Complexa

**Entrada:**
```
"Quanto a IFS gastou com TI em 2024 comparado com 2023?"
```

**Saída esperada:**
```
Comparativo de Gastos com TI:

2023: R$ 450.000,00
2024: R$ 580.000,00

Variação: +R$ 130.000,00 (28,9% aumento)

Principais fornecedores:
- Microsoft: +R$ 80.000
- Amazon AWS: +R$ 35.000
- Outros: +R$ 15.000

🟡 Confiança Média (68%)
Nota: Variação pode incluir ajustes de 
      classificação entre anos
```

---

# 🔧 TROUBLESHOOTING

## Problema 1: "Connection Refused" (Conexão Recusada)

**Mensagem:**
```
ERROR: Não conseguiu conectar ao banco de dados
Access denied for user 'root'...
```

**Solução:**

### Se está usando Online:
```bash
# 1. Verificar se MySQL está rodando
mysql -u root -p

# Se não conectar, iniciar MySQL:
# Windows: net start MySQL80
# Mac: brew services start mysql
# Linux: sudo systemctl start mysql
```

### Se está usando Docker:
```bash
# 1. Verificar se containers estão rodando
docker-compose ps

# 2. Verificar se MySQL está pronto
docker-compose logs mysql

# 3. Reiniciar tudo
docker-compose down
docker-compose up -d
```

**Verificar credenciais** em `.env`:
```bash
DB_HOST=localhost (ou mysql se Docker)
DB_USER=root
DB_PASS=sua_senha_correta
```

---

## Problema 2: "Port Already in Use" (Porta Já Está em Uso)

**Mensagem:**
```
Error binding to port 8501: Address already in use
```

**Solução:**

### Online:
```bash
# Mudar porta
streamlit run app_v2.py --server.port 8502
```

### Docker:
```bash
# Editar docker-compose.yml
# Trocar porta 8501 para 8503

ports:
  - "8503:8501"  # Mudado de 8501

# Reiniciar
docker-compose down
docker-compose up -d
```

---

## Problema 3: "OpenAI API Key Invalid" (Chave Inválida)

**Mensagem:**
```
openai.error.AuthenticationError: Invalid API key
```

**Solução:**

```bash
# 1. Verificar chave em .env
echo $OPENAI_API_KEY

# 2. Se vazio, adicionar ao .env:
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxx

# 3. Regenerar chave em:
https://platform.openai.com/api-keys

# 4. Reiniciar app
# Online: Ctrl+C + streamlit run app_v2.py
# Docker: docker-compose restart app1 app2
```

---

## Problema 4: "Slow Response" (Respostas Lentas)

**Solução:**

### Online:
```bash
# Verificar memória disponível
# Se <1GB RAM, fechar outras apps

# Verificar MySQL
SHOW PROCESSLIST;  # Ver queries em execução
```

### Docker:
```bash
# Verificar recursos
docker stats

# Se CPU/RAM altos, aumentar limites em docker-compose.yml
# Deploy documentação: https://docs.docker.com/compose/
```

---

## Problema 5: "Database Not Found" (Banco Não Existe)

**Mensagem:**
```
Unknown database 'dw_ifs_gastos'
```

**Solução:**

```bash
# 1. Criar banco (MySQL)
mysql -u root -p
CREATE DATABASE dw_ifs_gastos;
EXIT;

# 2. Importar dados (se tiver arquivo SQL)
mysql -u root -p dw_ifs_gastos < dados.sql

# 3. Verificar que tabelas existem
mysql -u root -p -e "USE dw_ifs_gastos; SHOW TABLES;"
```

---

## Problema 6: "Timeout" (Demorou muito)

**Mensagem:**
```
⏱️ Operação demorou muito. Tente uma pergunta mais específica.
```

**Solução:**

```
• Use perguntas mais simples
• Evite períodos muito longos
• Tente filtrar por campus
• Reduz conexões simultâneas
```

---

# ❓ FAQ

## P: Quais dados posso consultar?

**R:** Qualquer dado público do IFS:
```
✅ Gastos e despesas
✅ Fornecedores (pessoa física/jurídica)
✅ Campi e unidades administrativas
✅ Classificação de despesas
✅ Períodos (ano, mês, dia)
```

---

## P: O sistema tem acesso à internet?

**R:** 
- ✅ Faz login com OpenAI (precisa internet)
- ✅ Coleta dados via Portal da Transparência
- ❌ Não expõe dados para fora

---

## P: Posso usar offline?

**R:** Parcialmente:
- ✅ Online: Sim, usa OpenAI + dados em cache
- ✅ Docker: Sim (se usar Ollama local)
- ❌ Não: Se precisar de dados atualizados em tempo real

---

## P: Como atualizar os dados?

**R:**
- ✅ Online: Rodar manualmente `python etl_scripts/main.py`
- ✅ Docker: Automático! ETL roda de 24 em 24h
- ✅ Manual: `docker-compose exec etl python /app/etl_scripts/main.py`

---

## P: Posso compartilhar a URL da app?

**R:**
- ✅ Online local: Não (só no seu PC)
- ✅ Docker: Não (a menos que expor via ngrok)
- ✅ Docker em servidor: Sim! Acesse via IP do servidor

```bash
# Para compartilhar localmente via ngrok:
pip install ngrok
ngrok http 8501
# Vai gerar URL como: https://xxxx.ngrok.io
```

---

## P: Como faço backup dos dados?

**R:**

### Online:
```bash
# Backup MySQL
mysqldump -u root -p dw_ifs_gastos > backup.sql

# Restaurar
mysql -u root -p dw_ifs_gastos < backup.sql
```

### Docker:
```bash
# Backup do volume MySQL
docker-compose exec mysql mysqldump -uroot -p$DB_PASS dw_ifs_gastos > backup.sql
```

---

## P: Quanto custa rodar isso?

**R:**

### Online:
```
✅ Grátis (você roda em seu PC)
💰 Custo: OpenAI API (paga conforme usa)
   ~$0.01 por pergunta média
```

### Docker:
```
✅ Grátis (você roda em seu servidor/PC)
💰 Custo: OpenAI API (paga conforme usa)
   ~$0.01 por pergunta média
💰 Servidor (se usar cloud): $5-50/mês
```

---

## P: Qual a melhor performance?

**R:**
1. **Docker com 2+ apps** (Recommended) → 99.5% uptime
2. **Docker com 1 app** → 95% uptime
3. **Online local** → Depende do PC

---

## P: Como monitorar em produção?

**R:**

### Docker:
```bash
# Ver recursos
docker stats

# Ver logs
docker-compose logs -f

# Health checks
curl http://localhost/health
```

### Adicionar monitoramento real:
```bash
# Prometheus + Grafana
docker run -d prom/prometheus
docker run -d grafana/grafana
```

---

## P: Posso customizar as respostas?

**R:** Sim! Editar em `crew_definition_v2.py`:

```python
# Mudar prompts dos agentes
# Exemplo: Public Analyst adicionar emojis, tabelas, etc
```

---

## P: Como reportar bugs?

**R:**
```
1. GitHub Issues: https://github.com/Thasys/projeto-chatbot-ifs/issues
2. Email: suporte@ifs.edu.br
3. Documentação: Ver ROADMAP_MELHORIAS.md
```

---

# 🎓 RECURSOS ADICIONAIS

## Documentação Técnica

```
📖 IMPLEMENTACAO_P01_ETL_AUTOMATICO.md      → ETL setup
📖 IMPLEMENTACAO_P02_AUDIT_LOGGING.md       → Auditoria
📖 IMPLEMENTACAO_P03_CONFIDENCE_SCORES.md   → Confidence
📖 IMPLEMENTACAO_P04_DOCKER_LOADBALANCER.md → Docker
📖 ROADMAP_MELHORIAS.md                     → Futuro
📖 ANALISE_ARQUITETURAL_CRITICA.md          → Arquitetura
```

## Links Úteis

```
🔗 GitHub: https://github.com/Thasys/projeto-chatbot-ifs
🔗 Portal Transparência: https://dadosabertos.ifs.edu.br
🔗 OpenAI API: https://platform.openai.com
🔗 Streamlit Docs: https://docs.streamlit.io
🔗 Docker Docs: https://docs.docker.com
```

---

## Comandos Rápidos

### Online
```bash
# Setup
git clone https://...
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Run
streamlit run app_v2.py
```

### Docker
```bash
# Setup
git clone https://...
# Editar .env

# Run
docker-compose up -d

# Logs
docker-compose logs -f

# Stop
docker-compose down
```

---

# 🎉 CONCLUSÃO

Você está pronto para usar o **IFS Transparência IA**!

**Dúvidas?**
- Consulte este guia
- Verifique os logs
- Procure no FAQ

**Boa sorte! 🚀**

---

**Última atualização:** 27 de Março de 2026  
**Versão:** 2.0 Production  
**Status:** ✅ Pronto para Uso
