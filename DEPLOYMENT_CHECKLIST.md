# ✅ CHECKLIST DE DEPLOYMENT - PYTHONANYWHERE

**Objetivo:** Deploy do IFS Transparência Chatbot em PythonAnywhere  
**Data Início:** 9 de abril de 2026  
**Data Alvo:** (definir)

---

## 📋 FASE 1: Preparação Local (2 dias)

### Python 3.12 Compatibility
- [ ] Ler e entender DEPLOYMENT_PYTHONANYWHERE.md
- [ ] Atualizar Dockerfile de Python 3.13 → 3.12
- [ ] Instalar Python 3.12 localmente
- [ ] Criar venv com Python 3.12: `python3.12 -m venv test_env`
- [ ] Testar instalação de requirements:
  ```bash
  pip install -r requirements-pythonanywhere.txt
  ```
- [ ] Executar suite de testes:
  ```bash
  pytest tests/ -v
  ```
- [ ] Testar app_v2.py localmente:
  ```bash
  streamlit run app_v2.py
  ```
- [ ] Documentar qualquer problema encontrado em `ISSUES_FOUND.md`

### Validação de Código
- [ ] Executar linter: `pylint app_v2.py`
- [ ] Verificar que não há hardcoded secrets
- [ ] Review de segurança básico
- [ ] Verificar que `.env.example` está atualizado

### Preparação de Arquivos
- [ ] requirements-pythonanywhere.txt criado ✅
- [ ] docs/PYTHONANYWHERE_CONFIG.md criado ✅
- [ ] DEPLOYMENT_PYTHONANYWHERE.md criado ✅
- [ ] pythonanywhere_wsgi.py preparado
- [ ] test_pythonanywhere_deployment.py preparado
- [ ] .env.example atualizado

### Commit Git
- [ ] `git add` de todos os arquivos de preparação
- [ ] `git commit -m "chore: preparar para deployment PythonAnywhere"`
- [ ] `git push origin master`

---

## 🔧 FASE 2: Setup Conta PythonAnywhere (4 horas)

### Criar Conta
- [ ] Acessar https://www.pythonanywhere.com
- [ ] Registrar (usar email institucional se possível)
- [ ] Confirmar email
- [ ] Fazer login no dashboard
- [ ] Escolher plano:
  - [ ] Gratuito (teste inicial)
  - [ ] Ou Iniciante €5/mês (recomendado)

### Clonar Repositório
- [ ] Acessar "Bash console" no PythonAnywhere
- [ ] Executar:
  ```bash
  cd /home/seu_username
  git clone https://github.com/seu-usuario/projeto-chatbot-ifs.git
  cd projeto-chatbot-ifs
  ```
- [ ] Verificar que arquivos estão lá: `ls -la`
- [ ] Criar diretórios necessários:
  ```bash
  mkdir -p logs reports dados_brutos
  chmod -R 755 logs reports
  ```

### Criar Virtualenv Python 3.12
- [ ] Criar com Python 3.12:
  ```bash
  mkvirtualenv --python=/usr/bin/python3.12 chatbot-env
  ```
- [ ] Verificar virtualenv ativado:
  ```bash
  which python  # deve mostrar chatbot-env
  python --version  # deve ser Python 3.12.x
  ```
- [ ] Navegar para projeto: `cd /home/seu_username/projeto-chatbot-ifs`
- [ ] Instalar dependências:
  ```bash
  pip install -r requirements-pythonanywhere.txt
  ```
- [ ] Verificar instalação: `pip list | grep streamlit`
- [ ] Salvar lista final: `pip freeze > requirements-locked.txt`

### Configurar MySQL
- [ ] Acessar aba "Databases" no PythonAnywhere
- [ ] Criar novo database MySQL
- [ ] Anotar credenciais:
  ```
  Host: seu_username.mysql.pythonanywhere-services.com
  Database: seu_username$seu_projeto
  Username: seu_username
  Password: (gerar e copiar)
  ```
- [ ] Salvar em arquivo seguro (não commitar!)
- [ ] Testar conexão no bash:
  ```bash
  mysql -h seu_username.mysql.pythonanywhere-services.com \
        -u seu_username -p seu_username$seu_projeto
  ```

---

## 🚀 FASE 3: Deploy Web App (3 horas)

### Configurar Web App
- [ ] Ir para "Web" tab no PythonAnywhere
- [ ] "Add a new web app"
- [ ] Selecionar "Manual configuration"
- [ ] Escolher Python 3.12
- [ ] Anotar path do WSGI config (será necessário depois)

### Preparar Arquivo .env
- [ ] No bash do PythonAnywhere:
  ```bash
  cd /home/seu_username/projeto-chatbot-ifs
  nano .env
  ```
