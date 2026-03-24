# 🚀 SETUP GITHUB ACTIONS - ETL AUTOMÁTICO

**Data:** 24 de Março de 2026  
**Objetivo:** Configurar automação de coleta de dados  

---

## 📋 PRÉ-REQUISITOS

✅ Seu projeto está em um repositório GitHub (já validado)  
✅ Você tem acesso de admin ao repositório  
✅ Python dependencies estão em `requirements.txt`  

---

## 🔧 PASSO A PASSO DE CONFIGURAÇÃO

### PASSO 1: Adicionar Secrets ao GitHub

Os secrets são variáveis confidenciais armazenadas de forma segura no GitHub.

**Ir para:** https://github.com/seu-usuario/seu-repo/settings/secrets/actions

Ou pelo GitHub Desktop/CLI:

```bash
gh secret set DB_HOST --body "localhost"
gh secret set DB_PORT --body "3306"
gh secret set DB_NAME --body "ifs_database"
gh secret set DB_USER --body "seu_usuario"
gh secret set DB_PASS --body "sua_senha_segura"
gh secret set API_KEY --body "sua_api_key_ifs"
```

**Secrets Obrigatórios:**
```
DB_HOST          (exemplo: localhost ou servidor remoto)
DB_PORT          (padrão: 3306)
DB_NAME          (nome do banco de dados)
DB_USER          (usuário MySQL)
DB_PASS          (senha MySQL)
API_KEY          (chave API do Portal da Transparência)
```

**Secret Opcional (Slack):**
```
SLACK_WEBHOOK_URL (para notificações, deixar em branco para ignorar)
```

---

### PASSO 2: Testar com Disparo Manual

1. Ir para: **Actions** → **Daily ETL Pipeline - IFS Transparência**
2. Clicar em: **Run workflow** → **Run workflow**
3. Esperar conclusão (~5-10 minutos)

**Resultado esperado:**
```
✅ All jobs succeeded
```

**Se falhar:**
```
❌ Falha - Ver logs detalhados na aba "Logs"
```

---

### PASSO 3: Validar Agendamento Automático

O workflow roda **automaticamente todo dia às 23:00 UTC (20:00 BRT)**.

**Onde ver próximas execuções:**
- **Tab:** Actions → Daily ETL Pipeline
- **Schedule:** Mostra última execução e próxima

---

## 📊 O QUE O WORKFLOW FAZ

```
┌─────────────────────────────────────┐
│  1. VALIDAÇÃO (2 min)               │
│  └─ Verifica Python, dependências   │
│                                     │
├─────────────────────────────────────┤
│  2. VALIDAÇÃO DE CREDENCIAIS (1 min)│
│  └─ Garante secrets existem         │
│                                     │
├─────────────────────────────────────┤
│  3. EXECUÇÃO ETL (3-5 min)         │
│  └─ Coleta dados, transforma, carrega
│                                     │
├─────────────────────────────────────┤
│  4. VALIDAÇÃO BD (1 min)            │
│  └─ Verifica integridade dos dados  │
│                                     │
├─────────────────────────────────────┤
│  5. NOTIFICAÇÕES (0 min)            │
│  └─ Slack/Email se configurado      │
│                                     │
├─────────────────────────────────────┤
│  6. DOCUMENTAÇÃO (0 min)            │
│  └─ Salva logs como artifacts       │
│                                     │
└─────────────────────────────────────┘

⏱️ TEMPO TOTAL: ~10-15 minutos
```

---

## 📈 MONITORAR EXECUÇÕES

### Via GitHub UI
```
1. Ir para: GitHub.com → Seu Repo
2. Clicar em: Actions
3. Selecionar: "Daily ETL Pipeline - IFS Transparência"
4. Ver histórico de execuções
```

### Via GitHub CLI
```bash
# Ver status da última execução
gh run list --workflow="etl-daily.yml" --limit=5

# Ver logs detalhados de uma execução
gh run view <RUN_ID> --log

# Redirecionar output para arquivo
gh run view <RUN_ID> --log > etl_execution.log
```

### Via Git Local
```bash
# Puxar logs commitados
git pull
cat etl_logs.log

# Ver histórico de commits do ETL
git log --grep="AUTO.*ETL" --oneline
```

---

## 🛠️ CUSTOMIZAÇÕES

### Alterar Horário de Execução

**Em `.github/workflows/etl-daily.yml`:**

```yaml
on:
  schedule:
    - cron: '0 23 * * *'  # ← Editar aqui
```

**Exemplos de horários:**
```
'0 23 * * *'   = 23:00 UTC (20:00 BRT) ← PADRÃO
'0 1 * * *'    = 01:00 UTC (22:00 BRT anterior)
'0 12 * * mon' = 12:00 seg, qua, sex
'*/6 * * * *'  = A cada 6 horas
'0 3 * * *'    = 03:00 UTC (00:00 BRT)
```

