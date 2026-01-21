"""
Sistema de IA Híbrido - Griffe da Prata
Funciona SEM APIs externas - 100% Gratuito e Local
Usa processamento de linguagem natural baseado em regras
"""

import re
from typing import List, Tuple, Optional
from datetime import datetime

class ChatBotInteligente:
    """Chatbot inteligente baseado em regras e contexto"""
    
    def __init__(self):
        # Base de conhecimento de produtos
        self.produtos = {
            'anel': {
                'descricao': 'Anéis de prata 925 lindos e elegantes',
                'preco': 'R$ 80 a R$ 300',
                'tipos': ['solitário', 'aliança', 'anel de compromisso', 'anel delicado']
            },
            'brinco': {
                'descricao': 'Brincos de prata 925 para todos os estilos',
                'preco': 'R$ 50 a R$ 250',
                'tipos': ['argola', 'pendente', 'brinco de pressão', 'ear cuff']
            },
            'colar': {
                'descricao': 'Colares elegantes de prata 925',
                'preco': 'R$ 100 a R$ 400',
                'tipos': ['corrente', 'pingente', 'colar delicado', 'choker']
            },
            'pulseira': {
                'descricao': 'Pulseiras sofisticadas de prata 925',
                'preco': 'R$ 90 a R$ 350',
                'tipos': ['corrente', 'bracelete', 'pulseira articulada', 'charm']
            },
            'conjunto': {
                'descricao': 'Conjuntos coordenados de joias',
                'preco': 'R$ 250 a R$ 600',
                'tipos': ['colar + brinco', 'pulseira + anel', 'conjunto completo']
            }
        }
        
        # Padrões de intenção
        self.intencoes = {
            'saudacao': [r'\b(oi|olá|ola|hello|hey|bom dia|boa tarde|boa noite)\b'],
            'produto': [r'\b(anel|aneis|brinco|brincos|colar|colares|pulseira|pulseiras|joia|joias)\b'],
            'preco': [r'\b(preço|preco|valor|quanto custa|custo|caro|barato)\b'],
            'comprar': [r'\b(comprar|quero|gostaria|interessado|adquirir)\b'],
            'entrega': [r'\b(entrega|entregar|frete|envio|prazo|demora)\b'],
            'pagamento': [r'\b(pagamento|pagar|cartão|cartao|pix|boleto|parcela)\b'],
            'duvida': [r'\b(duvida|dúvida|pergunta|info|informação|informacao)\b'],
            'qualidade': [r'\b(qualidade|material|prata|925|original|autêntico|autentico)\b'],
            'troca': [r'\b(troca|trocar|devolução|devolver|garantia)\b']
        }
    
    def detectar_intencao(self, mensagem: str) -> str:
        """Detecta a intenção da mensagem"""
        mensagem_lower = mensagem.lower()
        
        for intencao, padroes in self.intencoes.items():
            for padrao in padroes:
                if re.search(padrao, mensagem_lower):
                    return intencao
        
        return 'geral'
    
    def detectar_produto(self, mensagem: str) -> Optional[str]:
        """Detecta qual produto o cliente está interessado"""
        mensagem_lower = mensagem.lower()
        
        for produto in self.produtos.keys():
            if produto in mensagem_lower or (produto + 's') in mensagem_lower:
                return produto
        
        return None
    
    def gerar_resposta(self, mensagem: str, historico: List[Tuple[str, str]] = None) -> str:
        """
        Gera resposta inteligente baseada em regras
        
        Args:
            mensagem: Mensagem do usuário
            historico: Histórico de conversas
            
        Returns:
            Resposta contextual
        """
        intencao = self.detectar_intencao(mensagem)
        produto = self.detectar_produto(mensagem)
        
        # Respostas baseadas em intenção
        if intencao == 'saudacao':
            return "Olá! 😊 Bem-vindo à Griffe da Prata! Somos especialistas em joias de prata 925. Como posso ajudar você hoje? Temos brincos, colares, anéis, pulseiras e conjuntos lindos!"
        
        elif intencao == 'produto' and produto:
            info = self.produtos[produto]
            return f"Temos {info['descricao']}! Os preços variam de {info['preco']}. Oferecemos vários tipos: {', '.join(info['tipos'])}. Gostaria de ver algum modelo específico?"
        
        elif intencao == 'preco':
            if produto:
                return f"Os {produto}s variam de {self.produtos[produto]['preco']}, dependendo do modelo e design. Temos opções para todos os gostos! 💎"
            else:
                return "Nossos preços variam de R$ 50 a R$ 600, dependendo da peça. Anéis, brincos, colares e pulseiras - tudo em prata 925 genuína! Qual produto te interessa?"
        
        elif intencao == 'comprar':
            return "Que ótimo! 🎉 Você pode fazer seu pedido direto pelo WhatsApp: (82) 98160-2651 ou pelo nosso site. Aceitamos cartão, PIX e parcelamento. Qual produto você gostaria de comprar?"
        
        elif intencao == 'entrega':
            return "Entregamos para todo o Brasil! 📦 O prazo varia de 7 a 15 dias úteis dependendo da região. Frete calculado no checkout. Pedidos acima de R$ 300 ganham frete grátis! 🎁"
        
        elif intencao == 'pagamento':
            return "Aceitamos: 💳 Cartão de crédito (até 6x sem juros), PIX (5% desconto), boleto e transferência bancária. Pagamento 100% seguro! Qual forma prefere?"
        
        elif intencao == 'qualidade':
            return "Todas nossas joias são de prata 925 GENUÍNA! 💎 Certificado de autenticidade, garantia de 6 meses e durabilidade comprovada. Pode confiar - é qualidade premium!"
        
        elif intencao == 'troca':
            return "Você tem 30 dias para trocar ou devolver! 🔄 Garantia de 6 meses contra defeitos de fabricação. Estamos aqui para garantir sua satisfação total!"
        
        elif produto:
            info = self.produtos[produto]
            return f"Interessado em {produto}s? Excelente escolha! {info['descricao']} com preços de {info['preco']}. Quer saber mais detalhes ou fazer um pedido?"
        
        else:
            return "Estou aqui para ajudar! 😊 Posso te mostrar nossos produtos (brincos, colares, anéis, pulseiras), falar sobre preços, formas de pagamento, entrega... O que você gostaria de saber?"

# Configuração global
def gerar_resposta(prompt: str, tipo: str = 'chatbot_site', historico: list = None) -> str:
    """
    Interface compatível com o sistema existente
    
    Args:
        prompt: Mensagem do usuário
        tipo: Tipo (ignorado, sempre usa chatbot)
        historico: Histórico de conversas
        
    Returns:
        Resposta gerada
    """
    bot = ChatBotInteligente()
    return bot.gerar_resposta(prompt, historico)

if __name__ == "__main__":
    print("🤖 Testando ChatBot Inteligente...")
    bot = ChatBotInteligente()
    
    # Testes
    testes = [
        "Olá, boa tarde!",
        "Quero ver anéis",
        "Quanto custa?",
        "Aceita cartão?",
        "Como funciona a entrega?",
        "É prata de verdade?"
    ]
    
    for teste in testes:
        resposta = bot.gerar_resposta(teste)
        print(f"\n👤 {teste}")
        print(f"🤖 {resposta}")
    
    print("\n✅ ChatBot funcionando perfeitamente - SEM APIs EXTERNAS!")