"""
Configuração das APIs de IA
IMPORTANTE: Configure sua chave OpenAI antes de usar!
"""

import os

# ==============================================
# CONFIGURAÇÃO OPENAI
# ==============================================

# Coloque sua chave OpenAI aqui ou defina no ambiente
# Obtenha em: https://platform.openai.com/api-keys
OPENAI_API_KEY = "cole-sua-chave-aqui"

# Ou use variável de ambiente (recomendado para produção)
if not OPENAI_API_KEY or OPENAI_API_KEY == "cole-sua-chave-aqui":
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# ==============================================
# CONFIGURAÇÃO GROK (XAI) - ALTERNATIVA GRATUITA
# ==============================================

# Chave da API do Grok (xAI) - GRATUITA!
# Obtenha em: https://console.x.ai/
GROK_API_KEY = "cole-sua-chave-grok-aqui"

# Ou use variável de ambiente
if not GROK_API_KEY or GROK_API_KEY == "cole-sua-chave-grok-aqui":
    GROK_API_KEY = os.getenv('GROK_API_KEY', '')

# ==============================================
# CONFIGURAÇÃO WHATSAPP BUSINESS API
# ==============================================

# Para integração com WhatsApp, você precisa:
# 1. Conta Twilio (https://www.twilio.com/)
# 2. WhatsApp Business API
# 3. Ou usar MessageBird, etc.

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')

# ==============================================
# OUTRAS CONFIGURAÇÕES
# ==============================================

# Modelos OpenAI disponíveis
MODELOS_DISPONIVEIS = {
    'gpt-4': 'Mais inteligente, mais caro',
    'gpt-4-turbo': 'Rápido e inteligente',
    'gpt-3.5-turbo': 'Mais rápido, mais barato'
}

# URLs dos serviços
BACKEND_URL = 'http://localhost:5000'
CHATBOT_URL = 'http://localhost:5001'
WHATSAPP_BOT_URL = 'http://localhost:5002'

print("\n" + "="*60)
print("⚙️  CONFIGURAÇÃO DE IA - GRIFFE DA PRATA")
print("="*60)

if OPENAI_API_KEY and OPENAI_API_KEY != "cole-sua-chave-aqui":
    print("✅ OpenAI API Key: Configurada")
else:
    print("❌ OpenAI API Key: NÃO CONFIGURADA!")

if GROK_API_KEY and GROK_API_KEY != "cole-sua-chave-grok-aqui":
    print("✅ Grok API Key (xAI): Configurada - GRATUITA!")
else:
    print("⚠️  Grok API Key: Opcional (alternativa gratuita)")
    print("   👉 Obtenha gratuitamente em: https://console.x.ai/")

if TWILIO_ACCOUNT_SID:
    print("✅ Twilio WhatsApp: Configurado")
else:
    print("⚠️  Twilio WhatsApp: Opcional (para integração WhatsApp)")

print("\n📚 Próximos passos:")
print("   1. Configure OPENAI_API_KEY neste arquivo")
print("   2. Execute: python chatbot_api.py")
print("   3. Execute: python whatsapp_bot.py")
print("   4. Abra index.html no navegador")
print("="*60 + "\n")
