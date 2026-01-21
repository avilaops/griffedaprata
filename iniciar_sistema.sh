#!/bin/bash
# Script de Inicialização - Sistema de IA
# Griffe da Prata (Linux/Mac)

echo "============================================================"
echo "   INICIANDO SISTEMA DE IA - GRIFFE DA PRATA"
echo "============================================================"
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ ERRO: Python não encontrado!"
    echo "   Instale Python 3.10+ em: https://www.python.org/downloads/"
    exit 1
fi

echo "[1/4] Verificando dependências..."
python3 -c "import openai, flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "   📦 Instalando dependências..."
    pip3 install -r requirements_ai.txt
fi

echo "[2/4] Verificando configuração..."
python3 -c "from config_openai import OPENAI_API_KEY; exit(0 if OPENAI_API_KEY and OPENAI_API_KEY != 'cole-sua-chave-aqui' else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "   ⚠️  AVISO: Chave OpenAI não configurada!"
    echo "   Edite .env_config.py e adicione sua chave"
    echo "   Obtenha em: https://platform.openai.com/api-keys"
    echo ""
    read -p "Continuar mesmo assim? (s/n): " continuar
    if [ "$continuar" != "s" ] && [ "$continuar" != "S" ]; then
        exit 1
    fi
fi

echo "[3/4] Inicializando bancos de dados..."
python3 -c "from chatbot_api import init_db; from whatsapp_bot import init_whatsapp_db; init_db(); init_whatsapp_db()"

echo "[4/4] Iniciando serviços..."
echo ""
echo "============================================================"
echo "   SERVIÇOS DISPONÍVEIS:"
echo "============================================================"
echo ""
echo "   1. Backend Principal     - http://localhost:5000"
echo "   2. Chatbot API          - http://localhost:5001"
echo "   3. WhatsApp Bot         - http://localhost:5002"
echo ""
echo "   Site Principal:         - index.html"
echo "   Chat Dedicado:          - chat.html"
echo "   Painel Admin:           - painel_pedidos.html"
echo ""
echo "============================================================"

# Menu de opções
echo ""
echo "O que deseja iniciar?"
echo ""
echo "[1] Tudo (Backend + Chatbot + WhatsApp)"
echo "[2] Backend + Chatbot"
echo "[3] Apenas Backend"
echo "[4] Apenas Chatbot"
echo "[5] Apenas WhatsApp Bot"
echo "[6] Assistente de Desenvolvimento"
echo "[0] Sair"
echo ""

read -p "Digite uma opção: " opcao

case $opcao in
    1)
        echo ""
        echo "🚀 Iniciando TODOS os serviços..."
        gnome-terminal -- bash -c "python3 backend_api.py; exec bash" 2>/dev/null || \
        xterm -e "python3 backend_api.py" 2>/dev/null || \
        python3 backend_api.py &
        
        sleep 3
        
        gnome-terminal -- bash -c "python3 chatbot_api.py; exec bash" 2>/dev/null || \
        xterm -e "python3 chatbot_api.py" 2>/dev/null || \
        python3 chatbot_api.py &
        
        sleep 3
        
        gnome-terminal -- bash -c "python3 whatsapp_bot.py; exec bash" 2>/dev/null || \
        xterm -e "python3 whatsapp_bot.py" 2>/dev/null || \
        python3 whatsapp_bot.py &
        
        sleep 3
        xdg-open index.html 2>/dev/null || open index.html 2>/dev/null
        ;;
        
    2)
        echo ""
        echo "🚀 Iniciando Backend + Chatbot..."
        python3 backend_api.py &
        sleep 3
        python3 chatbot_api.py &
        sleep 3
        xdg-open index.html 2>/dev/null || open index.html 2>/dev/null
        ;;
        
    3)
        echo ""
        echo "🚀 Iniciando apenas Backend..."
        python3 backend_api.py
        ;;
        
    4)
        echo ""
        echo "🚀 Iniciando apenas Chatbot..."
        python3 chatbot_api.py &
        sleep 3
        xdg-open chat.html 2>/dev/null || open chat.html 2>/dev/null
        ;;
        
    5)
        echo ""
        echo "🚀 Iniciando apenas WhatsApp Bot..."
        python3 whatsapp_bot.py
        ;;
        
    6)
        echo ""
        echo "💻 Assistente de Desenvolvimento"
        python3 assistente_dev.py chat
        ;;
        
    0)
        echo ""
        echo "👋 Saindo..."
        exit 0
        ;;
        
    *)
        echo ""
        echo "❌ Opção inválida!"
        exit 1
        ;;
esac

echo ""
echo "============================================================"
echo "   ✅ Serviços iniciados com sucesso!"
echo "============================================================"
echo ""
echo "   Para parar os serviços: Ctrl+C ou kill <PID>"
echo ""
echo "============================================================"
