# 🔧 PLANO DE MELHORIA ARQUITETURAL - CHATBOT IFS

**Data:** 24 de Março de 2026  
**Baseado em:** ANALISE_ARQUITETURAL_CRITICA.md  
**Objetivo:** Evoluir de 7.6/10 → 9.2/10 em qualidade arquitetural

---

## 📋 RESUMO EXECUTIVO

```
PROBLEMAS IDENTIFICADOS: 8 (4 críticos, 4 médios)
TEMPO PARA IMPLEMENTAR CRÍTICOS: 8-10 horas
TEMPO PARA IMPLEMENTAR TUDO: 20-25 horas (2-3 dias de dev full-time)

RESULTADO ESPERADO:
├─ Sistema pronto para produção real
├─ Cobertura legal/compliance (LAI)
├─ Escalável para 1.000+ usuários
├─ Auditoria completa
└─ Score: 9.2/10
```

---

## 🔴 PROBLEMAS CRÍTICOS (P0)

### P0.1: ETL SEM AUTOMAÇÃO

**Status Atual:**
```bash
$ python etl_scripts/main.py  # Manual, irregular execution
# Resultado: Dados podem estar 1-7 dias atrasados
```

**Impacto:** Violação de "Transparência Pública" com dados velhos

**Solução:**

#### Opção A: GitHub Actions (RECOMENDADO)
```yaml
# .github/workflows/etl-daily.yml
name: Daily ETL Pipeline

on:
  schedule:
    - cron: '0 23 * * *'  # 23:00 UTC (20:00 BRT) todo dia
  workflow_dispatch:  # Também manual

jobs:
  etl:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run ETL Pipeline
        env:
          DB_HOST: ${{ secrets.DB_HOST }}
          DB_USER: ${{ secrets.DB_USER }}
          DB_PASS: ${{ secrets.DB_PASS }}
          # ... outras variáveis
        run: |
          python etl_scripts/main.py 2>&1 | tee etl_output.log
      
      - name: Check if failed
        if: failure()
        run: |
          curl -X POST -H 'Content-type: application/json' \
            -d '{"text":"ETL Failed! Check logs"}' \
            ${{ secrets.SLACK_WEBHOOK }}
      
      - name: Upload logs
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: etl-logs
          path: etl_output.log
```

**Tempo:** 1-2 horas  
**Benefícios:**
- ✅ Automático diário
- ✅ Logs preservados (GitHub)
- ✅ Alert se falha (Slack)
- ✅ Histórico completo
- ✅ Sem servidor extra

---

#### Opção B: APScheduler (Se server próprio)
```python
# etl_scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from etl_scripts.main import run_etl
import logging

logger = logging.getLogger(__name__)

def schedule_etl():
    scheduler = BackgroundScheduler()
    
    # Rodar ETL todo dia às 23:00
    scheduler.add_job(
        func=run_etl_safe,
        trigger="cron",
        hour=23,
        minute=0,
        id='daily_etl',
        name='Daily ETL Pipeline',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("✅ ETL Scheduler iniciado. Próxima execução: amanhã às 23:00")
    return scheduler

def run_etl_safe():
    try:
        logger.info("🚀 Iniciando ETL Pipeline...")
        run_etl()
        logger.info("✅ ETL concluído com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro no ETL: {str(e)}")
        # Send Slack alert
        send_slack_alert(f"ETL FAILED: {str(e)}")

if __name__ == "__main__":
    scheduler = schedule_etl()
    # Manter vivo (em produção com supervisord ou systemd)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
```

**Tempo:** 2-3 horas  
**Requisito:** Servidor sempre ligado

---

### P0.2: SEM AUDIT LOGGING

**Status Atual:**
```python
# Nenhuma log de qual pergunta foi feita, qual resposta dada
# Violação: Lei de Acesso à Informação não atendida
```

**Impacto:** Impossível auditar, nenhuma comprovação legal

**Solução:**

