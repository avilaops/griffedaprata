@echo off
REM Script de Inicialização - Sistema de IA
REM Griffe da Prata

echo ============================================================
echo    INICIANDO SISTEMA DE IA - GRIFFE DA PRATA
echo ============================================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Instale Python 3.10+ em: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Verificando dependencias...
python -c "import openai, flask" >nul 2>&1
if errorlevel 1 (
    echo.
    echo   Instalando dependencias...
    pip install -r requirements_ai.txt
)

echo [2/4] Verificando configuracao...
python -c "from config_openai import OPENAI_API_KEY; exit(0 if OPENAI_API_KEY and OPENAI_API_KEY != 'cole-sua-chave-aqui' else 1)" >nul 2>&1
if errorlevel 1 (
    echo.
    echo   AVISO: Chave OpenAI nao configurada!
    echo   Edite .env_config.py e adicione sua chave
    echo   Obtencao: https://platform.openai.com/api-keys
    echo.
    set /p continuar="Continuar mesmo assim? (S/N): "
    if /i not "%continuar%"=="S" exit /b 1
)

echo [3/4] Inicializando bancos de dados...
python -c "from chatbot_api import init_db; from whatsapp_bot import init_whatsapp_db; init_db(); init_whatsapp_db()"

echo [4/4] Iniciando servicos...
echo.
echo ============================================================
echo   SERVICOS DISPONIVEIS:
echo ============================================================
echo.
echo   1. Backend Principal     - http://localhost:5000
echo   2. Chatbot API          - http://localhost:5001
echo   3. WhatsApp Bot         - http://localhost:5002
echo.
echo   Site Principal:         - index.html
echo   Chat Dedicado:          - chat.html
echo   Painel Admin:           - painel_pedidos.html
echo.
echo ============================================================

REM Menu de opções
echo.
echo O que deseja iniciar?
echo.
echo [1] Tudo (Backend + Chatbot + WhatsApp)
echo [2] Backend + Chatbot
echo [3] Apenas Backend
echo [4] Apenas Chatbot
echo [5] Apenas WhatsApp Bot
echo [6] Assistente de Desenvolvimento
echo [0] Sair
echo.

set /p opcao="Digite uma opcao: "

if "%opcao%"=="1" (
    echo.
    echo Iniciando TODOS os servicos...
    start "Backend API" cmd /k "python backend_api.py"
    timeout /t 3 >nul
    start "Chatbot API" cmd /k "python chatbot_api.py"
    timeout /t 3 >nul
    start "WhatsApp Bot" cmd /k "python whatsapp_bot.py"
    timeout /t 3 >nul
    start "" index.html
    
) else if "%opcao%"=="2" (
    echo.
    echo Iniciando Backend + Chatbot...
    start "Backend API" cmd /k "python backend_api.py"
    timeout /t 3 >nul
    start "Chatbot API" cmd /k "python chatbot_api.py"
    timeout /t 3 >nul
    start "" index.html
    
) else if "%opcao%"=="3" (
    echo.
    echo Iniciando apenas Backend...
    start "Backend API" cmd /k "python backend_api.py"
    
) else if "%opcao%"=="4" (
    echo.
    echo Iniciando apenas Chatbot...
    start "Chatbot API" cmd /k "python chatbot_api.py"
    timeout /t 3 >nul
    start "" chat.html
    
) else if "%opcao%"=="5" (
    echo.
    echo Iniciando apenas WhatsApp Bot...
    start "WhatsApp Bot" cmd /k "python whatsapp_bot.py"
    
) else if "%opcao%"=="6" (
    echo.
    echo Assistente de Desenvolvimento - Opcoes:
    echo.
    echo [1] Analisar codigo
    echo [2] Gerar documentacao
    echo [3] Gerar testes
    echo [4] Analisar seguranca
    echo [5] Chat interativo
    echo.
    set /p dev_opcao="Digite uma opcao: "
    
    if "!dev_opcao!"=="1" (
        set /p arquivo="Digite o nome do arquivo: "
        python assistente_dev.py analisar !arquivo!
        
    ) else if "!dev_opcao!"=="2" (
        set /p arquivo="Digite o nome do arquivo: "
        python assistente_dev.py documentar !arquivo!
        
    ) else if "!dev_opcao!"=="3" (
        set /p arquivo="Digite o nome do arquivo: "
        python assistente_dev.py testar !arquivo!
        
    ) else if "!dev_opcao!"=="4" (
        set /p arquivo="Digite o nome do arquivo: "
        python assistente_dev.py seguranca !arquivo!
        
    ) else if "!dev_opcao!"=="5" (
        python assistente_dev.py chat
    )
    
) else if "%opcao%"=="0" (
    echo.
    echo Saindo...
    exit /b 0
    
) else (
    echo.
    echo Opcao invalida!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Servicos iniciados com sucesso!
echo ============================================================
echo.
echo   Para parar os servicos, feche as janelas abertas
echo   ou pressione Ctrl+C em cada terminal
echo.
echo ============================================================

pause
