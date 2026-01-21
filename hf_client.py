"""
Cliente para Hugging Face Inference API
100% GRATUITO - Sem limites de uso!
"""

import os
from huggingface_hub import InferenceClient
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class HuggingFaceClient:
    """Cliente para usar modelos gratuitos do Hugging Face"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o cliente Hugging Face
        
        Args:
            api_key: Token do HF. Se None, busca de HF_TOKEN
        """
        self.api_key = api_key or os.getenv('HF_TOKEN')
        if not self.api_key:
            raise ValueError("HF_TOKEN não encontrado no .env")
        
        # Cliente oficial do HF
        self.client = InferenceClient(token=self.api_key)
        
        # Modelo padrão - Mistral 7B (gratuito via Serverless)
        self.model = "mistralai/Mistral-7B-Instruct-v0.1"
    
    def chat(self,
            mensagem: str,
            system_prompt: Optional[str] = None,
            historico: list = None,
            max_tokens: int = 500) -> str:
        """
        Chat conversacional
        
        Args:
            mensagem: Mensagem do usuário
            system_prompt: Instruções do sistema
            historico: Histórico de conversas
            max_tokens: Máximo de tokens
            
        Returns:
            Resposta do bot
        """
        try:
            # Montar mensagens
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            if historico:
                for h in historico[-3:]:  # Últimas 3
                    messages.append({"role": "user", "content": h[0]})
                    messages.append({"role": "assistant", "content": h[1]})
            
            messages.append({"role": "user", "content": mensagem})
            
            # Gerar resposta usando chat_completion sem modelo específico
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"⚠️ Erro na geração: {e}")
            return f"Desculpe, tive um problema técnico. Por favor, entre em contato: (82) 98160-2651"

def test_hf():
    """Testa conexão com Hugging Face"""
    try:
        client = HuggingFaceClient()
        print("Cliente criado com sucesso!")
        resposta = client.chat("Diga olá em uma palavra")
        print(f"Resposta: {resposta}")
        return len(resposta) > 0
    except Exception as e:
        print(f"Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testando Hugging Face...")
    if test_hf():
        print("✅ Hugging Face funcionando!")
    else:
        print("❌ Erro no Hugging Face")