```sql
-- Criar tabela de auditoria
CREATE TABLE chat_audit_log (
  id INT AUTO_INCREMENT PRIMARY KEY,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  user_ip VARCHAR(45),
  user_id VARCHAR(100),
  
  -- Input
  pergunta_original TEXT NOT NULL,
  
  -- Processamento
  json_intent JSON,              -- Output do Data Detective
  entidades_detectadas JSON,     -- Entidades identificadas
  sql_executado TEXT,            -- SQL gerado e executado
  
  -- Output
  resposta_final LONGTEXT,       -- Resposta ao usuário
  confidence_score FLOAT,        -- Confiança 0-100%
  
  -- Metadata
  tempo_processamento_ms INT,    -- Total milliseconds
  status ENUM('SUCCESS', 'ERROR', 'TIMEOUT', 'BLOCKED'),
  mensagem_erro TEXT,
  
  -- Rastreabilidade
  periodo_dados_inicio DATE,     -- Dados consultados de
  periodo_dados_fim DATE,        -- Dados consultados até
  data_coleta_mais_recente DATE, -- Quando foram coletados
  
  -- Filters/Contexto
  filtros_aplicados JSON,        -- UG, natureza, etc
  parametros_request JSON,       -- Tudo que veio do request
  
  -- Índices para busca rápida
  INDEX idx_timestamp (timestamp),
  INDEX idx_user_id (user_id),
  INDEX idx_status (status),
  FULLTEXT idx_ft_pergunta (pergunta_original)
);
```

**Implementação em app_v2.py:**

```python
import json
import time
from datetime import datetime
from db_connection import DBConnection

def log_to_audit(
    pergunta: str,
    json_intent: dict,
    sql_executado: str,
    resposta: str,
    confidence: float,
    tempo_ms: int,
    status: str,
    user_ip: str = None
):
    """Log tudo em chat_audit_log"""
    
    db = DBConnection()
    
    try:
        query = """
        INSERT INTO chat_audit_log (
            timestamp, user_ip, pergunta_original,
            json_intent, sql_executado, resposta_final,
            confidence_score, tempo_processamento_ms, status,
            parametros_request
        ) VALUES (
            NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        db.execute_query(query, (
            user_ip or get_user_ip(),
            pergunta,
            json.dumps(json_intent, ensure_ascii=False),
            sql_executado,
            resposta[:5000],  # Limitar tamanho
            confidence,
            tempo_ms,
            status,
            json.dumps({"source": "streamlit_app"})
        ))
        
        logger.info(f"✅ Audit log salvo para: {pergunta[:50]}...")
        
    except Exception as e:
        logger.error(f"❌ Erro ao salvar audit log: {str(e)}")
        # NÃO deixar erro de logging quebrar a aplicação
        pass

# Em app_v2.py, chamar assim:
def process_user_question(question: str):
    start_time = time.time()
    
    try:
        crew = get_crew()
        json_intent = crew.agents[0].generate_intent(question)  # Data Detective
        sql_executado = crew.agents[1].generate_sql(json_intent)  # SQL Architect
        resposta = crew.agents[2].format_response(sql_result)  # Public Analyst
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        log_to_audit(
            pergunta=question,
            json_intent=json_intent,
            sql_executado=sql_executado,
            resposta=resposta,
            confidence=calculate_confidence(json_intent),
            tempo_ms=elapsed_ms,
            status="SUCCESS",
            user_ip=request.remote_addr if request else None
        )
        
        return resposta
        
    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        log_to_audit(
            pergunta=question,
            json_intent={},
            sql_executado="",
            resposta="",
            confidence=0.0,
            tempo_ms=elapsed_ms,
            status="ERROR",
            user_ip=request.remote_addr if request else None
        )
        
        raise
```

**Tempo:** 2-3 horas  
**Benefícios:**
- ✅ Comprovação legal (LAI)
- ✅ Analytics completo
- ✅ Debug de problemas
- ✅ Detectar padrões suspeitos

---

### P0.3: SEM CONFIANÇA/EXPLICABILIDADE

**Status Atual:**
```
Usuário: "Quantos Energisa pagou?"
Bot: "Energisa recebeu R$ 1.500.000,00"
Usuário: ❓ "De quando? Como você sabe? Tem certeza?"
Bot: ❌ Silêncio
```

