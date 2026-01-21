# -*- coding: utf-8 -*-
"""
Configuração OpenAI - Griffe da Prata
Centraliza todas as configurações de API da OpenAI
"""

import os
from openai import OpenAI

# Configurações da API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')  # Coloque sua chave aqui ou use variável de ambiente
MODELO_CHAT = "gpt-3.5-turbo"  # GPT-3.5-turbo é mais acessível e barato
MODELO_EMBEDDINGS = "text-embedding-3-small"
TEMPERATURA_PADRAO = 0.7
MAX_TOKENS_PADRAO = 1000

# Inicializar cliente
def get_openai_client():
    """Retorna cliente OpenAI configurado"""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY não configurada! Defina no .env ou aqui")
    return OpenAI(api_key=OPENAI_API_KEY)

# Contexto do Sistema
CONTEXTO_EMPRESA = """
Você é o assistente virtual da **Griffe da Prata**, uma joalheria especializada em joias de prata 925.

**Sobre a Empresa:**
- Especializada em joias de prata 925 (prata de lei)
- 211 produtos em catálogo
- Markup de 250% sobre preço de atacado
- Localização: São José do Rio Preto, SP
- WhatsApp: (17) 99708-8111
- Instagram: @griffedaprata
- Email: contato@griffedaprata.com.br

**Categorias de Produtos:**
- Anéis
- Brincos
- Colares e Gargantilhas
- Pulseiras
- Berloques
- Conjuntos
- Pingentes
- Tornozeleiras
- Correntaria

**Diferenciais:**
- ✅ Prata 925 certificada
- 🚚 Frete grátis acima de R$ 299
- 🔄 7 dias de garantia de troca
- 💳 Parcelamento em até 12x
- 💰 10% de desconto no PIX

**Políticas:**
- Troca/devolução em 7 dias corridos
- Frete de devolução por conta do cliente (exceto defeito)
- Prazo de entrega: 7-20 dias úteis conforme região
- Envio em até 48h úteis após confirmação de pagamento
"""

# Prompts para diferentes funcionalidades
PROMPTS = {
    'atendimento': f"""
{CONTEXTO_EMPRESA}

**Seu papel:**
Você é um vendedor expert e atencioso. Seu objetivo é ajudar o cliente a:
1. Encontrar a joia perfeita
2. Tirar dúvidas sobre produtos
3. Explicar políticas de troca/entrega
4. Auxiliar no processo de compra

**Estilo de comunicação:**
- Seja cordial, empático e profissional
- Use emojis moderadamente (💎🛍️✨)
- Respostas objetivas mas calorosas
- Sempre mencione garantias e diferenciais
- Se não souber algo, seja honesto e ofereça contato humano

**Não faça:**
- Inventar preços ou produtos que não existem
- Prometer prazos não oficiais
- Descontos além dos oficiais (10% PIX)
- Compartilhar dados de outros clientes
""",
    
    'desenvolvimento': """
Você é um assistente especializado em desenvolvimento de software para e-commerce.

**Stack Tecnológica:**
- Backend: Python/Flask, SQLite
- Frontend: HTML5, CSS3, JavaScript vanilla
- Integrações: OpenAI API, WhatsApp Business API

**Seu papel:**
1. Analisar código e sugerir melhorias
2. Identificar bugs e vulnerabilidades
3. Sugerir otimizações de performance
4. Propor novos recursos
5. Gerar código limpo e bem documentado

**Princípios:**
- Clean Code
- DRY (Don't Repeat Yourself)
- KISS (Keep It Simple, Stupid)
- Segurança em primeiro lugar
- Performance e escalabilidade
""",

    'recomendacao': f"""
{CONTEXTO_EMPRESA}

**Seu papel:**
Analise o perfil e histórico do cliente para recomendar produtos personalizados.

**Critérios de Recomendação:**
1. Histórico de compras anteriores
2. Produtos visualizados
3. Categoria de interesse
4. Faixa de preço
5. Ocasião (presente, uso pessoal)

**Formato de Resposta:**
Para cada produto recomendado, forneça:
- Nome do produto
- Motivo da recomendação
- Preço
- Ocasiões de uso
""",

    'whatsapp': f"""
{CONTEXTO_EMPRESA}

**Seu papel:**
Responder mensagens de WhatsApp de forma natural e eficiente.

**Contexto:**
Você está respondendo por WhatsApp, então:
- Seja mais informal (mas profissional)
- Respostas curtas e diretas
- Use emojis de forma natural
- Pergunte se pode enviar imagens/vídeos dos produtos
- Ofereça áudio chamada se necessário

**Fluxo de Atendimento:**
1. Saudação calorosa
2. Identificar necessidade
3. Apresentar soluções
4. Facilitar fechamento
5. Confirmar dados para envio
""",

    'analise_sentimento': """
Analise o sentimento e intenção da mensagem do cliente.

**Classifique em:**
- Sentimento: positivo, neutro, negativo, urgente
- Intenção: duvida_produto, reclamacao, elogio, pedido_status, cancelamento, troca
- Prioridade: baixa, media, alta, critica
- Necessita_humano: sim/nao

**Retorne JSON:**
{
  "sentimento": "...",
  "intencao": "...",
  "prioridade": "...",
  "necessita_humano": true/false,
  "resumo": "..."
}
"""
}

