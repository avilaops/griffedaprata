# 📱 Guia de Integração WhatsApp Business

## Passo a Passo Completo

### Opção 1: Twilio (Recomendado)

#### 1. Criar Conta no Twilio

1. Acesse: https://www.twilio.com/try-twilio
2. Crie sua conta (gratuita para testes)
3. Verifique seu email e telefone

#### 2. Configurar WhatsApp Sandbox

1. No painel Twilio, vá em: **Messaging** → **Try it Out** → **Send a WhatsApp Message**
2. Anote seu **WhatsApp Sandbox Number** (ex: +1 415 523 8886)
3. Escaneie o QR Code ou envie o código de ativação via WhatsApp

Exemplo:
```
join [seu-código-único]
```

#### 3. Obter Credenciais

No Dashboard do Twilio:
- **Account SID**: Ex: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
- **Auth Token**: Ex: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

#### 4. Configurar Webhook

1. Em **WhatsApp Sandbox Settings**
2. Em **When a message comes in**, coloque:
```
http://seu-dominio.com:5002/whatsapp/webhook
```

**Para testes locais com ngrok:**
```bash
ngrok http 5002
```

Use a URL gerada pelo ngrok:
```
https://xxxx-xx-xxx-xxx-xxx.ngrok.io/whatsapp/webhook
```

#### 5. Configurar no Sistema

Edite `.env_config.py`:

```python
TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"
```

#### 6. Testar

```bash
python whatsapp_bot.py
```

Envie uma mensagem para o número do sandbox!

---

### Opção 2: WhatsApp Business API (Oficial)

#### Requisitos
- ✅ Empresa registrada
- ✅ Número de telefone dedicado
- ✅ Facebook Business Manager
- 💰 Custo mais alto que Twilio

#### Passos

1. **Criar Facebook Business Manager**
   - https://business.facebook.com/

2. **Solicitar WhatsApp Business API**
   - Em Business Settings → WhatsApp Manager
   - Adicionar número de telefone

3. **Obter Credenciais**
   - App ID
   - App Secret
   - WhatsApp Business Account ID
   - Phone Number ID
   - Access Token

4. **Configurar Webhook**
```
POST /whatsapp/webhook
```

5. **Modificar código** em `whatsapp_bot.py` para usar a API oficial

---

### Opção 3: MessageBird

Similar ao Twilio, mas com preços diferentes.

1. **Criar conta:** https://messagebird.com/
2. **Configurar WhatsApp:** Dashboard → Channels → WhatsApp
3. **Obter API Key**
4. **Configurar webhook:** Similar ao Twilio

---

## Testando Localmente com ngrok

### 1. Instalar ngrok

**Windows:**
```powershell
choco install ngrok
```

**Linux/Mac:**
```bash
brew install ngrok
# ou
npm install -g ngrok
```

**Ou baixe:** https://ngrok.com/download

### 2. Iniciar túnel

```bash
ngrok http 5002
```

### 3. Copiar URL

```
Forwarding: https://xxxx-xx-xxx-xxx-xxx.ngrok.io -> http://localhost:5002
```

### 4. Configurar no Twilio

Use a URL do ngrok como webhook:
```
https://xxxx-xx-xxx-xxx-xxx.ngrok.io/whatsapp/webhook
```

---

## Código de Integração (Twilio)

### Instalar biblioteca Twilio

```bash
pip install twilio
```

### Exemplo de envio de mensagem

```python
from twilio.rest import Client

# Suas credenciais
account_sid = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
auth_token = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
client = Client(account_sid, auth_token)

# Enviar mensagem
message = client.messages.create(
    from_='whatsapp:+14155238886',  # Seu número Twilio
    body='Olá! Esta é uma mensagem automática da Griffe da Prata!',
    to='whatsapp:+5582981602651'    # Número do cliente
)

print(f"Mensagem enviada: {message.sid}")
```

---

## Fluxo de Atendimento

```
Cliente WhatsApp
      ↓
Envia mensagem
      ↓
Twilio recebe
      ↓
Webhook → whatsapp_bot.py
      ↓
OpenAI GPT-4 processa
      ↓
Resposta gerada
      ↓
whatsapp_bot.py retorna
      ↓
Twilio envia
      ↓
Cliente recebe resposta
```

---

## Customização de Respostas

### 1. Editar prompts

Em `config_openai.py`:

```python
PROMPTS['whatsapp'] = """
Você é o atendente virtual via WhatsApp da Griffe da Prata.

Seja:
- Informal mas profissional
- Use emojis naturalmente
- Respostas curtas e diretas
- Pergunte se pode enviar fotos dos produtos
"""
```

### 2. Adicionar comandos especiais

Em `whatsapp_bot.py`, adicione:

