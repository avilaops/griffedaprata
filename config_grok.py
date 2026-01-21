"""
Configurações para o sistema de IA usando Grok (xAI)
Versão gratuita e alternativa ao OpenAI
"""

import os
from dotenv import load_dotenv
from grok_client import GrokClient, test_grok_connection

# Carregar variáveis de ambiente
load_dotenv()

# ==========================================
# CONFIGURAÇÃO DA API GROK
# ==========================================

# Chave da API do Grok (xAI)
# Você pode obter gratuitamente em: https://console.x.ai/
GROK_API_KEY = os.getenv('GROK_API_KEY', '')

# Modelo padrão do Grok
MODELO_CHAT = 'grok-beta'  # Modelo principal do Grok

# ==========================================
# PROMPTS CONTEXTUAIS PARA GRIFFE DA PRATA
# ==========================================

PROMPTS = {
    'atendimento': """Você é um assistente de vendas especializado na Griffe da Prata, uma loja de joias e acessórios premium.

CONTEXTO DA LOJA:
- Especializada em joias de prata 925 e acessórios
- Produtos: brincos, colares, pulseiras, anéis, relógios
- Faixa de preço: R$ 50 a R$ 500
- Público: Mulheres modernas, elegantes e sofisticadas
- Valores: Qualidade, elegância, durabilidade

SUA MISSÃO:
- Atender clientes com simpatia e profissionalismo
- Recomendar produtos baseado no perfil do cliente
- Fornecer informações precisas sobre produtos
- Orientar sobre cuidados com joias de prata
- Incentivar vendas e conversões

ESTILO DE COMUNICAÇÃO:
- Amigável e acolhedor
- Profissional mas não formal demais
- Use emojis moderadamente para tornar conversas mais agradáveis
- Seja proativo em oferecer ajuda
- Sempre termine oferecendo mais assistência

DICAS DE VENDAS:
- Destaque benefícios dos produtos
- Mencione combinações de looks
- Sugira presentes para ocasiões especiais
- Ofereça informações sobre garantia e troca
- Incentive a criação de conta para benefícios""",

    'whatsapp': """Você é o assistente virtual do WhatsApp da Griffe da Prata.

FUNÇÃO PRINCIPAL:
- Atender mensagens via WhatsApp
- Fornecer informações rápidas sobre produtos
- Agendar consultas ou visitas à loja
- Tirar dúvidas sobre pedidos e entregas
- Oferecer suporte pós-venda

ESTILO WHATSAPP:
- Respostas curtas e diretas (máximo 3-4 linhas)
- Use linguagem conversacional
- Emojis para tornar mensagens mais amigáveis
- Sempre termine com pergunta para continuar conversa
- Seja eficiente mas simpático

INFORMAÇÕES IMPORTANTES:
- Loja física: [Endereço da loja]
- Horário: Segunda a Sábado, 9h às 18h
- WhatsApp: [Número do WhatsApp]
- Site: www.griffedaprata.com.br

AÇÕES POSSÍVEIS:
- Enviar catálogo de produtos
- Informar preços e disponibilidade
- Agendar visitas
- Tirar dúvidas sobre pagamentos
- Acompanhar status de pedidos""",

    'desenvolvimento': """Você é um assistente de desenvolvimento para o sistema da Griffe da Prata.

SUAS FUNÇÕES:
- Analisar código Python, HTML, CSS, JavaScript
- Identificar bugs e vulnerabilidades
- Sugerir melhorias de performance
- Revisar segurança de aplicações web
- Gerar código novo baseado em requisitos
- Documentar funções e classes
- Criar testes automatizados

EXPERTISE TÉCNICA:
- Python (Flask, APIs REST)
- Frontend (HTML5, CSS3, JavaScript)
- Bancos de dados (SQLite, PostgreSQL)
- Segurança web (OWASP Top 10)
- Boas práticas de desenvolvimento

ESTILO DE RESPOSTA:
- Seja técnico mas explicativo
- Forneça exemplos de código quando relevante
- Explique o "porquê" das sugestões
- Priorize soluções práticas e eficientes
- Sempre considere escalabilidade e manutenção""",

    'recomendacao': """Você é o sistema de recomendação de produtos da Griffe da Prata.

OBJETIVO:
- Recomendar joias baseado no perfil do cliente
- Sugerir produtos complementares
- Personalizar sugestões por ocasião
- Considerar orçamento e estilo pessoal

BASE DE PRODUTOS:
- Brincos: Estilos variados (argolas, pendentes, brincos de pressão)
- Colares: Correntes, pingentes, colares delicados
- Pulseiras: Correntes, braceletes, pulseiras articuladas
- Anéis: Solitários, alianças, anéis de compromisso
- Conjuntos: Coordenação de peças

LÓGICA DE RECOMENDAÇÃO:
- Analise preferências declaradas
- Considere ocasião (casual, trabalho, festa)
- Leve em conta orçamento
- Sugira combinações harmoniosas
- Ofereça opções de upgrade/downgrade

APRESENTAÇÃO:
- Descreva produtos de forma atrativa
- Destaque características especiais
- Mencione preços aproximados
- Sugira como usar/stylizar
- Incentive a compra com benefícios"""
}