**Impacto:** Sem transparência = contradiz objetivo de "transparência pública"

**Solução:**

```python
# Em crew_definition.py, adicionar "response_metadata"

class AgentResponse:
    def __init__(self):
        self.resposta_texto = ""
        self.confianca = 0.0  # 0-100%
        self.periodo_dados = {"inicio": None, "fim": None}
        self.data_coleta = None
        self.registros_processados = 0
        self.avisos = []
        self.explicacao_filtros = ""

def calculate_confidence(json_intent, sql_result):
    """
    Calcular confiança de 0-100%
    
    Reduz confiança se:
    - Entidades não encontradas (70%)
    - Dados muito antigos (80%)
    - Resultado é vazio (30%)
    - Múltiplos matches fuzzy (70%)
    - Query usa padrão genérico (80%)
    """
    base_confidence = 100.0
    
    # Penalizar por fatores de risco
    if not json_intent.get("entities"):
        base_confidence -= 15  # Genérico = menos confiança
    
    if sql_result.empty:
        base_confidence -= 40  # Sem resultado = baixa confiança
    else:
        base_confidence -= max(0, 10 - len(sql_result))  # Poucos resultados = menos confiança
    
    # Penalizar se dados muito antigos
    from datetime import date, timedelta
    ultima_coleta = get_last_etl_date()
    dias_delay = (date.today() - ultima_coleta).days
    
    if dias_delay > 3:
        base_confidence -= (dias_delay * 5)  # -5% por dia de atraso
    
    return max(30, min(100, base_confidence))  # Clamp 30-100

def format_response_with_metadata(resposta_texto, metadata):
    """
    Formatar responsável (PT-BR)
    """
    resultado = f"""
{resposta_texto}

---
📋 **INFORMAÇÕES SOBRE ESTA RESPOSTA:**

🎯 **Confiança:** {metadata['confianca']:.0f}%
   └─ {'Alta confiabilidade' if metadata['confianca'] > 90 else 'Confiança média' if metadata['confianca'] > 70 else 'Confiança baixa - verificar'}

📅 **Período de Dados:** {metadata['periodo_dados']['inicio'].strftime('%d/%m/%Y')} a {metadata['periodo_dados']['fim'].strftime('%d/%m/%Y')}

🔄 **Dados Atualizados:** {metadata['data_coleta'].strftime('%d/%m/%Y às %H:%M')}

📊 **Registros Processados:** {metadata['registros_processados']:,}

⚠️ **Avisos:**
"""
    
    if metadata['avisos']:
        for aviso in metadata['avisos']:
            resultado += f"   • {aviso}\n"
    else:
        resultado += "   • Nenhum aviso\n"
    
    resultado += f"""
🔍 **Explicação dos Filtros Aplicados:**
{metadata['explicacao_filtros']}

💡 **Perguntas Similares que Você Pode Fazer:**
   • Próximas linhas similares
   • Comparação com períodos anteriores
   • Análise por categoria

---
*Resposta gerada automaticamente pelo Chatbot IFS*
*Lei de Acesso à Informação (Lei nº 12.527/2011)*
    """
    
    return resultado
```

**Tempo:** 2-3 horas  
**Benefícios:**
- ✅ Transparência real (não apenas nome)
- ✅ Usuário sabe confiança
- ✅ Avisos de dados antigos
- ✅ Explicação clara de filtros
- ✅ Responsabilidade administrativa

---

### P0.4: SEM ESCALABILIDADE

**Status Atual:**
```
┌─ Única instância Streamlit
├─ Cache em memória (não sincronizado)
├─ MySQL sem replicação
└─ Limite: 50-100 usuários simultâneos
```

**Impacto:** Crashes com picos de tráfego, sem redundância

**Solução:**