```python
def detectar_comando(mensagem):
    msg_lower = mensagem.lower()
    
    if 'catalogo' in msg_lower or 'produtos' in msg_lower:
        return 'enviar_catalogo'
    elif 'preco' in msg_lower or 'preço' in msg_lower:
        return 'consultar_preco'
    elif 'rastrear' in msg_lower or 'pedido' in msg_lower:
        return 'rastrear_pedido'
    else:
        return 'conversa_normal'
```

---

## Monitoramento

### Ver conversas em tempo real

```bash
# Terminal 1
python whatsapp_bot.py

# Terminal 2 (logs)
tail -f whatsapp_bot.log
```

### API de estatísticas

```bash
curl http://localhost:5002/whatsapp/estatisticas
```

Retorna:
```json
{
  "total_clientes": 45,
  "total_mensagens": 312,
  "clientes_hoje": 12,
  "media_mensagens": 6.93
}
```

---

## Custos Estimados

### Twilio (Sandbox - Grátis)
- ✅ Ilimitado para testes
- ❌ Precisa enviar código de ativação
- ❌ Mensagem "Sandbox" aparece

### Twilio (Produção)
- 💰 $0.005 por mensagem recebida
- 💰 $0.005 por mensagem enviada
- 💰 $0.50 por conversa iniciada (24h)

**Exemplo:**
- 1000 mensagens = ~$10/mês
- 100 conversas = ~$50/mês

### WhatsApp Business API
- 💰 1000 conversas grátis/mês
- 💰 Após isso, ~$0.05 por conversa
- 💰 Varia por país

---

## Troubleshooting

### Webhook não recebe mensagens

**Verifique:**
1. WhatsApp bot está rodando (`python whatsapp_bot.py`)
2. ngrok está ativo
3. URL do webhook está correta no Twilio
4. Firewall não está bloqueando porta 5002

### Erro "Invalid signature"

**Solução:** Configure o `auth_token` corretamente em `.env_config.py`

### Mensagens lentas

**Otimize:**
1. Use `gpt-3.5-turbo` ao invés de `gpt-4`
2. Reduza `max_tokens` em `config_openai.py`
3. Cache respostas comuns

---

## Segurança

### ⚠️ Importante

1. **NUNCA** commite credenciais no Git
2. Use variáveis de ambiente em produção
3. Valide todas as mensagens recebidas
4. Implemente rate limiting
5. Use HTTPS sempre (ngrok já usa)

### .gitignore

Adicione:
```
.env
.env_config.py
*.db
twilio_credentials.txt
```

---

## Deploy em Produção

### 1. Servidor (VPS/Cloud)

**Opções:**
- AWS EC2
- DigitalOcean Droplet
- Heroku
- Google Cloud

### 2. Configurar domínio

```bash
# Instalar nginx
sudo apt install nginx

# Configurar reverse proxy
server {
    location /whatsapp {
        proxy_pass http://localhost:5002;
    }
}
```

### 3. Usar PM2 para manter ativo

```bash
npm install -g pm2
pm2 start whatsapp_bot.py --interpreter python3
pm2 save
pm2 startup
```

---

## Recursos Avançados

### 1. Enviar imagens de produtos

```python
message = client.messages.create(
    from_='whatsapp:+14155238886',
    body='Confira este produto!',
    media_url=['https://seu-site.com/imagem-produto.jpg'],
    to='whatsapp:+5582981602651'
)
```

### 2. Botões interativos

```python
message = client.messages.create(
    from_='whatsapp:+14155238886',
    body='Escolha uma opção:',
    to='whatsapp:+5582981602651',
    # Twilio suporta botões via templates
)
```

### 3. Localização da loja

```python
# Enviar localização
message = client.messages.create(
    from_='whatsapp:+14155238886',
    body='Nossa localização:',
    media_url=['https://maps.google.com/?q=-9.6658,-35.7356'],
    to='whatsapp:+5582981602651'
)
```

---

## Suporte

**Documentação:**
- Twilio WhatsApp: https://www.twilio.com/docs/whatsapp
- ngrok: https://ngrok.com/docs
- OpenAI: https://platform.openai.com/docs

**Comunidade:**
- Twilio Community: https://www.twilio.com/community
- Stack Overflow: Tag `twilio-whatsapp`

---

## ✅ Checklist de Implementação

- [ ] Conta Twilio criada
- [ ] WhatsApp Sandbox configurado
- [ ] Credenciais obtidas
- [ ] `.env_config.py` configurado
- [ ] ngrok instalado e rodando
- [ ] Webhook configurado no Twilio
- [ ] `whatsapp_bot.py` rodando
- [ ] Teste enviando mensagem
- [ ] Resposta automática funcionando
- [ ] Painel admin acessível
- [ ] Monitoramento ativo

---

**🎉 Pronto! Seu WhatsApp Bot com IA está funcionando!**