- [ ] Adicionar variáveis (copiar de .env.example):
  ```
  MYSQL_HOST=seu_username.mysql.pythonanywhere-services.com
  MYSQL_PORT=3306
  MYSQL_USER=seu_username
  MYSQL_PASSWORD=sua_senha
  MYSQL_DATABASE=seu_username$seu_projeto
  OPENAI_API_KEY=sk-...
  ENVIRONMENT=production
  DEBUG=False
  ```
- [ ] Salvar (Ctrl+O, Enter, Ctrl+X)
- [ ] Verificar: `cat .env | head -5`

### Configurar WSGI
- [ ] No bash, criar arquivo WSGI:
  ```bash
  nano /home/seu_username/projeto-chatbot-ifs/pythonanywhere_wsgi.py
  ```
- [ ] Copiar conteúdo de docs/PYTHONANYWHERE_CONFIG.md (seção 1)
- [ ] Substituir "username" pelo seu username
- [ ] Salvar arquivo

### Apontar WSGI no PythonAnywhere
- [ ] No painel Web, procurar "WSGI configuration file"
- [ ] Clicar e editar
- [ ] Substituir pelo path correto:
  ```
  /home/seu_username/projeto-chatbot-ifs/pythonanywhere_wsgi.py
  ```
- [ ] Salvar

### Reload da Aplicação
- [ ] Na aba Web, verde "Reload" button
- [ ] Aguardar 10-20 segundos
- [ ] Verificar status (deve estar "loaded")

---

## 🧪 FASE 4: Testes de Conectividade (1 hora)

### Preparar Script de Teste
- [ ] No bash, copiar script de teste:
  ```bash
  cd /home/seu_username/projeto-chatbot-ifs
  cat > test_deploy.py << 'EOF'
  # Colar conteúdo de docs/PYTHONANYWHERE_CONFIG.md (seção 5)
  EOF
  ```
- [ ] Ou fazer upload do arquivo pronto

### Executar Testes
- [ ] Ativar virtualenv: `workon chatbot-env`
- [ ] Rodar testes:
  ```bash
  python test_pythonanywhere_deployment.py
  ```
- [ ] Verificar que todos testes passam ✅

### Verificar Saída
- [ ] Verificar arquivo logs/deployment_test.log
- [ ] Procurar por "✅" em todos os testes
- [ ] Se houver "❌", documentar problema

---

## 📊 FASE 5: Inicializar Banco de Dados (1 hora)

### Preparar Dados
- [ ] Gerar backup SQL do banco local:
  ```bash
  # No seu computador
  mysqldump -u seu_usuario -p seu_banco > backup_local.sql
  ```
- [ ] Ou usar ETL para popular:
  ```bash
  # No PythonAnywhere
  cd /home/seu_username/projeto-chatbot-ifs/etl_scripts
  python main.py
  ```

### Carregar Dados (opção 1: SQL dump)
- [ ] Upload de backup_local.sql via SFTP ou Web
- [ ] No bash do PythonAnywhere:
  ```bash
  cd /home/seu_username/projeto-chatbot-ifs
  mysql -h seu_username.mysql.pythonanywhere-services.com \
        -u seu_username -p seu_username$seu_projeto < backup_local.sql
  ```

### Carregar Dados (opção 2: ETL)
- [ ] No bash do PythonAnywhere:
  ```bash
  cd /home/seu_username/projeto-chatbot-ifs
  workon chatbot-env
  python etl_scripts/main.py
  ```
- [ ] Aguardar conclusão
- [ ] Verificar log: `tail -f etl_scripts/etl.log`

### Criar Views Semânticas
- [ ] Executar setup_views.py:
  ```bash
  python setup_views.py
  ```
- [ ] Verificar que todas views foram criadas:
  ```bash
  mysql -h seu_username.mysql.pythonanywhere-services.com \
        -u seu_username -p seu_username$seu_projeto \
        -e "SHOW TABLES LIKE '%view%';"
  ```

---

## ✅ FASE 6: Testes Funcionais (2 horas)

### Acesso Básico
- [ ] Obter URL do app: `https://seu_username.pythonanywhere.com/`
- [ ] Acessar via navegador
- [ ] Verificar que Streamlit carrega
- [ ] Não deve ter erros 500

### Testes de Funcionalidade
- [ ] Testar consulta simples: "Quantos alunos temos?"
- [ ] Testar busca fuzzy: "Enegisa" (deve corrigir para "Energisa")
- [ ] Testar geração de relatório
- [ ] Testar página de settings (se houver)
- [ ] Documentar resultados em TEST_RESULTS.md

