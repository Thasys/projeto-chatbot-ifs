# 📋 Plano de Ação: Deploy em PythonAnywhere

**Objetivo:** Colocar o IFS Transparência Chatbot em produção no PythonAnywhere

**Data de Criação:** 9 de abril de 2026  
**Status:** 🚀 Planejamento Inicial

---

## 📊 Análise da Situação Atual

### ✅ Pontos Positivos
- ✓ Projeto bem estruturado com requirements.txt
- ✓ Dockerfile e docker-compose já preparados
- ✓ Código versionado no Git
- ✓ Arquivo .env.example disponível
- ✓ Banco de dados MySQL configurável
- ✓ Aplicação Streamlit pronta (app_v2.py)

### ⚠️ Desafios a Resolver
- ⚠️ PythonAnywhere tem Python limitado (3.10, 3.11, 3.12, não 3.13)
- ⚠️ Streamlit requer configuração especial em servidor compartilhado
- ⚠️ Conexão com banco de dados MySQL remoto
- ⚠️ Variáveis de ambiente sensíveis (API keys OpenAI, etc)
- ⚠️ Dependências nativas (gcc, g++) podem causar problemas
- ⚠️ Limites de recursos em plano gratuito

---

## 🎯 Plano de Ação em Fases

### **FASE 1: Preparação do Projeto (1-2 dias)**

#### 1.1 Verificar Compatibilidade
- [ ] Atualizar Dockerfile para Python 3.12 (em vez de 3.13)
- [ ] Executar testes com Python 3.12 localmente
- [ ] Validar que todas as dependências funcionam em Python 3.12
- [ ] Verificar se `mysql-connector-python` e outras libs nativas compilam

#### 1.2 Otimizar Dependências
- [ ] Revisar requirements.txt e remover dependências desnecessárias
- [ ] Testar com versions.txt congeladas para garantir compatibilidade
- [ ] Criar requirements-pythonanywhere.txt (sem dependências com compilação)
- [ ] Documentar versões específicas testadas

#### 1.3 Preparar Arquivo de Configuração
- [ ] Criar arquivo `.wsgi.py` para PythonAnywhere
- [ ] Criar arquivo `pythonanywhere_config.py` com todas as configs
- [ ] Documentar quais variáveis de ambiente são obrigatórias

**Entregáveis:**
```
- requirements-pythonanywhere.txt (atualizado)
- pythonanywhere_wsgi.py (novo)
- PYTHONANYWHERE_CONFIG.md (novo)
- Testes executados com Python 3.12
```

---

### **FASE 2: Configuração da Conta PythonAnywhere (2-3 horas)**

#### 2.1 Criar Conta
- [ ] Registrar em pythonanywhere.com
- [ ] Escolher plano adequado:
  - **Gratuito:** Limite 100MB, 1 app web, sem SSL
  - **Iniciante (€5/mês):** 512MB, 1 app, SSL
  - **Semi-Profissional (€7/mês):** 2GB, 2 apps, SSL

#### 2.2 Clonar Repositório
- [ ] Via SSH: `git clone` do repositório GitHub
- [ ] Ou upload de arquivos zip
- [ ] Estrutura: `/home/username/projeto-chatbot-ifs`

#### 2.3 Criar Ambiente Virtual
- [ ] Acessar bash console no PythonAnywhere
- [ ] Criar venv com Python 3.12:
  ```bash
  mkvirtualenv --python=/usr/bin/python3.12 chatbot-env
  ```
- [ ] Instalar dependências:
  ```bash
  pip install -r requirements-pythonanywhere.txt
  ```

#### 2.4 Configurar Banco de Dados MySQL
- [ ] Acessar painel "Databases" do PythonAnywhere
- [ ] Criar banco de dados MySQL
- [ ] Anotar credenciais:
  - Host: `username.mysql.pythonanywhere-services.com`
  - Port: `3306`
  - Database: `username$chatbot_db`
  - Username: `username`
  - Password: (gerado automaticamente)

**Entregáveis:**
```
- Conta PythonAnywhere criada
- Repositório clonado
- Virtualenv configurado
- Banco de dados MySQL criado
- Credenciais documentadas em arquivo seguro
```