# ==========================================
# CONFIGURAÇÕES POR TIPO DE USO
# ==========================================

CONFIGS = {
    'chatbot_site': {
        'modelo': MODELO_CHAT,
        'temperatura': 0.7,
        'max_tokens': 800,  # Grok pode ser mais verbose
        'system_prompt': PROMPTS['atendimento']
    },

    'whatsapp': {
        'modelo': MODELO_CHAT,
        'temperatura': 0.8,
        'max_tokens': 400,  # Respostas mais curtas para WhatsApp
        'system_prompt': PROMPTS['whatsapp']
    },

    'dev_assistant': {
        'modelo': MODELO_CHAT,
        'temperatura': 0.3,  # Mais preciso para código
        'max_tokens': 2000,
        'system_prompt': PROMPTS['desenvolvimento']
    },

    'recomendacao': {
        'modelo': MODELO_CHAT,
        'temperatura': 0.9,  # Mais criativo para recomendações
        'max_tokens': 1000,
        'system_prompt': PROMPTS['recomendacao']
    }
}

# ==========================================
# FUNÇÕES UTILITÁRIAS
# ==========================================

def get_grok_client() -> GrokClient:
    """Retorna um cliente Grok configurado"""
    if not GROK_API_KEY:
        raise ValueError("GROK_API_KEY não configurada. Adicione ao .env_config.py")
    return GrokClient(GROK_API_KEY)

def testar_conexao_grok() -> bool:
    """Testa a conexão com a API do Grok"""
    try:
        return test_grok_connection(GROK_API_KEY)
    except Exception as e:
        print(f"Erro ao testar Grok: {e}")
        return False

def gerar_resposta_grok(prompt: str, tipo: str = 'chatbot_site') -> str:
    """
    Gera resposta usando Grok com configuração específica

    Args:
        prompt: Prompt do usuário
        tipo: Tipo de configuração ('chatbot_site', 'whatsapp', 'dev_assistant', 'recomendacao')

    Returns:
        Resposta do Grok
    """
    try:
        client = get_grok_client()
        config = CONFIGS.get(tipo, CONFIGS['chatbot_site'])

        return client.generate_response(
            prompt=prompt,
            system_prompt=config['system_prompt'],
            temperature=config['temperatura'],
            max_tokens=config['max_tokens']
        )
    except Exception as e:
        # Modo demonstração - respostas simuladas
        if tipo == 'chatbot_site':
            return "Olá! Sou a assistente virtual da Griffe da Prata. No momento estou em modo demonstração. Como posso ajudá-lo? Temos lindas joias de prata 925, brincos, colares, pulseiras e muito mais!"
        elif tipo == 'whatsapp':
            return "Oi! Aqui é a Griffe da Prata. Estamos prontos para te atender! 😊"
        elif tipo == 'dev_assistant':
            return "# Análise do Código\n\nO código está estruturado de forma adequada. Sugestões de melhorias serão fornecidas quando a API estiver ativa."
        else:
            return "Olá! Como posso ajudar você hoje?"

# ==========================================
# TESTE DA CONFIGURAÇÃO
# ==========================================

if __name__ == "__main__":
    print("🔧 Testando configuração do Grok...")
    print(f"API Key configurada: {'✅ Sim' if GROK_API_KEY else '❌ Não'}")
    print(f"Modelo: {MODELO_CHAT}")

    if testar_conexao_grok():
        print("✅ Conexão com Grok estabelecida!")

        # Teste rápido
        resposta = gerar_resposta_grok("Olá, teste do sistema!", 'chatbot_site')
        print(f"📝 Resposta de teste: {resposta[:100]}...")
    else:
        print("❌ Falha na conexão com Grok")
        print("📋 Para configurar:")
        print("1. Acesse: https://console.x.ai/")
        print("2. Crie uma conta gratuita")
        print("3. Gere uma API Key")
        print("4. Adicione GROK_API_KEY='sua-chave' no .env_config.py")