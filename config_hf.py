"""
Configuração do sistema de IA usando Hugging Face
100% GRATUITO - Sem custos!
"""

import os
from dotenv import load_dotenv
from hf_client import HuggingFaceClient

load_dotenv()

# Token Hugging Face
HF_TOKEN = os.getenv('HF_TOKEN', '')

# Prompts contextuais
PROMPTS = {
    'atendimento': """Você é assistente de vendas da Griffe da Prata, joalheria de prata 925.
Seja simpático, profissional e ajude o cliente com informações sobre joias.
Produtos: brincos, colares, pulseiras, anéis. Preços: R$ 50-500.
Seja breve e direto.""",

    'whatsapp': """Assistente WhatsApp da Griffe da Prata.
Respostas curtas (máx 3 linhas). Use emojis. Seja amigável.""",

    'dev_assistant': """Assistente de desenvolvimento.
Analise código, sugira melhorias, identifique bugs.""",

    'recomendacao': """Sistema de recomendação de joias.
Sugira produtos baseado no perfil e ocasião do cliente."""
}

CONFIGS = {
    'chatbot_site': {
        'model': 'chat',
        'temperatura': 0.7,
        'max_tokens': 400,
        'system_prompt': PROMPTS['atendimento']
    },
    'whatsapp': {
        'model': 'fast',
        'temperatura': 0.8,
        'max_tokens': 200,
        'system_prompt': PROMPTS['whatsapp']
    },
    'dev_assistant': {
        'model': 'chat',
        'temperatura': 0.3,
        'max_tokens': 1000,
        'system_prompt': PROMPTS['dev_assistant']
    },
    'recomendacao': {
        'model': 'chat',
        'temperatura': 0.9,
        'max_tokens': 600,
        'system_prompt': PROMPTS['recomendacao']
    }
}

def get_hf_client() -> HuggingFaceClient:
    """Retorna cliente Hugging Face configurado"""
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN não configurado no .env")
    return HuggingFaceClient(HF_TOKEN)

def gerar_resposta(prompt: str, tipo: str = 'chatbot_site', historico: list = None) -> str:
    """
    Gera resposta usando Hugging Face
    
    Args:
        prompt: Mensagem do usuário
        tipo: Tipo de configuração
        historico: Histórico de conversas
        
    Returns:
        Resposta gerada
    """
    try:
        client = get_hf_client()
        config = CONFIGS.get(tipo, CONFIGS['chatbot_site'])
        
        return client.chat(
            mensagem=prompt,
            system_prompt=config['system_prompt'],
            historico=historico,
            max_tokens=config['max_tokens']
        )
    except Exception as e:
        # Fallback
        if tipo == 'chatbot_site':
            return "Olá! Sou da Griffe da Prata. Como posso ajudar você?"
        elif tipo == 'whatsapp':
            return "Oi! 😊 Como posso te ajudar?"
        else:
            return f"Sistema temporariamente indisponível: {str(e)}"

if __name__ == "__main__":
    print("🧪 Testando configuração Hugging Face...")
    print(f"Token configurado: {'✅ Sim' if HF_TOKEN else '❌ Não'}")
    
    if HF_TOKEN:
        resposta = gerar_resposta("Olá, gostaria de ver anéis", 'chatbot_site')
        print(f"📝 Teste: {resposta[:100]}...")
        print("✅ Sistema pronto!")
    else:
        print("❌ Configure HF_TOKEN no .env")
