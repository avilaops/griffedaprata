/* 
 * Widget de Chat Flutuante - Griffe da Prata
 * Inclua em todas as páginas: <script src="chatbot-widget.js"></script>
 */

(function() {
    'use strict';

    const API_URL = 'http://localhost:5001/api/chatbot';
    let sessaoId = localStorage.getItem('chatbot_sessao_id');
    let chatAberto = false;

    // Estilos do widget
    const styles = `
        #chatbot-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        #chatbot-button {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            transition: all 0.3s;
            position: relative;
        }

        #chatbot-button:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }

        #chatbot-button .notification-badge {
            position: absolute;
            top: -5px;
            right: -5px;
            background: #ff4444;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }

        #chatbot-window {
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 380px;
            height: 600px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            display: none;
            flex-direction: column;
            overflow: hidden;
            animation: slideUp 0.3s ease;
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        #chatbot-window.open {
            display: flex;
        }

        .chatbot-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .chatbot-header-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .chatbot-avatar {
            width: 40px;
            height: 40px;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }

        .chatbot-header h3 {
            font-size: 16px;
            margin: 0;
        }

        .chatbot-header p {
            font-size: 11px;
            margin: 0;
            opacity: 0.9;
        }

        .chatbot-close {
            background: none;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .chatbot-messages {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            background: #f5f5f5;
        }

        .chatbot-message {
            margin-bottom: 12px;
            display: flex;
            gap: 8px;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .chatbot-message.user {
            flex-direction: row-reverse;
        }

        .chatbot-message-bubble {
            max-width: 75%;
            padding: 10px 14px;
            border-radius: 15px;
            font-size: 14px;
            line-height: 1.4;
        }

        .chatbot-message.bot .chatbot-message-bubble {
            background: white;
            color: #333;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .chatbot-message.user .chatbot-message-bubble {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .chatbot-typing {
            display: none;
            padding: 10px;
        }

        .chatbot-typing.active {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .chatbot-typing-dots {
            display: flex;
            gap: 3px;
        }

        .chatbot-typing-dots span {
            width: 6px;
            height: 6px;
            background: #667eea;
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out;
        }

        .chatbot-typing-dots span:nth-child(1) { animation-delay: -0.32s; }
        .chatbot-typing-dots span:nth-child(2) { animation-delay: -0.16s; }

        .chatbot-input-area {
            padding: 15px;
            background: white;
            border-top: 1px solid #eee;
            display: flex;
            gap: 8px;
        }

        .chatbot-input {
            flex: 1;
            padding: 10px 14px;
            border: 2px solid #eee;
            border-radius: 20px;
            font-size: 13px;
            outline: none;
            transition: border-color 0.3s;
        }

        .chatbot-input:focus {
            border-color: #667eea;
        }

        .chatbot-send {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 50%;
            color: white;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }

        .chatbot-send:hover {
            transform: scale(1.1);
        }

        .chatbot-send:active {
            transform: scale(0.95);
        }

        @media (max-width: 480px) {
            #chatbot-window {
                width: calc(100vw - 40px);
                height: calc(100vh - 140px);
            }
        }
    `;

    // HTML do widget
    const widgetHTML = `
        <button id="chatbot-button">
            🤖
            <span class="notification-badge" style="display: none;">1</span>
        </button>
        
        <div id="chatbot-window">
            <div class="chatbot-header">
                <div class="chatbot-header-info">
                    <div class="chatbot-avatar">🤖</div>
                    <div>
                        <h3>Assistente Virtual</h3>
                        <p>Griffe da Prata</p>
                    </div>
                </div>
                <button class="chatbot-close">×</button>
            </div>
            
            <div class="chatbot-messages" id="chatbot-messages"></div>
            
            <div class="chatbot-typing" id="chatbot-typing">
                <div class="chatbot-typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <span style="font-size: 11px; color: #999;">Digitando...</span>
            </div>
            
            <div class="chatbot-input-area">
                <input 
                    type="text" 
                    class="chatbot-input" 
                    id="chatbot-input" 
                    placeholder="Digite sua mensagem..."
                />
                <button class="chatbot-send" id="chatbot-send">➤</button>
            </div>
        </div>
    `;

    // Inicializar widget
    function init() {
        // Adicionar estilos
        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);

        // Adicionar HTML
        const widgetDiv = document.createElement('div');
        widgetDiv.id = 'chatbot-widget';
        widgetDiv.innerHTML = widgetHTML;
        document.body.appendChild(widgetDiv);

        // Event listeners
        document.getElementById('chatbot-button').addEventListener('click', toggleChat);
        document.querySelector('.chatbot-close').addEventListener('click', toggleChat);
        document.getElementById('chatbot-send').addEventListener('click', enviarMensagem);
        document.getElementById('chatbot-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') enviarMensagem();
        });

        // Inicializar sessão
        inicializarSessao();
    }

    // Toggle chat
    function toggleChat() {
        const window = document.getElementById('chatbot-window');
        chatAberto = !chatAberto;
        
        if (chatAberto) {
            window.classList.add('open');
            document.querySelector('.notification-badge').style.display = 'none';
            document.getElementById('chatbot-input').focus();
        } else {
            window.classList.remove('open');
        }
    }

    // Inicializar sessão
    async function inicializarSessao() {
        if (!sessaoId) {
            try {
                const usuario = JSON.parse(localStorage.getItem('usuario_logado') || '{}');
                
                const response = await fetch(`${API_URL}/iniciar`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        nome: usuario.nome,
                        email: usuario.email
                    })
                });

                const data = await response.json();
                sessaoId = data.sessao_id;
                localStorage.setItem('chatbot_sessao_id', sessaoId);

                // Mostrar mensagem inicial se abrir o chat
                setTimeout(() => {
                    if (!chatAberto) {
                        document.querySelector('.notification-badge').style.display = 'flex';
                    }
                }, 3000);

            } catch (error) {
                console.error('Erro ao inicializar chatbot:', error);
            }
        }
    }

    // Adicionar mensagem
    function adicionarMensagem(tipo, texto) {
        const messagesDiv = document.getElementById('chatbot-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chatbot-message ${tipo}`;
        
        const bubble = document.createElement('div');
        bubble.className = 'chatbot-message-bubble';
        bubble.innerHTML = formatarMensagem(texto);
        
        messageDiv.appendChild(bubble);
        messagesDiv.appendChild(messageDiv);
        
        // Scroll para o final
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    // Formatar mensagem
    function formatarMensagem(texto) {
        return texto
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
    }

    // Enviar mensagem
    async function enviarMensagem() {
        const input = document.getElementById('chatbot-input');
        const mensagem = input.value.trim();

        if (!mensagem) return;

        // Adicionar mensagem do usuário
        adicionarMensagem('user', mensagem);
        input.value = '';

        // Mostrar indicador de digitação
        const typingIndicator = document.getElementById('chatbot-typing');
        typingIndicator.classList.add('active');

        try {
            const response = await fetch(`${API_URL}/mensagem`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    mensagem: mensagem,
                    sessao_id: sessaoId
                })
            });

            const data = await response.json();

            // Esconder indicador
            typingIndicator.classList.remove('active');

            // Adicionar resposta
            adicionarMensagem('bot', data.resposta);

        } catch (error) {
            console.error('Erro:', error);
            typingIndicator.classList.remove('active');
            adicionarMensagem('bot', 'Desculpe, ocorreu um erro. Tente novamente!');
        }
    }

    // Inicializar quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