#### FASE 1: Docker + Load Balancer (3-5 horas)

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app_v2.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```yaml
# docker-compose.yml
version: '3.9'

services:
  # 3 instâncias do APP
  web1:
    build: .
    container_name: chatbot-web-1
    ports:
      - "8501:8501"
    environment:
      - DB_HOST=mysql
      - REDIS_HOST=redis
    depends_on:
      - mysql
      - redis
    networks:
      - chatbot-network

  web2:
    build: .
    container_name: chatbot-web-2
    ports:
      - "8502:8501"
    environment:
      - DB_HOST=mysql
      - REDIS_HOST=redis
    depends_on:
      - mysql
      - redis
    networks:
      - chatbot-network

  web3:
    build: .
    container_name: chatbot-web-3
    ports:
      - "8503:8501"
    environment:
      - DB_HOST=mysql
      - REDIS_HOST=redis
    depends_on:
      - mysql
      - redis
    networks:
      - chatbot-network

  # Load Balancer (nginx)
  nginx:
    image: nginx:latest
    container_name: chatbot-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl/:/etc/nginx/ssl/:ro
    depends_on:
      - web1
      - web2
      - web3
    networks:
      - chatbot-network

  # Cache distribuído
  redis:
    image: redis:7-alpine
    container_name: chatbot-redis
    ports:
      - "6379:6379"
    networks:
      - chatbot-network

  # Banco de dados
  mysql:
    image: mysql:8.0
    container_name: chatbot-mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASS}
      MYSQL_DATABASE: ${DB_NAME}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - chatbot-network

networks:
  chatbot-network:
    driver: bridge

volumes:
  mysql_data:
```

```nginx
# nginx.conf
upstream app {
    least_conn;
    server web1:8501;
    server web2:8501;
    server web3:8501;
}

server {
    listen 80;
    server_name chatbot.ifs.edu.br;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name chatbot.ifs.edu.br;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (Streamlit needs it)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Usar assim:
docker-compose up -d

# Verificar status:
docker-compose ps

# Visualizar logs:
docker-compose logs -f web1

# Scale para 5 instâncias:
docker-compose up -d --scale web=5
```

**Tempo:** 3-5 horas  
**Benefícios:**
- ✅ Múltiplas instâncias (load balanced)
- ✅ Sem ponto único de falha
- ✅ Fácil de escalar (docker-compose up scale)
- ✅ Isolamento de ambiente

---

## 🟡 PROBLEMAS MÉDIOS (P1-P2)

### P1.1: CACHE NÃO DISTRIBUÍDO

**Problema:** Se 3 instâncias, cada uma tem EntityCache diferente

**Solução:** Redis

```python
# Em tools.py, substituir cache em memória por Redis

import redis
from functools import wraps
import json

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

def search_entity_fuzzy_redis(search_term: str):
    """
    Busca fuzzy com Redis como backend
    """
    # Cache key
    cache_key = f"entity_fuzzy:{search_term.lower()}"
    
    # Tenta cache primeiro
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Se não em cache, faz busca (no-op para teste)
    results = _fuzzy_search_slow(search_term)
    
    # Salva em Redis por 1 hora
    redis_client.setex(cache_key, 3600, json.dumps(results, ensure_ascii=False))
    
    return results

# Função auxiliar para popular cache na inicialização
def populate_entity_cache():
    """Pré-carregar todas as entidades no Redis"""
    from db_connection import DBConnection
    
    db = DBConnection()
    
    # Carregar dim_favorecido
    favorecidos = db.execute_query("SELECT id_favorecido, nomeFavorecido FROM dim_favorecido")
    redis_client.setex("dim:favorecido", 86400, json.dumps(favorecidos))
    
    logger.info("✅ Entity cache populado no Redis")
```

**Tempo:** 1-2 horas  
**Benefícios:**
- ✅ Cache sincronizado entre instâncias
- ✅ TTL automático (invalidate)
- ✅ Escalável com múltiplos servidores

---

### P1.2: COBERTURA DO KNOWLEDGE BASE

**Problema:** Apenas 40% dos padrões de pergunta são cobertos

**Solução:** Expandir para 100+ exemplos