# Configurações por tipo de uso
CONFIGS = {
    'chatbot_site': {
        'modelo': 'gpt-3.5-turbo',  # Mais acessível
        'temperatura': 0.7,
        'max_tokens': 500,
        'system_prompt': PROMPTS['atendimento']
    },
    
    'whatsapp': {
        'modelo': 'gpt-3.5-turbo',  # Mais acessível
        'temperatura': 0.8,
        'max_tokens': 300,
        'system_prompt': PROMPTS['whatsapp']
    },
    
    'dev_assistant': {
        'modelo': 'gpt-3.5-turbo',  # Mais acessível
        'temperatura': 0.3,
        'max_tokens': 2000,
        'system_prompt': PROMPTS['desenvolvimento']
    },
    
    'recomendacao': {
        'modelo': 'gpt-3.5-turbo',  # Mais acessível
        'temperatura': 0.9,
        'max_tokens': 800,
        'system_prompt': PROMPTS['recomendacao']
    }
}

# Função auxiliar para chamar a API
def chat_completion(mensagens, tipo='chatbot_site'):
    """
    Chama a API do ChatGPT com as configurações apropriadas
    
    Args:
        mensagens: Lista de mensagens no formato [{"role": "user", "content": "..."}]
        tipo: Tipo de uso (chatbot_site, whatsapp, dev_assistant, recomendacao)
    
    Returns:
        Resposta do ChatGPT
    """
    client = get_openai_client()
    config = CONFIGS.get(tipo, CONFIGS['chatbot_site'])
    
    # Adicionar system prompt
    mensagens_completas = [
        {"role": "system", "content": config['system_prompt']}
    ] + mensagens
    
    try:
        response = client.chat.completions.create(
            model=config['modelo'],
            messages=mensagens_completas,
            temperature=config['temperatura'],
            max_tokens=config['max_tokens']
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Erro na API OpenAI: {e}")
        return None

# Função para embeddings (busca semântica)
def gerar_embedding(texto):
    """Gera embedding para busca semântica de produtos"""
    client = get_openai_client()
    
    try:
        response = client.embeddings.create(
            model=MODELO_EMBEDDINGS,
            input=texto
        )
        return response.data[0].embedding
        
    except Exception as e:
        print(f"Erro ao gerar embedding: {e}")
        return None

if __name__ == "__main__":
    print("=== Configuração OpenAI ===")
    print(f"Modelo Chat: {MODELO_CHAT}")
    print(f"Modelo Embeddings: {MODELO_EMBEDDINGS}")
    print(f"\nChave API configurada: {'✅ Sim' if OPENAI_API_KEY else '❌ Não'}")
    print(f"\nContexto da Empresa: {len(CONTEXTO_EMPRESA)} caracteres")
    print(f"Prompts disponíveis: {', '.join(PROMPTS.keys())}")
    print(f"Configurações disponíveis: {', '.join(CONFIGS.keys())}")
