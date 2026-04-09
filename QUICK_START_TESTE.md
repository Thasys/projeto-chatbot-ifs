# QUICK START - TESTE EM 5 MINUTOS

## ⚡ Início Rápido

### 1️⃣ Abra PowerShell
```powershell
cd "c:\Users\thars\Documents\THARSYS\ESTUDOS\Chatbot - IFS\04\projeto-chatbot-ifs"
```

### 2️⃣ Execute o Teste Automático
```powershell
python test_simples.py
```

### 3️⃣ Aguarde Resultado
Espere 5-10 minutos pelo resultado:
```
RESULTADO V1: 5 OK, 0 ERROS
RESULTADO V2: 5 OK, 0 ERROS
```

---

## 🎯 As 5 Perguntas de Teste

Copie e cole no chat quando iniciar o app:

### ✅ Pergunta 1
```
Qual o total de gastos do IFS em 2024?
```

### ✅ Pergunta 2
```
Quais foram os 5 maiores fornecedores do IFS em 2024?
```

### ✅ Pergunta 3
```
Quanto o IFS gastou com a Energisa em 2024?
```

### ✅ Pergunta 4
```
Qual foi o gasto total do Campus de Propriá em janeiro de 2024?
```

### ✅ Pergunta 5
```
Quais foram as maiores despesas com diárias em 2024?
```

---

## 🚀 Iniciar Aplicativo

**Escolha UMA opção:**

### Opção A: Recomendado (com Auditoria)
```powershell
streamlit run app_v2.py
```

### Opção B: Simples
```powershell
streamlit run app.py
```

---

## ✅ O que Procurar

| Verificar | APP.PY | APP_V2.PY |
|-----------|--------|-----------|
| Resposta com números | ✅ | ✅ |
| Em português claro | ✅ | ✅ |
| Confidence score | ❌ | ✅ 85-95% |
| Sem erros | ✅ | ✅ |
| <30 seg resposta | ✅ | ✅ |

---

## 🐛 Problema? Tente Isto:

| Erro | Solução |
|------|---------|
| "Connection refused" | Verificar .env com `cat .env` |
| "No module crewai" | `pip install crewai` |
| Resposta vazia | Pergunta muito específica, tente outra |
| Muito lento | Normal 1ª execução, cache depois |

---

**Tempo estimado: 5 minutos de teste automático + 10 min manual**
