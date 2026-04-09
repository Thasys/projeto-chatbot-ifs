# GUIA PRÁTICO - TESTE DO SISTEMA CHATBOT IFS

**Versão:** 1.0  
**Data:** 9 de abril de 2026  
**Status:** ✅ Pronto para teste

---

## 📋 SUMÁRIO

Este guia fornece um **passo a passo completo** para testar o sistema do chatbot IFS, incluindo as 5 perguntas recomendadas e como executar os testes.

---

## 🚀 PASSO 1: Preparação do Ambiente

### 1.1 Abrir Terminal PowerShell
```powershell
# Abrir PowerShell no diretório do projeto
cd "c:\Users\thars\Documents\THARSYS\ESTUDOS\Chatbot - IFS\04\projeto-chatbot-ifs"
```

### 1.2 Verificar Python
```powershell
# Confirmar que Python está disponível
python --version
# Esperado: Python 3.13.x ou superior
```

### 1.3 Verificar Dependências
```powershell
# Verificar se Streamlit está instalado
python -c "import streamlit; print('Streamlit OK')"

# Verificar se CrewAI está instalado
python -c "from crewai import Agent; print('CrewAI OK')"
```

---

## 🧪 PASSO 2: Teste Automático (Recomendado)

### 2.1 Executar Teste de 5 Perguntas
```powershell
# Rodar teste automático com timeout de 10 minutos
python test_simples.py 2>&1
```

**Esperado:**
```
RESULTADO V1: 5 OK, 0 ERROS
RESULTADO V2: 5 OK, 0 ERROS
```

### 2.2 Interpretar Resultados
- ✅ Se ver "5 OK, 0 ERROS" em ambas as versões = **Sistema OK**
- ❌ Se ver "ERROS" = Há problema de conexão ou configuração

---

## 💬 PASSO 3: Teste Manual Interativo

### 3.1 Iniciar APP_V2.PY (Recomendado)
```powershell
# Iniciar a interface Streamlit com app_v2.py
streamlit run app_v2.py
```

**O que Esperar:**
- Navegador abre automaticamente em `http://localhost:8501`
- Apareça interface com chat box
- Sidebar com histórico de mensagens

### 3.2 Ou Iniciar APP.PY (Versão Simples)
```powershell
# Alternativa com versão mais simples
streamlit run app.py
```

---

## 📝 PASSO 4: Fazer as Perguntas de Teste

### Pergunta 1: Total de Gastos em 2024
```
Digite na caixa de chat:
"Qual o total de gastos do IFS em 2024?"

Esperado:
- Resposta com valor total em reais
- Confidence score: 85-95% (no app_v2.py)
- Tempo: 8-15 segundos
```

### Pergunta 2: Top 5 Fornecedores
```
Digite na caixa de chat:
"Quais foram os 5 maiores fornecedores do IFS em 2024?"

Esperado:
- Lista de 5 fornecedores com valores
- Exemplos: Banco do Brasil, Caixa Econômica, Energisa
- Confidence score: 90-95% (no app_v2.py)
- Tempo: 10-18 segundos
```

### Pergunta 3: Gasto com Fornecedor Específico
```
Digite na caixa de chat:
"Quanto o IFS gastou com a Energisa em 2024?"

Esperado:
- Valor total gasto com Energisa
- Pode retornar zero se não houver dados
- Confidence score: 80-90% (no app_v2.py)
- Tempo: 8-12 segundos
```

### Pergunta 4: Filtro por Campus e Mês
```
Digite na caixa de chat:
"Qual foi o gasto total do Campus de Propriá em janeiro de 2024?"

Esperado:
- Valor total para Campus specific em período específico
- Pode retornar zero se não houver dados
- Confidence score: 75-85% (no app_v2.py)
- Tempo: 10-15 segundos
```

### Pergunta 5: Filtro por Tipo de Despesa
```
Digite na caixa de chat:
"Quais foram as maiores despesas com diárias em 2024?"

Esperado:
- Lista de pesoas/departamentos com maiores gastos em diárias
- Confidence score: 90-95% (no app_v2.py)
- Tempo: 12-20 segundos
```

---

## ✅ PASSO 5: Validar Resultados

### 5.1 Checklist para APP.PY
- ✅ Resposta contém dados numéricos reais
- ✅ Formatação em português claro
- ✅ Sem erros ou exceções
- ✅ Tempo de resposta < 30 segundos
- ⚠️ Sem confidence score
- ⚠️ Sem auditoria

### 5.2 Checklist para APP_V2.PY (RECOMENDADO)
- ✅ Resposta contém dados numéricos reais
- ✅ Formatação em português claro
- ✅ Confidence score visível (ex: 92%)
- ✅ Período de dados exibido
- ✅ Sem erros ou exceções
- ✅ Tempo de resposta < 30 segundos
- ✅ Auditoria registrada (ver no banco de dados)

---

## 🐛 PASSO 6: Diagnosticar Problemas

### 6.1 Se Ver Erro "Connection Refused"
```
Problema: Banco de dados não está acessível

Solução:
1. Verificar arquivo .env:
   cat .env
   
2. Confirmar as credenciais do MySQL:
   DATABASE_URL=mysql://user:password@host/db
   
3. Testar conexão:
   python -c "from db_connection import DBConnection; db = DBConnection().get_engine(); print('OK')"
```