**Após alterar:**
```bash
git add .github/workflows/etl-daily.yml
git commit -m "🔄 Alterar agendamento ETL para [novo horário]"
git push
```

---

### Adicionar Notificação ao Slack

1. **Criar Slack Webhook:**
   - Ir para: https://api.slack.com/apps
   - New App → From scratch
   - Nome: "IFS Chatbot ETL"
   - Workspace: seu workspace
   - Features → Incoming Webhooks → On
   - Add New Webhook to Workspace
   - Copiar URL (exemplo: https://hooks.slack.com/services/T.../...)

2. **Adicionar Secret no GitHub:**
   ```bash
   gh secret set SLACK_WEBHOOK_URL --body "https://hooks.slack.com/services/..."
   ```

3. **Resultado:**
   - ✅ Mensagem direto no Slack quando ETL rodar
   - 🔔 Notificação se falhar

---

### Estender o Workflow

**Exemplo: Rodar testes após ETL**

```yaml
# Adicionar step após ETL
- name: 🧪 Run tests
  run: |
    pytest -m unit --tb=short
  continue-on-error: true
```

**Exemplo: Gerar relatório HTML**

```yaml
- name: 📊 Generate report
  run: |
    python etl_scripts/generate_report.py
    
- name: 📤 Upload report
  uses: actions/upload-artifact@v4
  with:
    name: etl-report-html
    path: reports/etl_report.html
```

---

## 🔍 TROUBLESHOOTING

### ❌ "Workflow file not found"
```
Solução: Verificar que arquivo está em:
.github/workflows/etl-daily.yml

NÃO em:
.github/etl-daily.yml
.workflows/etl-daily.yml
etl-daily.yml
```

---

### ❌ "Secrets have not been set"
```
Solução: 
1. Verificar se secrets foram adicionados
2. Nomes devem ser EXATAMENTE iguais em maiúsculas
3. Aguardar 1-2 minutos após adicionar
```

---

### ❌ "Database connection failed"
```
Solução:
1. Validar credenciais (DB_USER, DB_PASS, DB_HOST)
2. Verificar se BD está acessível de internet
   - Se BD é local/private, usar VPN ou SSH tunnel
3. Verificar firewall (porta 3306 aberta?)

Alternativa: Usar GitHub Runner self-hosted
```

---

### ❌ "Python dependencies not found"
```
Solução:
1. Verificar requirements.txt está no root
2. Checar se tem mysql-connector-python
   
   pip install mysql-connector-python
   pip freeze > requirements.txt
   git add requirements.txt
   git commit -m "Atualizar dependencies"
   git push
```

---

### ⚠️ "ETL roda mas dados não atualizam"
```
Verificar:
1. Log da execução → Actions → Ver detalhes
2. Contar registros no BD:
   
   SELECT COUNT(*) FROM fato_execucao
   WHERE data_emissao >= DATE_SUB(NOW(), INTERVAL 1 DAY)
   
3. Se tiver registros = dados foram carregados ✅
4. Se vazio = verificar query no etl_scripts/
```

---

## 📊 DASHBOARD DE EXECUÇÃO

**Para criar dashboard:**

1. Usar GitHub Actions API
```bash
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/seu-usuario/seu-repo/actions/runs
```

2. Visualmente no GitHub:
   - Actions → "Daily ETL Pipeline"
   - Mostra últimas 10 execuções
   - Status: ✅ ou ❌
   - Data/Hora: UTC
   - Duração: minutos

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

```
[ ] Secrets adicionados (6 obrigatórios)
[ ] Arquivo .github/workflows/etl-daily.yml criado
[ ] Primeiro teste manual realizado
[ ] Notificação Slack configurada (opcional)
[ ] Logs sendo salvos em artifacts
[ ] Agendamento 23:00 UTC validado
[ ] Documentação passada ao time
```

---

## 🎓 PRÓXIMAS TAREFAS

Após P0.1 estar funcionando (24h):

### P0.2: Audit Logging
```
Criar tabela chat_audit_log
Implementar logging em app_v2.py
```

### P0.3: Confidence Scores
```
Adicionar metadata nas respostas
Implementar no agente Public Analyst
```

### P0.4: Docker + Load Balancer
```
Criar Dockerfile
Setup docker-compose.yml
Configurar nginx
```

---

## 📞 SUPORTE

**Se tiver problemas:**

1. Verificar logs: https://github.com/seu-usuario/seu-repo/actions
2. Consultare docs GitHub Actions: https://docs.github.com/en/actions
3. Testar local: `python etl_scripts/main.py`

---

## 📈 MÉTRICAS DE SUCESSO

Após 1 semana de execução:
- ✅ 7 execuções bem-sucedidas
- ✅ Dados atualizados diariamente
- ✅ 0 falhas não reportadas
- ✅ Slack notificações funcionando
- ✅ Logs preservados

---

**Setup Concluído!**  
**Sua coleta de dados agora é automática!** 🎉
