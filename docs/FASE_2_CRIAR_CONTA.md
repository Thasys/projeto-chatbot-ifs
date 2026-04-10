# 📋 FASE 2: Criar Conta PythonAnywhere

**Data Início:** 9 de abril de 2026  
**Tempo Estimado:** 30 minutos  
**Status:** 🔄 EM PROGRESSO

---

## 📌 Objetivo

Registrar conta no PythonAnywhere e preparar ambiente para deployment

---

## ✅ Passo a Passo

### PASSO 1: Acessar PythonAnywhere

1. Abrir navegador (Chrome, Firefox, Edge)
2. Ir para: **https://www.pythonanywhere.com**
3. Você verá página inicial com "Get started"

---

### PASSO 2: Criar Conta

**Opção A: Registro Direto**
1. Clique em **"Try it now"** ou **"Sign up"** (canto superior direito)
2. Será levado para página de registro

**Na página de registro, preencher:**
```
Username: [seu_username_pythonanywhere]
Email: seu@email.com
Password: [senha_forte]
Confirm Password: [repetir_senha]
```

#### 💡 Dica de Username
- Use letras minúsculas e números
- Evite espaços e caracteres especiais
- Exemplo: `seu_username_2026` ou `tharsys_chatbot`
- **Este username será parte da sua URL: seu_username.pythonanywhere.com**

#### 🔐 Dica de Senha
- Use pelo menos 8 caracteres
- Inclua maiúsculas, minúsculas, números
- Guarde em local seguro (você usará depois)

**3. Aceitar Termos de Serviço**
- [ ] Marcar "I agree to the PythonAnywhere terms of service"

**4. Clique em "Sign up"**
- Pode levar alguns segundos

---

### PASSO 3: Confirmar Email

**Você receberá email com assunto:**
```
Welcome to PythonAnywhere!
```

1. Verifique sua caixa de entrada (e spam se necessário)
2. Clique no link de confirmação no email
3. Será levado de volta para PythonAnywhere
4. Você verá mensagem: "Email confirmed successfully"

**Se não receber email em 2 minutos:**
- Clique "Resend confirmation email" na página
- Aguarde mais 1-2 minutos

---

### PASSO 4: Escolher Plano

Após email confirmado, você verá página de escolha de plano:

#### 🔵 Plano Gratuito (Beginner)
```
FREE
- 100 MB disk space
- 1 web app
- Sem SSL/HTTPS
```
✅ Bom para: Teste rápido  
❌ Limitações: Sem HTTPS, pouca memória

#### 🟢 Plano Iniciante (Hacker)
```
€5 / mês
- 512 MB disk space
- 1 web app
- SSL/HTTPS incluído
```
✅ Recomendado para: Produção  
✅ Benefícios: HTTPS, mais espaço, melhor suporte

#### 🟣 Plano Semi-Profissional (Hacker+)
```
€7 / mês
- 2 GB disk space
- 2 web apps
- SSL/HTTPS incluído
```
✅ Para: Múltiplas aplicações

---

### 🎯 NOSSA RECOMENDAÇÃO

Para este projeto, recomendamos: **Plano Iniciante (€5/mês)**

**Por quê:**
- Banco de dados MySQL funcionando melhor
- SSL/HTTPS essencial para produção
- Espaço suficiente para dados
- Suporte melhorado

**Como escolher:**
1. Clique em **"€5 / month"** sob "Hacker"
2. Ou comece com Gratuito e faça upgrade depois

---

### PASSO 5: Fazer Login (Primeira Vez)

Após escolher plano:
1. Você será levado para dashboard
2. Você verá seu nome de usuário no canto superior direito
3. Panel principal mostra:
   - Web apps
   - Files
   - Bash console
   - Databases
   - etc.

---

### PASSO 6: Preparar Credenciais

**Salvar em arquivo seguro (ex: credenciais.txt - NÃO COMMITAR NO GIT):**

```
PYTHONANYWHERE ACCOUNT INFORMATION
==================================
Username: [seu_username]
Email: [seu@email.com]
Password: [sua_senha]
URL do app: [seu_username].pythonanywhere.com
Account Page: https://www.pythonanywhere.com/accounts/account/
```

---

### PASSO 7: Acessar Bash Console

No dashboard:
1. Clique em **"Bash console"** (à esquerda)
2. Ou clique em **"Consoles"** → **"Bash console"**
3. Abre terminal web do PythonAnywhere

Você verá:
```
~ $
```

**Teste conexão digitando:**
```bash
python3 --version
```

Deve retornar algo como:
```
Python 3.10.13
```

✅ Perfeito! Seu ambiente bash está funcionando.

---

## 📊 Checklist FASE 2

### Registro e Setup
- [ ] Conta criada em pythonanywhere.com
- [ ] Email confirmado
- [ ] Plano escolhido (Gratuito ou Iniciante)
- [ ] Login realizado com sucesso
- [ ] Dashboard acessível

### Validação
- [ ] Bash console abrindo
- [ ] Python3 funcionando
- [ ] Credenciais salvas em local seguro

### Documentação
- [ ] Arquivo de credenciais criado(credenciais_pythonanywhere.txt - NÃO COMMITAR)
- [ ] URL do app anotada
- [ ] Username confirmado

---

## 🎉 Resultado Esperado

Ao final da FASE 2, você deve ter:

✅ Conta ativa em PythonAnywhere  
✅ Email confirmado  
✅ Acesso ao dashboard  
✅ Bash console funcionando  
✅ Python3 disponível  
✅ Credenciais seguras  

---

## ⏭️ Próximas Etapas (FASE 3)

Depois de FASE 2 completa, faça:

**FASE 3: Setup - Clonar Repositório e Configurar**

```bash
# No PythonAnywhere bash console:

# 1. Clonar repositório
cd /home/seu_username
git clone https://github.com/Thasys/projeto-chatbot-ifs.git
cd projeto-chatbot-ifs

# 2. Criar virtualenv Python 3.12
mkvirtualenv --python=/usr/bin/python3.12 chatbot-env

# 3. Instalar dependências
pip install -r requirements-pythonanywhere.txt
```

---

## 🆘 Problemas Comuns

### Problema 1: Email não chegou
**Solução:**
- Verificar spam
- Aguardar 2 minutos
- Clicar "Resend confirmation email"
- Se continuar, tentar outro email

### Problema 2: Plano com número de cartão
**Se precisar adicionar cartão:**
- Clique em "Account settings"
- "Billing"
- Adicionar método de pagamento
- Não é obrigatório para plano gratuito

### Problema 3: Login com GitHub/Google
**Alternativa útil:**
- Pode fazer login com GitHub em vez de email
- Recomendado se tiver conta GitHub

---

## 📚 Recursos Úteis

- **PythonAnywhere Help:** https://help.pythonanywhere.com
- **Getting Started:** https://help.pythonanywhere.com/pages/Python36
- **FAQ:** https://www.pythonanywhere.com/faqs/

---

## ⏱️ Timeline

| Ação | Tempo |
|------|-------|
| Registro | 2 min |
| Email | 1-2 min |
| Confirmação | <1 min |
| Plano | 1 min |
| Login | <1 min |
| **Total** | **~5-7 min** |

---

**Status:** 🔄 Aguardando execução  
**Próxima fase:** FASE 3 - Setup repositório  
**Data prevista:** Hoje (2026-04-09)