### 6.2 Se Ver Erro "No module named 'crewai'"
```
Problema: Dependências não instaladas

Solução:
pip install -r requirements.txt
```

### 6.3 Se Ver Erro de Validação Pydantic
```
Problema: Decorador duplicado na função (JÁ CORRIGIDO)

Solução (caso retorne):
1. Verificar tools.py linha 150
2. Garantir que @tool() aparece apenas 1 vez por função
```

### 6.4 Se Resposta Ficar Vazia
```
Problema: Query SQL retornou zero linhas

Solução:
1. Pergunta pode ser muito específica
2. Dados podem não existir no período
3. Tente pergunta mais genérica
```

---

## 📊 PASSO 7: Comparar Resultados

| Aspecto | APP.PY | APP_V2.PY |
|---------|--------|-----------|
| **Funcionalidade** | ✅ OK | ✅ OK |
| **Velocidade** | Rápido | Normal |
| **Confidence Score** | ❌ Não | ✅ Sim |
| **Auditoria** | ❌ Não | ✅ Sim |
| **Cache** | ❌ Não | ✅ Sim (TTL=300s) |
| **Rate Limiting** | ❌ Não | ✅ Sim |
| **Recomendado** | Desenvolvimento | **Produção** |

---

## 🎯 PASSO 8: Teste de Carga (Opcional)

### 8.1 Executar Multiple Queries Sequencialmente
```powershell
# Script para teste de múltiplas perguntas
for ($i = 1; $i -le 5; $i++) {
    Write-Host "Iteracao $i..."
    python test_simples.py | grep "RESULTADO"
    Start-Sleep -Seconds 2
}
```

### 8.2 Monitorar Performance
```powershell
# Em outro terminal, monitorar uso de recursos
Get-Process python | Select ProcessName, CPU, WorkingSet | Format-Table

# Ou monitorar banco de dados
# SHOW PROCESSLIST; -- no MySQL
```

---

## 📈 PASSO 9: Validar Auditoria (APP_V2.PY Only)

### 9.1 Conectar ao Banco de Dados
```bash
# Abrir MySQL Client
mysql -u seu_usuario -p seu_password seu_database

# Ver registros de auditoria
SELECT pergunta, resposta, confidence, status, created_at 
FROM chat_audit_log 
ORDER BY created_at DESC 
LIMIT 10;
```

### 9.2 Verificar Estrutura de Auditoria
```sql
-- Deve conter:
-- 1. pergunta (string com a pergunta do usuário)
-- 2. resposta (resposta do sistema)
-- 3. confidence (score 0-100)
-- 4. status (SUCCESS ou ERROR)
-- 5. created_at (timestamp)
-- 6. tempo_ms (tempo em milissegundos)
-- 7. user_ip (IP do usuário)
```

---

## ✨ PASSO 10: Conclusão

### 10.1 Se Tudo Passou
```
✅ Sistema está PRONTO PARA PRODUÇÃO

Próximas ações:
1. Deploy do app_v2.py em servidor
2. Configurar SSL/HTTPS
3. Conectar a domínio
4. Configurar monitoramento
```

### 10.2 Se Encontrou Problemas
```
❌ Precisa de correções

Próximas ações:
1. Verificar .env
2. Validar conexão MySQL
3. Rodar test_simples.py novamente
4. Verificar logs de erro
```

---

## 📞 SUPORTE

Se encontrar problemas:

1. **Verificar Logs**
   ```powershell
   # Ver últimas linhas do log
   Get-Content -Path *.log -Tail 50
   ```

2. **Testar Conectividade MySQL**
   ```powershell
   python -c "from db_connection import DBConnection; print('Conexao OK')"
   ```

3. **Validar Syntax Python**
   ```powershell
   python -m py_compile app.py app_v2.py tools.py
   ```

---

## 📋 RESUMO DE TESTES

**Forma 1: Teste Automático (Recomendado para começar)**
```powershell
python test_simples.py
# Duração: 5-15 minutos
# Testa 5 perguntas em ambos os apps
```

**Forma 2: Teste Manual (Para análise detalhada)**
```powershell
streamlit run app_v2.py
# Duração: Indefinida (você controla)
# Digita perguntas e analisa respostas
```

**Forma 3: Teste Via Script**
```powershell
python test_5_perguntas.py
# Duração: 15-25 minutos
# Teste mais detalhado com mais logging
```

---

## 🎓 DICAS IMPORTANTES

### ✅ Faça
- ✅ Teste as 5 perguntas base primeiro
- ✅ Use app_v2.py para produção
- ✅ Verifique confidence scores
- ✅ Monitore tempo de resposta
- ✅ Revise logs de erro

### ❌ Não Faça
- ❌ Não modifique o banco de dados durante testes
- ❌ Não use app.py com dados críticos
- ❌ Não ignre avisos de confidence baixo
- ❌ Não deixe cache muito alto (>600s)

---

**Versão 1.0 - Pronto para Uso**  
**Last Updated:** 9 de abril de 2026
