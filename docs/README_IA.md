# 🤖 Sistema de IA - Griffe da Prata

Sistema completo de Inteligência Artificial integrado ao e-commerce, incluindo chatbot de atendimento, WhatsApp bot e assistente de desenvolvimento.

## 📋 Índice

1. [Funcionalidades](#funcionalidades)
2. [Instalação](#instalação)
3. [Configuração](#configuração)
4. [Uso](#uso)
5. [APIs Disponíveis](#apis-disponíveis)
6. [Integração WhatsApp](#integração-whatsapp)
7. [Assistente de Desenvolvimento](#assistente-de-desenvolvimento)

---

## ✨ Funcionalidades

### 🤖 Chatbot de Atendimento
- ✅ Widget flutuante em todas as páginas
- ✅ Chat dedicado com interface completa
- ✅ Histórico de conversas
- ✅ Recomendações de produtos
- ✅ Integração com banco de dados
- ✅ Respostas inteligentes com contexto

### 📱 WhatsApp Bot
- ✅ Atendimento automatizado via WhatsApp
- ✅ Detecção de intenção
- ✅ Histórico por cliente
- ✅ Integração com Twilio/MessageBird
- ✅ Estatísticas de atendimento

### 💻 Assistente de Desenvolvimento
- ✅ Análise de código
- ✅ Geração de testes
- ✅ Documentação automática
- ✅ Auditoria de segurança
- ✅ Otimização de performance
- ✅ Geração de features

---

## 🚀 Instalação

### 1. Instalar Dependências

```bash
python instalar_ia.py
```

Ou manualmente:

```bash
pip install -r requirements_ai.txt
```

### 2. Configurar Chave OpenAI

Edite o arquivo `.env_config.py`:

```python
OPENAI_API_KEY = "sua-chave-aqui"
```

**Obtenha sua chave em:** https://platform.openai.com/api-keys

---

## ⚙️ Configuração

### Opções de Modelo

Edite `config_openai.py`:

```python
# GPT-4 (mais inteligente, mais caro)
MODELO_CHAT = "gpt-4"

# GPT-3.5 (mais rápido, mais barato)
MODELO_CHAT = "gpt-3.5-turbo"
```

### Personalizar Prompts

Em `config_openai.py`, seção `PROMPTS`:

```python
PROMPTS = {
    'atendimento': "...",  # Chatbot do site
    'whatsapp': "...",     # WhatsApp bot
    'desenvolvimento': "..." # Assistente dev
}
```

---

## 🎯 Uso

### Iniciar Serviços

**Terminal 1 - Backend Principal:**
```bash
python backend_api.py
```

**Terminal 2 - Chatbot API:**
```bash
python chatbot_api.py
```

**Terminal 3 - WhatsApp Bot (opcional):**
```bash
python whatsapp_bot.py
```

### Integrar Widget nas Páginas

Adicione no final do `<body>` de cada página HTML:

```html
<script src="chatbot-widget.js"></script>
```

O widget flutuante aparecerá automaticamente!

### Chat Dedicado

Acesse: `chat.html`

---

## 🔌 APIs Disponíveis

### Chatbot API (Porta 5001)

#### Iniciar Sessão
```http
POST /api/chatbot/iniciar
Content-Type: application/json

{
  "nome": "João",
  "email": "joao@email.com"
}
```

#### Enviar Mensagem
```http
POST /api/chatbot/mensagem
Content-Type: application/json

{
  "sessao_id": "abc123",
  "mensagem": "Quero ver anéis"
}
```

#### Buscar Histórico
```http
GET /api/chatbot/historico/{sessao_id}
```

#### Estatísticas
```http
GET /api/chatbot/estatisticas
```

---

### WhatsApp Bot API (Porta 5002)

#### Webhook (receber mensagens)
```http
POST /whatsapp/webhook
Content-Type: application/json

{
  "from": "5582981602651",
  "body": "Olá, gostaria de ver produtos"
}
```

#### Enviar Mensagem
```http
POST /whatsapp/enviar
Content-Type: application/json

{
  "numero": "5582981602651",
  "mensagem": "Olá! Como posso ajudar?"
}
```

#### Histórico de Cliente
```http
GET /whatsapp/historico/{numero}
```

#### Listar Clientes
```http
GET /whatsapp/clientes
```

---

## 📱 Integração WhatsApp

### Usando Twilio

1. **Crie conta:** https://www.twilio.com/
2. **Configure WhatsApp Sandbox**
3. **Edite `.env_config.py`:**

```python
TWILIO_ACCOUNT_SID = "seu_account_sid"
TWILIO_AUTH_TOKEN = "seu_auth_token"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"
```

4. **Configure Webhook no Twilio:**
```
http://seu-servidor.com:5002/whatsapp/webhook
```

### Usando MessageBird

Similar ao Twilio, configure as credenciais e webhook.

### Fluxo de Atendimento

```mermaid
Cliente → WhatsApp → Webhook → IA → Resposta → WhatsApp → Cliente
```

---

## 💻 Assistente de Desenvolvimento

### Comandos Disponíveis

#### Analisar Código
```bash
python assistente_dev.py analisar backend_api.py
```

Retorna:
- Resumo do código
- Nota de qualidade (0-10)
- Bugs potenciais
- Vulnerabilidades
- Sugestões de melhoria

#### Gerar Documentação
```bash
python assistente_dev.py documentar chatbot_api.py
```

Cria arquivo `chatbot_api_DOC.md` com documentação completa.

#### Gerar Testes
```bash
python assistente_dev.py testar config_openai.py
```

Cria arquivo `test_config_openai.py` com testes unitários.

#### Analisar Performance
```bash
python assistente_dev.py otimizar backend_api.py
```

Retorna:
- Análise de complexidade (Big O)
- Gargalos identificados
- Código otimizado

#### Auditoria de Segurança
```bash
python assistente_dev.py seguranca backend_api.py
```

Verifica:
- SQL Injection
- XSS
- Validação de entrada
- OWASP Top 10

#### Gerar Feature
```bash
python assistente_dev.py feature "Sistema de cupons de desconto"
```

Gera código completo para a feature solicitada.

#### Analisar Projeto Completo
```bash
python assistente_dev.py projeto
```

Cria relatório `ANALISE_PROJETO.md` com análise de todos os arquivos.

#### Chat Interativo
```bash
python assistente_dev.py chat
```

Modo conversação com o assistente.

---

## 📊 Monitoramento

### Ver Estatísticas do Chatbot

```bash
curl http://localhost:5001/api/chatbot/estatisticas
```

Retorna:
```json
{
  "total_sessoes": 150,
  "total_mensagens": 823,
  "sessoes_hoje": 45,
  "media_mensagens_por_sessao": 5.49
}
```

### Ver Estatísticas WhatsApp

```bash
curl http://localhost:5002/whatsapp/estatisticas
```

---

## 🎨 Personalização

### Alterar Aparência do Widget

Edite `chatbot-widget.js`, seção de estilos:

```javascript
const styles = `
    #chatbot-button {
        background: linear-gradient(135deg, #sua-cor-1, #sua-cor-2);
    }
`;
```

### Alterar Mensagens Padrão

Edite `config_openai.py`, seção `CONTEXTO_EMPRESA`:

```python
CONTEXTO_EMPRESA = """
Sua descrição da empresa aqui...
"""
```

---

## 🔧 Troubleshooting

### Erro: "OPENAI_API_KEY não configurada"

**Solução:** Configure a chave em `.env_config.py`

### Chatbot não responde

**Verifique:**
1. `chatbot_api.py` está rodando
2. Porta 5001 está livre
3. CORS configurado corretamente

### WhatsApp não recebe mensagens

**Verifique:**
1. `whatsapp_bot.py` está rodando
2. Webhook configurado no Twilio
3. URL pública acessível (use ngrok para testes)

### Usar ngrok para Testes

```bash
ngrok http 5002
```

Use a URL gerada como webhook no Twilio.

---

## 📈 Custos Estimados

### OpenAI API (GPT-4)
- Input: $0.03 / 1K tokens
- Output: $0.06 / 1K tokens
- ~500 conversas/mês = ~$10-20

### OpenAI API (GPT-3.5-turbo)
- Input: $0.0015 / 1K tokens
- Output: $0.002 / 1K tokens
- ~500 conversas/mês = ~$1-3

### Twilio WhatsApp
- $0.005 por mensagem recebida
- $0.005 por mensagem enviada
- 1000 mensagens = $10

---

## 🚀 Próximos Passos

1. ✅ Configurar OpenAI API
2. ✅ Testar chatbot no site
3. ✅ Configurar WhatsApp (opcional)
4. ⏳ Analisar código com assistente dev
5. ⏳ Monitorar estatísticas
6. ⏳ Personalizar prompts
7. ⏳ Adicionar mais funcionalidades

---

## 📞 Suporte

**Em caso de dúvidas:**
- 📧 Email: contato@griffedaprata.com.br
- 📱 WhatsApp: (82) 98160-2651

---

## 📝 Notas Importantes

1. **Segurança:** NUNCA compartilhe sua chave OpenAI
2. **Custos:** Monitore uso da API para evitar surpresas
3. **Rate Limits:** OpenAI tem limites de requisições por minuto
4. **Backup:** Faça backup dos bancos de dados regularmente

---

## 🎉 Pronto!

Seu sistema de IA está completo e funcional!

**Recursos Implementados:**
- ✅ Chatbot inteligente com contexto
- ✅ Widget flutuante responsivo
- ✅ WhatsApp bot automatizado
- ✅ Assistente de desenvolvimento
- ✅ Recomendação de produtos
- ✅ Histórico de conversas
- ✅ Estatísticas e analytics

**Aproveite! 🚀**
