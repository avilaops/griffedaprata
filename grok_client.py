"""
Cliente personalizado para Grok (xAI)
Usa a API REST diretamente via requests
"""

import requests
import json
import os
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class GrokClient:
    """Cliente para interagir com a API do Grok (xAI)"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o cliente Grok

        Args:
            api_key: Chave da API do Grok. Se None, tenta buscar de GROK_API_KEY
        """
        self.api_key = api_key or os.getenv('GROK_API_KEY')
        self.demo_mode = not self.api_key or self.api_key == 'demo'
        
        if not self.demo_mode:
            # URL base da API do Grok (xAI)
            self.base_url = "https://api.x.ai/v1"

            # Headers padrão
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

    def chat_completion(self,
                       messages: List[Dict[str, str]],
                       model: str = "grok-beta",
                       temperature: float = 0.7,
                       max_tokens: int = 1000,
                       **kwargs) -> Dict[str, Any]:
        """
        Faz uma requisição de chat completion para o Grok

        Args:
            messages: Lista de mensagens no formato [{"role": "user", "content": "texto"}]
            model: Modelo a usar (padrão: grok-beta)
            temperature: Temperatura da resposta (0.0 a 1.0)
            max_tokens: Máximo de tokens na resposta
            **kwargs: Outros parâmetros

        Returns:
            Resposta da API em formato similar ao OpenAI
        """
        payload = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                # Normalizar resposta para formato similar ao OpenAI
                return {
                    "choices": [{
                        "message": {
                            "content": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                            "role": "assistant"
                        },
                        "finish_reason": data.get("choices", [{}])[0].get("finish_reason", "stop")
                    }],
                    "usage": data.get("usage", {}),
                    "model": data.get("model", model)
                }
            else:
                error_msg = f"Erro na API Grok: {response.status_code} - {response.text}"
                raise Exception(error_msg)

        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro de conexão com Grok API: {str(e)}")

    def generate_response(self,
                         prompt: str,
                         system_prompt: Optional[str] = None,
                         temperature: float = 0.7,
                         max_tokens: int = 1000) -> str:
        """
        Método simplificado para gerar resposta

        Args:
            prompt: Prompt do usuário
            system_prompt: Prompt do sistema (opcional)
            temperature: Temperatura
            max_tokens: Máximo de tokens

        Returns:
            Resposta do Grok
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response["choices"][0]["message"]["content"].strip()

# Função de compatibilidade para substituir OpenAI
def create_grok_client(api_key: Optional[str] = None) -> GrokClient:
    """Cria e retorna um cliente Grok"""
    return GrokClient(api_key)

# Teste rápido da API
def test_grok_connection(api_key: Optional[str] = None) -> bool:
    """
    Testa a conexão com a API do Grok

    Returns:
        True se conexão OK, False caso contrário
    """
    try:
        client = GrokClient(api_key)
        response = client.generate_response(
            "Olá, você é o Grok?",
            temperature=0.1,
            max_tokens=50
        )
        return "Grok" in response or "xAI" in response
    except Exception as e:
        print(f"Erro no teste do Grok: {e}")
        return False

if __name__ == "__main__":
    # Teste do módulo
    print("Testando conexão com Grok...")
    if test_grok_connection():
        print("✅ Conexão com Grok estabelecida!")
    else:
        print("❌ Falha na conexão com Grok")