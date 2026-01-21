"""
Instalação e Teste do Sistema com Grok (xAI)
Versão gratuita e alternativa ao OpenAI
"""

import os
import sys
import subprocess
from config_grok import testar_conexao_grok, gerar_resposta_grok
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def instalar_dependencias():
    """Instala dependências necessárias"""
    print("📦 Instalando dependências...")
    try:
        # Instalar requests (já deve estar instalado)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        print("✅ Dependências instaladas!")
        return True
    except Exception as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def verificar_arquivos():
    """Verifica se todos os arquivos necessários existem"""
    arquivos_necessarios = [
        'grok_client.py',
        'config_grok.py',
        'chatbot_api.py',
        'whatsapp_bot.py',
        'assistente_dev.py',
        'backend_api.py',
        'chatbot_conversas.db',
        'whatsapp_conversas.db'
    ]

    print("🔍 Verificando arquivos...")
    arquivos_faltando = []

    for arquivo in arquivos_necessarios:
        if not os.path.exists(arquivo):
            arquivos_faltando.append(arquivo)

    if arquivos_faltando:
        print(f"❌ Arquivos faltando: {', '.join(arquivos_faltando)}")
        return False
    else:
        print("✅ Todos os arquivos estão presentes!")
        return True

def testar_api_grok():
    """Testa a conexão com a API do Grok"""
    print("🧪 Testando API do Grok...")

    if testar_conexao_grok():
        print("✅ Conexão com Grok estabelecida!")

        # Teste rápido de resposta
        try:
            resposta = gerar_resposta_grok(
                "Olá! Você é o Grok da xAI?",
                tipo='chatbot_site'
            )
            print(f"📝 Resposta de teste: {resposta[:100]}...")
            return True
        except Exception as e:
            print(f"❌ Erro no teste de resposta: {e}")
            return False
    else:
        print("❌ Falha na conexão com Grok")
        return False

def main():
    """Função principal de instalação"""
    print("="*60)
    print("🚀 INSTALAÇÃO DO SISTEMA COM GROK (xAI)")
    print("="*60)

    # Passo 1: Instalar dependências
    if not instalar_dependencias():
        return False

    # Passo 2: Verificar arquivos
    if not verificar_arquivos():
        print("❌ Arquivos necessários não encontrados!")
        return False

    # Passo 3: Verificar configuração
    grok_key = os.getenv('GROK_API_KEY', '')
    if not grok_key or grok_key == "cole-sua-chave-grok-aqui":
        print("❌ GROK_API_KEY não configurada!")
        print("   👉 Edite .env_config.py e adicione sua chave do Grok")
        print("   👉 Obtenha gratuitamente em: https://console.x.ai/")
        return False
    else:
        print("✅ Chave Grok configurada!")

    # Passo 4: Testar API
    if not testar_api_grok():
        print("❌ API do Grok não está funcionando!")
        return False

    print("\n" + "="*60)
    print("✨ INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)

    print("\n📋 PRÓXIMOS PASSOS:")
    print("1️⃣  Inicie o backend principal:     python backend_api.py")
    print("2️⃣  Em outro terminal, inicie o chatbot:     python chatbot_api.py")
    print("3️⃣  Em outro terminal, inicie o WhatsApp:    python whatsapp_bot.py")
    print("4️⃣  Abra no navegador: index.html")

    print("\n📚 RECURSOS DISPONÍVEIS:")
    print("🤖 CHATBOT: Widget flutuante em todas as páginas")
    print("📱 WHATSAPP: Atendimento automatizado")
    print("💻 DEV ASSISTANT: python assistente_dev.py [comando]")
    print("🆓 GRATUITO: Usando Grok da xAI (sem custos!)")

    print("\n🎉 Sistema pronto para uso com IA gratuita!")
    print("="*60)

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)