---

### **FASE 3: Deploy da Aplicação (3-4 horas)**

#### 3.1 Configurar Web App
- [ ] No painel PythonAnywhere, criar novo Web App
- [ ] Selecionar "Manual configuration" + Python 3.12
- [ ] Pode ser Streamlit direto ou via WSGI

#### 3.2 Opção A - Deploy com Streamlit (Recomendado)
```bash
# No bash do PythonAnywhere
cd /home/username/projeto-chatbot-ifs
streamlit run app_v2.py --server.port=5000 \
  --server.address=0.0.0.0 \
  --server.headless=true
```

#### 3.3 Opção B - Deploy com WSGI + Nginx Reverso Proxy
- [ ] Criar arquivo `pythonanywhere_wsgi.py`
- [ ] Configurar como WSGI app no painel
- [ ] Nginx faz proxy para app Streamlit rodando internamente
- [ ] Mais complexo mas mais controlável

#### 3.4 Configurar Variáveis de Ambiente
- [ ] No painel "Web", adicionar variáveis:
  ```
  OPENAI_API_KEY=seu_api_key
  MYSQL_HOST=username.mysql.pythonanywhere-services.com
  MYSQL_USER=username
  MYSQL_PASSWORD=senha
  MYSQL_DATABASE=username$chatbot_db
  PYTHONUNBUFFERED=1
  ENVIRONMENT=production
  ```

#### 3.5 Testar Conectividade
- [ ] Script para testar conexão MySQL
- [ ] Script para testar API OpenAI
- [ ] Log inicial em `/home/username/projeto-chatbot-ifs/deploy_test.log`

**Entregáveis:**
```
- Web App configurado
- Variáveis de ambiente definidas
- Testes de conectividade: ✅ MySQL ✅ OpenAI
- deploy_test.log gerado
```

---

### **FASE 4: Inicialização de Banco de Dados (1 hora)**

#### 4.1 Transferir Dados
- [ ] Executar ETL scripts no servidor:
  ```bash
  cd /home/username/projeto-chatbot-ifs/etl_scripts
  python main.py
  ```
- Ou usar arquivo SQL dump:
  ```bash
  mysql --host=username.mysql.pythonanywhere-services.com \
        --user=username --password \
        username$chatbot_db < backup.sql
  ```

#### 4.2 Criar Views Semânticas
- [ ] Executar `setup_views.py`
- [ ] Verificar que todas as views foram criadas

#### 4.3 Validar Dados
- [ ] Testar queries de exemplo
- [ ] Verificar tabelas principais
- [ ] Log de validação em `db_validation.log`

**Entregáveis:**
```
- Banco de dados populado
- Views criadas e testadas
- db_validation.log com status ✅
```

---

### **FASE 5: Testes e Validação (2-3 horas)**

#### 5.1 Testes Funcionais
- [ ] Testar página de login/acesso
- [ ] Testar consultas simples em linguagem natural
- [ ] Testar fuzzy matching
- [ ] Testar geração de relatórios
- [ ] Testar pages do Streamlit (se houver)

#### 5.2 Testes de Performance
- [ ] Medir tempo de resposta para queries simples
- [ ] Medir tempo para queries complexas
- [ ] Verificar uso de memória
- [ ] Documentar limites encontrados

#### 5.3 Testes de Segurança
- [ ] Verificar que credenciais do banco não estão expostas
- [ ] Testar SQL injection (deve ser bloqueado)
- [ ] Verificar logs para ataques
- [ ] Habilitar SSL/HTTPS

#### 5.4 Monitoramento Inicial
- [ ] Configurar logs em `/home/username/projeto-chatbot-ifs/logs/`
- [ ] Monitore erro_log.py execução
- [ ] Acompanhar primeiras 24 horas de uso

**Entregáveis:**
```
- TEST_RESULTS.md com resultado de todos os testes
- PERFORMANCE_METRICS.json
- Aplicação acessível via HTTPS
- Logs funcionando normalmente
```

---

### **FASE 6: Monitoramento e Manutenção (Contínuo)**

