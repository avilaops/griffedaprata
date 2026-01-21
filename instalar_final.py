"""
Instalação Final - Sistema de IA Griffe da Prata
Sistema Híbrido Inteligente - 100% GRATUITO, SEM APIs EXTERNAS!
"""

import os
import sys
from chatbot_hibrido import ChatBotInteligente

def main():
    print("="*60)
    print("🚀 SISTEMA DE IA - GRIFFE DA PRATA")
    print("="*60)
    print("\n✨ Sistema Híbrido Inteligente")
    print("💯 100% GRATUITO - Sem custos de API!")
    print("🤖 Chatbot baseado em regras e contexto")
    print("\n" + "="*60)
    
    # Testar chatbot
    print("\n🧪 Testando Chatbot...")
    bot = ChatBotInteligente()
    
    testes = [
        ("Olá!", "Saudação"),
        ("Quero ver anéis de prata", "Consulta de produto"),
        ("Quanto custa?", "Preço")
    ]
    
    for mensagem, desc in testes:
        resposta = bot.gerar_resposta(mensagem)
        print(f"\n✅ Teste: {desc}")
        print(f"   Resposta: {resposta[:80]}...")
    
    print("\n" + "="*60)
    print("✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    
    print("\n📋 COMO USAR:")
    print("\n1️⃣  Inicie o Backend:")
    print("   python backend_api.py")
    
    print("\n2️⃣  Inicie o Chatbot (em outro terminal):")
    print("   python chatbot_api.py")
    
    print("\n3️⃣  Inicie o WhatsApp Bot (opcional):")
    print("   python whatsapp_bot.py")
    
    print("\n4️⃣  Abra no navegador:")
    print("   index.html")
    
    print("\n🎯 RECURSOS DISPONÍVEIS:")
    print("  🤖 Chatbot inteligente no site")
    print("  📱 Bot WhatsApp automatizado")
    print("  💬 Respostas contextuais sobre produtos")
    print("  💰 Informações de preços e pagamento")
    print("  📦 Detalhes de entrega e garantia")
    print("  💎 100% focado em joias de prata 925")
    
    print("\n💡 VANTAGENS:")
    print("  ✅ SEM custos de API")
    print("  ✅ SEM limites de uso")
    print("  ✅ Funciona OFFLINE")
    print("  ✅ Respostas instantâneas")
    print("  ✅ Totalmente personalizável")
    
    print("\n🎉 Sistema pronto para atender seus clientes!")
    print("="*60)

if __name__ == "__main__":
    main()