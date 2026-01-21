"""
Sincronizador Automático: Scraper → MarketplaceBuilder
Atualiza produtos no Marketplace após cada execução do scraper
"""

import requests
import json
import sqlite3
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configurações - USAR AS MESMAS DO migrate_to_marketplace.py
CONFIG = {
    'marketplace_api': 'https://localhost:5001',
    'tenant_id': 'f5852246-a25a-4848-80cf-7637d0218177',
    'sqlite_db': 'pedidos.db',
    'verify_ssl': False
}

class MarketplaceSyncer:
    def __init__(self):
        self.api_url = CONFIG['marketplace_api']
        self.tenant_id = CONFIG['tenant_id']
        self.headers = {
            'Content-Type': 'application/json',
            'X-Tenant-Id': self.tenant_id
        }
        self.atualizados = 0
        self.criados = 0
        self.erros = 0
    
    def obter_produtos_sqlite(self):
        """Lê produtos do banco local"""
        conn = sqlite3.connect(CONFIG['sqlite_db'])
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, titulo, preco_atacado, preco_varejo, imagem_url FROM produtos")
        produtos = cursor.fetchall()
        conn.close()
        return produtos
    
    def buscar_produto_por_sku(self, sku):
        """Busca produto no Marketplace pelo SKU"""
        try:
            response = requests.get(
                f"{self.api_url}/api/admin/products/by-sku/{sku}",
                headers=self.headers,
                verify=CONFIG['verify_ssl']
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"⚠️ Erro ao buscar {sku}: {e}")
            return None
    
    def atualizar_produto(self, product_id, codigo, preco_varejo):
        """Atualiza preço de um produto existente"""
        try:
            # Buscar variantes do produto
            response = requests.get(
                f"{self.api_url}/api/admin/products/{product_id}/variants",
                headers=self.headers,
                verify=CONFIG['verify_ssl']
            )
            
            if response.status_code != 200:
                return False
            
            variants = response.json()
            
            # Atualizar preço da primeira variante (padrão)
            if variants and len(variants) > 0:
                variant_id = variants[0]['id']
                
                payload = {
                    'price': int(preco_varejo * 100)
                }
                
                response = requests.patch(
                    f"{self.api_url}/api/admin/products/{product_id}/variants/{variant_id}",
                    json=payload,
                    headers=self.headers,
                    verify=CONFIG['verify_ssl']
                )
                
                if response.status_code in [200, 204]:
                    self.atualizados += 1
                    print(f"🔄 {codigo} - Preço atualizado: R$ {preco_varejo:.2f}")
                    return True
            
            return False
            
        except Exception as e:
            self.erros += 1
            print(f"❌ {codigo} - Erro ao atualizar: {e}")
            return False
    
    def criar_produto(self, produto):
        """Cria novo produto no Marketplace"""
        codigo, titulo, preco_atacado, preco_varejo, imagem_url = produto
        
        try:
            payload = {
                'title': titulo or f"Produto {codigo}",
                'slug': codigo.lower().replace('#', '').replace('-', ''),
                'description': f"Código: {codigo}",
                'status': 'Active',
                'primaryImageUrl': imagem_url,
                'variants': [{
                    'sku': codigo,
                    'title': 'Padrão',
                    'price': int(preco_varejo * 100),
                    'costPrice': int(preco_atacado * 100) if preco_atacado else None,
                    'stock': 100,
                    'isDefault': True
                }]
            }
            
            response = requests.post(
                f"{self.api_url}/api/admin/products",
                json=payload,
                headers=self.headers,
                verify=CONFIG['verify_ssl']
            )
            
            if response.status_code in [200, 201]:
                self.criados += 1
                print(f"✨ {codigo} - Novo produto criado: R$ {preco_varejo:.2f}")
                return True
            else:
                self.erros += 1
                print(f"❌ {codigo} - Erro ao criar: {response.status_code}")
                return False
                
        except Exception as e:
            self.erros += 1
            print(f"❌ {codigo} - Exceção: {e}")
            return False
    
    def sincronizar(self):
        """Sincroniza todos os produtos"""
        print("\n" + "="*70)
        print("🔄 SINCRONIZAÇÃO: SQLite → MarketplaceBuilder")
        print("="*70 + "\n")
        
        produtos = self.obter_produtos_sqlite()
        print(f"📦 Encontrados {len(produtos)} produtos no SQLite\n")
        
        inicio = datetime.now()
        
        for produto in produtos:
            codigo = produto[0]
            preco_varejo = produto[3]
            
            # Verificar se produto existe
            produto_existente = self.buscar_produto_por_sku(codigo)
            
            if produto_existente:
                # Atualizar preço
                product_id = produto_existente['id']
                self.atualizar_produto(product_id, codigo, preco_varejo)
            else:
                # Criar novo
                self.criar_produto(produto)
        
        # Relatório
        duracao = (datetime.now() - inicio).total_seconds()
        print("\n" + "="*70)
        print("📊 RELATÓRIO DE SINCRONIZAÇÃO")
        print("="*70)
        print(f"✨ Novos criados: {self.criados}")
        print(f"🔄 Atualizados: {self.atualizados}")
        print(f"❌ Erros: {self.erros}")
        print(f"⏱️  Tempo: {duracao:.2f}s")
        print("="*70 + "\n")

if __name__ == '__main__':
    syncer = MarketplaceSyncer()
    syncer.sincronizar()