```python
# Em knowledge_base.py, adicionar 70+ novos exemplos

SQL_EXAMPLES = [
    # ========== GRUPO 1: TOTAIS (Simple) ==========
    {"question": "Quanto foi gasto com Energisa?",
     "sql": """SELECT SUM(valor) as total 
              FROM v_financas_geral 
              WHERE nomeFavorecido LIKE '%{0}%'"""},
    
    {"question": "Qual é o total em 2025?",
     "sql": """SELECT SUM(valor) as total 
              FROM v_financas_geral 
              WHERE YEAR(data_emissao) = {0}"""},
    
    # ========== GRUPO 2: RANKINGS (Aggregation) ==========
    {"question": "Quantos dos 5 maiores fornecedores?",
     "sql": """SELECT nomeFavorecido, SUM(valor) as total
              FROM v_financas_geral
              GROUP BY nomeFavorecido
              ORDER BY total DESC
              LIMIT 5"""},
    
    {"question": "Qual natureza teve mais gasto?",
     "sql": """SELECT desc_categoria, SUM(valor) as total
              FROM v_financas_geral
              GROUP BY desc_categoria
              ORDER BY total DESC
              LIMIT 3"""},
    
    # ========== GRUPO 3: FILTROS CRUZADOS (Complex) ==========
    {"question": "Quantos Energisa pagou em Aracaju ano passado?",
     "sql": """SELECT SUM(valor) as total
              FROM v_financas_geral
              WHERE nomeFavorecido LIKE '%Energisa%'
              AND ug LIKE '%Aracaju%'
              AND YEAR(data_emissao) = {0}"""},
    
    {"question": "Top 3 fornecedores da Reitoria em 2024?",
     "sql": """SELECT nomeFavorecido, SUM(valor) as total
              FROM v_financas_geral
              WHERE ug = 'Reitoria'
              AND YEAR(data_emissao) = 2024
              GROUP BY nomeFavorecido
              ORDER BY total DESC
              LIMIT 3"""},
    
    # ========== GRUPO 4: ANÁLISES TEMPORAIS ==========
    {"question": "Evolução de gastos mês por mês?",
     "sql": """SELECT DATE_FORMAT(data_emissao, '%Y-%m') as mes, SUM(valor) as total
              FROM v_financas_geral
              GROUP BY mes
              ORDER BY mes DESC"""},
    
    # ========== GRUPO 5: COMPARATIVAS ==========
    {"question": "Campus Aracaju gasta mais que Lagarto?",
     "sql": """SELECT ug, SUM(valor) as total
              FROM v_financas_geral
              WHERE ug IN ('Campus Aracaju', 'Campus Lagarto')
              GROUP BY ug"""},
    
    # ... 100+ total exemplos (ver arquivo completo)
]
```

**Tempo:** 3-4 horas  
**Benefícios:**
- ✅ Cobertura 100% dos padrões
- ✅ Menos erros de geração SQL
- ✅ Respostas mais rápidas (menos LLM)

---

### P1.3: SEM RASTREAMENTO MULTI-TURN

**Problema:**
```
User: "Energisa 2025?"
Bot: "R$ 1.5M"

User: "E em Aracaju?"  ← Context perdido
Bot: ❌ "Aracaju O quê?"
```

**Solução:** Passar histórico ao Data Detective

```python
# Em app_v2.py, manter history e passar para agente

def get_crew_response_multiturno(pergunta_atual: str, historico: list):
    """
    Pergunta com contexto de histórico
    """
    
    # Criar mensagem de sistema com contexto
    context_msg = ""
    if historico:
        context_msg = "Histórico da conversa:\n"
        for i, msg in enumerate(historico[-3:]):  # Últimas 3 turns
            context_msg += f"\n{i+1}. User: {msg['pergunta']}\n   Bot: {msg['resposta'][:100]}...\n"
        
        context_msg += f"\nAgora o usuário pergunta: \"{pergunta_atual}\"\n"
        context_msg += "Use o histórico para inferir contexto (ex: se perguntou sobre Energisa, " \
                      "\"E em Aracaju?\" significa \"Energisa em Aracaju?\")"
    
    crew = IFSCrew()
    full_prompt = context_msg + "\n" + pergunta_atual
    
    result = crew.get_crew(full_prompt).kickoff()
    
    # Guardar em histórico
    historico.append({
        "timestamp": datetime.now(),
        "pergunta": pergunta_atual,
        "resposta": result
    })
    
    return result
```