#### 6.1 Monitoramento Diário
- [ ] Verificar logs de erro diariamente
- [ ] Monitorar uso de espaço em disco
- [ ] Verificar status do aplicativo

#### 6.2 Manutenção Semanal
- [ ] Revisar logs de performance
- [ ] Backup do banco de dados
- [ ] Atualizar dependências se necessário

#### 6.3 Manutenção Mensal
- [ ] Análise completa de performance
- [ ] Otimizações de queries
- [ ] Documentação de issues encontrados

---

## 📦 Matriz de Requisitos

| Requisito | Status | Notas |
|-----------|--------|-------|
| Conta PythonAnywhere | ⏳ Não iniciado | Criar conta gratuita ou paga |
| Python 3.12 | ⏳ Verificação | Atualizar Dockerfile para 3.12 |
| MySQL | ⏳ Não iniciado | PythonAnywhere fornece |
| Streamlit | ✅ Sim | Já configurado em app_v2.py |
| OpenAI API Key | ⏳ Não iniciado | Adicionar como variável de ambiente |
| Domínio customizado | ⏳ Opcional | pythonanywhere.com fornece domínio ou use próprio |
| SSL/HTTPS | ✅ Sim | PythonAnywhere fornece certificado |
| Backups | ⏳ Não iniciado | Automatizar backup semanal |

---

## 🔧 Checklist de Pre-Launch

### Antes de Colocar no Ar
- [ ] Todos os testes da FASE 5 passando
- [ ] Banco de dados com dados mais recentes
- [ ] Todas as variáveis de ambiente configuradas
- [ ] SSL/HTTPS ativado
- [ ] Logs configurados e testados
- [ ] Documentação atualizada para produção

### No Dia do Launch
- [ ] Último backup local realizado
- [ ] Notificar professor sobre disponibilização
- [ ] Teste final de acesso ao sistema
- [ ] Monitorar logs da primeira hora

### Após Launch (Primeiros 7 dias)
- [ ] Revisar logs diariamente
- [ ] Coletar feedback do professor
- [ ] Documentar issues encontrados
- [ ] Corrigir bugs críticos imediatamente

---

## 💰 Estimativa de Custos

| Serviço | Plano | Custo Mensal | Necessário? |
|---------|-------|--------------|------------|
| PythonAnywhere | Iniciante | €5 | Sim |
| OpenAI API | Pay-as-you-go | Variável | Sim (já tem) |
| Domínio customizado | Opcional | €8-12/ano | Não, usar PythonAnywhere |
| **Total Mensal** | | **~€5** | ✅ |

---

## 📖 Referências e Recursos

### Documentação
- [PythonAnywhere Docs](https://help.pythonanywhere.com)
- [Streamlit Deployment Guide](https://docs.streamlit.io/deploy)
- [CrewAI Documentation](https://docs.crewai.com)

### Tutoriais Importantes
- Deployment Streamlit em PythonAnywhere
- Configurar MySQL remoto
- Gerenciar variáveis de ambiente

### Contatos de Suporte
- PythonAnywhere Support: help@pythonanywhere.com
- GitHub Issues para bugs do projeto

---

## 🚨 Riscos e Mitigação

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|--------|-----------|
| Compatibilidade Python 3.12 | Média | Alto | Testar localmente antes |
| Limite de memória PythonAnywhere | Alta | Médio | Planejar upgrade de plano |
| Falha de conexão MySQL | Baixa | Alto | Implementar retry logic |
| API Key OpenAI exposta | Muito Baixa | Crítico | Usar variáveis de ambiente protegidas |
| Performance lenta | Média | Médio | Cache e otimizações de query |

---

## 📝 Próximos Passos

1. **Imediatamente:** Atualizar Dockerfile para Python 3.12
2. **Hoje:** Testar localmente com Python 3.12
3. **Amanhã:** Criar conta PythonAnywhere e clonar repositório
4. **Esta semana:** Completar FASES 1-3
5. **Próxima semana:** Completar FASES 4-5 e fazer deploy

**Estimativa Total:** 2-3 semanas para produção estável

---

**Preparado por:** GitHub Copilot  
**Versão:** 1.0  
**Última atualização:** 9 de abril de 2026