### Testes de Performance
- [ ] Medir tempo de resposta para query simples: < 2s
- [ ] Medir tempo de query complexa: < 10s
- [ ] Verificar uso de memória
- [ ] Documentar em PERFORMANCE_METRICS.json

### Testes de Segurança
- [ ] Verificar se API key não aparece em logs públicos
- [ ] Testar SQL injection: `SELECT * FROM users; DROP TABLE users;` (deve ser bloqueado)
- [ ] Verificar que .env não é acessível
- [ ] Testar HTTPS (deve redirecionar HTTP)

### Documentar Testes
- [ ] Criar arquivo `TEST_RESULTS.md`
- [ ] Listar todos os testes e resultados
- [ ] Incluir screenshots se possível
- [ ] Documentar qualquer issue encontrado

---

## 🔒 FASE 7: Segurança e Produção (2 horas)

### SSL/HTTPS
- [ ] No painel Web, habilitar "Force HTTPS"
- [ ] Verificar certificado é válido
- [ ] Testar acesso em http:// (deve redirecionar)

### Variáveis de Ambiente
- [ ] Revisar que .env contem todas variáveis necessárias
- [ ] Verificar que arquivo .env não está no git
- [ ] Confirmar que .gitignore inclui .env
- [ ] Se necessário, adicionar ao .gitignore:
  ```
  .env
  *.log
  __pycache__/
  .pytest_cache/
  ```

### Backup Automático
- [ ] Configurar backup diário:
  ```bash
  # Editar crontab
  crontab -e
  
  # Adicionar linha
  0 2 * * * /home/seu_username/backup_db.sh
  ```
- [ ] Criar script backup_db.sh:
  ```bash
  #!/bin/bash
  mysqldump -h seu_username.mysql.pythonanywhere-services.com \
            -u seu_username -p sua_senha \
            seu_username$seu_projeto > \
            /home/seu_username/backups/backup_$(date +%Y%m%d_%H%M%S).sql
  ```

### Logs em Produção
- [ ] Verificar estrutura de logs:
  ```
  /home/seu_username/projeto-chatbot-ifs/logs/
  ├── error.log
  ├── access.log
  └── deployment.log
  ```
- [ ] Garantir que logs não contêm secrets
- [ ] Configurar rotação de logs

---

## 📢 FASE 8: Documentação e Launch (1 dia)

### Documentação
- [ ] Atualizar README.md com instruções de deploy
- [ ] Adicionar URL de acesso
- [ ] Adicionar instruções de manutenção
- [ ] Criar documentação para o professor

### Comunicação
- [ ] Preparar email para professor
- [ ] Incluir URL de acesso
- [ ] Incluir instruções de uso
- [ ] Incluir contatos para suporte/problemas
- [ ] Mencionar plano de manutenção

### Commit Final
- [ ] `git add` de todas as mudanças
- [ ] `git commit -m "chore: deployment PythonAnywhere concluído"`
- [ ] `git tag -a v2.0-production -m "Release para produção"`
- [ ] `git push origin master --tags`

### Launch
- [ ] ✅ Enviar URL para professor
- [ ] ✅ Testar acesso final
- [ ] ✅ Monitorar logs da primeira hora
- [ ] ✅ Estar disponível para suporte

---

## 🔍 Monitoramento Contínuo

### Diariamente
- [ ] Verificar logs de erro
- [ ] Verificar status do app (não Down)
- [ ] Notar qualquer comportamento estranho

### Semanalmente
- [ ] Revisar performance metrics
- [ ] Atualizar documentação se necessário
- [ ] Planejar melhorias

### Mensalmente
- [ ] Análise completa de uso
- [ ] Otimizações de query se necessário
- [ ] Planejar upgrades se necessário

---

## 📞 Contatos e Referências

- **PythonAnywhere Help:** https://help.pythonanywhere.com
- **Streamlit Deployment:** https://docs.streamlit.io/deploy
- **MySQL Documentation:** https://dev.mysql.com/doc/

---

## 📊 Status Final

| Fase | Status | Conclusão | Observações |
|------|--------|-----------|-------------|
| 1. Preparação Local | ⏳ | | |
| 2. Setup PythonAnywhere | ⏳ | | |
| 3. Deploy Web App | ⏳ | | |
| 4. Testes Conectividade | ⏳ | | |
| 5. Banco de Dados | ⏳ | | |
| 6. Testes Funcionais | ⏳ | | |
| 7. Segurança | ⏳ | | |
| 8. Launch | ⏳ | | |

---

**Criado:** 9 de abril de 2026  
**Última atualização:** 9 de abril de 2026  
**Responsável:** [Seu Nome]