**Tempo:** 1-2 horas  
**Benefícios:**
- ✅ Conversação natural
- ✅ Follow-ups sem repetir contexto
- ✅ UX muito melhor

---

## 📊 ROADMAP DE IMPLEMENTAÇÃO

### Semana 1: P0s Críticos

```
SEGUNDA:
├─ P0.1: GitHub Actions ETL automático (1.5h)
├─ P0.2: Audit logging table + implementation (2h)
└─ TESTE: Validar ambos rodam sem erro

TERÇA:
├─ P0.3: Confidence score + metadata (2h)
├─ P0.4: Docker setup básico (2h)
└─ TESTE: Imagem Docker roda, app accessibility OK

QUARTA:
├─ P0.4: Nginx + load balancer (2h)
├─ Testes de load (multiple simultaneous users)
└─ PRODUÇÃO: Deploy em staging

QUINTA:
├─ P1.1: Redis caching (1.5h)
├─ P1.3: Multi-turn history (1h)
└─ TESTE: Validar performance

SEXTA:
├─ P1.2: Expandir knowledge base (2h)
├─ Smoke tests e2e
└─ PREPARAR: Go-live em produção
```

**Total Semana 1:** ~16-18 horas
**Resultado:** Score 9.0/10

---

## 🎯 CHECKLIST DE IMPLEMENTAÇÃO

### P0s
```
[ ] GitHub Actions workflow criado
[ ] ETL roda automaticamente todo dia
[ ] chat_audit_log tabela criada
[ ] Logging implementado em todos pontos críticos
[ ] Confidence scores integrados no agente
[ ] Response metadata formatado em PT-BR
[ ] Docker setup completo
[ ] Nginx load balancer configurado
[ ] 3 instâncias rodando
[ ] Health check implementado

Score esperado: 9.0/10
```

### P1s
```
[ ] Redis integrado (cache distribuído)
[ ] Knowledge base expandido (100+ exemplos)
[ ] Multi-turn conversation histórico
[ ] Smoke tests e2e passando
[ ] Performance <5s por pergunta

Score esperado: 9.2/10
```

### P2s (Optional, long-term)
```
[ ] MySQL replication (High Availability)
[ ] Kubernetes deployment
[ ] Prometheus monitoring
[ ] Alertas automáticos (Slack/Email)
[ ] Fine-tuning do modelo LLM

Score esperado: 9.5+/10
```

---

## 💼 ESTIMATIVA DE RECURSOS

| Item | Horas | Pessoa | Duração |
|------|-------|--------|---------|
| P0.1 (ETL Auto) | 2h | Dev 1 | Segunda |
| P0.2 (Audit Log) | 3h | Dev 1 | Seg-Ter |
| P0.3 (Confidence) | 2.5h | Dev 2 | Ter-Qua |
| P0.4 (Docker) | 3.5h | DevOps | Ter-Qua |
| P1.1 (Redis) | 1.5h | Dev 1 | Qui |
| P1.2 (KB Expand) | 3h | Dev 2 | Qui-Sex |
| P1.3 (Multi-turn) | 1.5h | Dev 1 | Qui |
| Testes/Deploy | 3h | DevOps | Sex |
| **TOTAL** | **20h** | **2-3 people** | **1 semana** |

---

## 🚀 PRÓXIMO PASSO

**Ação Imediata:**
```bash
# 1. Criar branch de feature
git checkout -b feature/architecture-improvements

# 2. Começar com P0.1 (ETL automático)
# Criar .github/workflows/etl-daily.yml

# 3. Executar completo

# 4. Merge + deploy

# 5. Validar em staging por 24h

# 6. Go-live em produção
```

---

**Roadmap Criado:** 24/03/2026  
**Score Atual:** 7.6/10  
**Score Meta:** 9.2/10  
**Tempo Estimado:** 20 horas (1 semana com 2-3 devs)  
**Status:** Pronto para iniciar implementação
