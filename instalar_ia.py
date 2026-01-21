# -*- coding: utf-8 -*-
"""
Script de Instalação e Configuração
Sistema de IA - Griffe da Prata
"""

import subprocess
import sys
import os

print("="*70)
print("🚀 INSTALAÇÃO DO SISTEMA DE IA - GRIFFE DA PRATA")
print("="*70)

# Passo 1: Instalar dependências
print("\n📦 Passo 1: Instalando dependências Python...")
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_ai.txt"])
    print("✅ Dependências instaladas com sucesso!")
except Exception as e:
    print(f"❌ Erro ao instalar dependências: {e}")
    sys.exit(1)

# Passo 2: Verificar chave OpenAI
print("\n🔑 Passo 2: Verificando chave OpenAI...")
from config_openai import OPENAI_API_KEY

if not OPENAI_API_KEY or OPENAI_API_KEY == "cole-sua-chave-aqui":
    print("❌ Chave OpenAI não configurada!")
    print("\n📝 Para configurar:")
    print("   1. Abra o arquivo: .env_config.py")
    print("   2. Coloque sua chave em: OPENAI_API_KEY = 'sua-chave-aqui'")
    print("   3. Execute este script novamente")
    print("\n🔗 Obtenha sua chave em: https://platform.openai.com/api-keys")
    
    resposta = input("\nDeseja continuar sem a chave? (s/n): ")
    if resposta.lower() != 's':
        sys.exit(1)
else:
    print("✅ Chave OpenAI configurada!")

# Passo 3: Inicializar bancos de dados
print("\n💾 Passo 3: Inicializando bancos de dados...")
try:
    from chatbot_api import init_db
    from whatsapp_bot import init_whatsapp_db
    
    init_db()
    init_whatsapp_db()
    print("✅ Bancos de dados criados!")
except Exception as e:
    print(f"⚠️  Aviso: {e}")

# Passo 4: Testar APIs
print("\n🧪 Passo 4: Testando sistema...")
try:
    from config_openai import chat_completion
    
    resposta = chat_completion(
        [{"role": "user", "content": "Olá, diga apenas: Sistema funcionando!"}],
        tipo='chatbot_site'
    )
    
    if resposta:
        print("✅ API OpenAI funcionando!")
        print(f"   Resposta de teste: {resposta[:50]}...")
    else:
        print("⚠️  API não respondeu (verifique sua chave)")
        
except Exception as e:
    print(f"⚠️  Não foi possível testar: {e}")

# Resumo final
print("\n" + "="*70)
print("✨ INSTALAÇÃO CONCLUÍDA!")
print("="*70)

print("\n📋 PRÓXIMOS PASSOS:\n")
print("1️⃣  Configure sua chave OpenAI em .env_config.py")
print("2️⃣  Inicie o backend principal:")
print("    python backend_api.py")
print("\n3️⃣  Em outro terminal, inicie o chatbot:")
print("    python chatbot_api.py")
print("\n4️⃣  Em outro terminal, inicie o WhatsApp bot:")
print("    python whatsapp_bot.py")
print("\n5️⃣  Abra no navegador:")
print("    - Site: index.html")
print("    - Chat: chat.html")
print("    - Admin: painel_pedidos.html")

print("\n" + "="*70)
print("📚 RECURSOS DISPONÍVEIS:")
print("="*70)
print("\n🤖 CHATBOT DE ATENDIMENTO:")
print("   - Widget flutuante em todas as páginas")
print("   - Chat dedicado: chat.html")
print("   - API: http://localhost:5001")

print("\n📱 WHATSAPP BOT:")
print("   - Atendimento automatizado via WhatsApp")
print("   - Integração com Twilio/MessageBird")
print("   - API: http://localhost:5002")

print("\n💻 ASSISTENTE DE DESENVOLVIMENTO:")
print("   - Analisar código: python assistente_dev.py analisar arquivo.py")
print("   - Gerar testes: python assistente_dev.py testar arquivo.py")
print("   - Documentar: python assistente_dev.py documentar arquivo.py")
print("   - Segurança: python assistente_dev.py seguranca arquivo.py")
print("   - Chat interativo: python assistente_dev.py chat")

print("\n" + "="*70)
print("🎉 Tudo pronto para usar IA no seu e-commerce!")
print("="*70 + "\n")
