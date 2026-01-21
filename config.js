// Configuração de API - Griffe da Prata
// Trocar entre desenvolvimento e produção

const CONFIG = {
    // 🌐 PRODUÇÃO (GitHub Pages + Hetzner)
    PRODUCTION: {
        API_URL: 'https://api.griffedaprata.com.br',
        CHATBOT_URL: 'https://api.griffedaprata.com.br/chatbot',
        WHATSAPP_URL: 'https://api.griffedaprata.com.br/whatsapp'
    },
    
    // 💻 DESENVOLVIMENTO LOCAL
    DEVELOPMENT: {
        API_URL: 'http://localhost:5000',
        CHATBOT_URL: 'http://localhost:5001',
        WHATSAPP_URL: 'http://localhost:5002'
    },

    // 📞 CONTATOS
    CONTATOS: {
        whatsapp: '5517997088111',
        whatsappFormatado: '+55 17 99708-8111',
        whatsappLink: 'https://wa.me/5517997088111',
        instagram: 'https://www.instagram.com/griffedaprata/',
        instagramUser: '@griffedaprata',
        email: 'contato@griffedaprata.com.br'
    }
};

// Detectar ambiente automaticamente
const isDevelopment = window.location.hostname === 'localhost' || 
                      window.location.hostname === '127.0.0.1' ||
                      window.location.hostname.includes('192.168');

// Exportar configuração ativa
const ACTIVE_CONFIG = isDevelopment ? CONFIG.DEVELOPMENT : CONFIG.PRODUCTION;

// URLs prontas para usar
const API_URL = ACTIVE_CONFIG.API_URL;
const CHATBOT_URL = ACTIVE_CONFIG.CHATBOT_URL;
const WHATSAPP_URL = ACTIVE_CONFIG.WHATSAPP_URL;
const CONTATOS = CONFIG.CONTATOS;

console.log(`🔧 Ambiente: ${isDevelopment ? 'DESENVOLVIMENTO' : 'PRODUÇÃO'}`);
console.log(`🌐 API: ${API_URL}`);
console.log(`📱 WhatsApp: ${CONTATOS.whatsappFormatado}`);
