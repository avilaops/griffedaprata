"""
Script de Migração: Griffe da Prata → MarketplaceBuilder
Migra produtos do SQLite local para o Marketplace via API
"""

import sqlite3
import requests
import json
import urllib3
from datetime import datetime

# Desabilitar warnings SSL para desenvolvimento
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configurações - AJUSTAR APÓS CRIAR TENANT
CONFIG = {
    'marketplace_api': 'https://localhost:5001',
    'tenant_id': 'f5852246-a25a-4848-80cf-7637d0218177',  # ⚠️ IMPORTANTE: Substituir após criar tenant
    'sqlite_db': 'pedidos.db',
    'verify_ssl': False  # True em produção
}

class MarketplaceMigrator:
    def __init__(self):
        self.api_url = CONFIG['marketplace_api']
        self.tenant_id = CONFIG['tenant_id']
        self.headers = {
            'Content-Type': 'application/json',
            'X-Tenant-Id': self.tenant_id
        }
        self.migrados = 0
        self.erros = 0
        
    def conectar_sqlite(self):
        """Conecta ao banco SQLite local"""
        print(f"📂 Conectando ao banco {CONFIG['sqlite_db']}...")
        return sqlite3.connect(CONFIG['sqlite_db'])
    
    def obter_produtos_sqlite(self):
        """Lê todos os produtos do SQLite"""
        conn = self.conectar_sqlite()
        cursor = conn.cursor()
        
        cursor.execute("SELECT codigo, titulo, preco_atacado, preco_varejo, peso, lote, descricao, imagem_url FROM produtos")
        produtos = cursor.fetchall()
        conn.close()
        
        print(f"✅ Encontrados {len(produtos)} produtos no SQLite\n")
        return produtos
    
    def criar_categoria(self, nome):
        """Cria categoria no Marketplace (se não existir)"""
        try:
            # Verificar se categoria já existe
            response = requests.get(
                f"{self.api_url}/api/admin/categories",
                headers=self.headers,
                verify=CONFIG['verify_ssl']
            )
            
            if response.status_code == 200:
                categorias = response.json()
                for cat in categorias:
                    if cat.get('name') == nome:
                        return cat['id']
            
            # Criar nova categoria
            payload = {
                'name': nome,
                'slug': nome.lower().replace(' ', '-')
            }
            
            response = requests.post(
                f"{self.api_url}/api/admin/categories",
                json=payload,
                headers=self.headers,
                verify=CONFIG['verify_ssl']
            )
            
            if response.status_code in [200, 201]:
                return response.json().get('id')
            
        except Exception as e:
            print(f"⚠️ Erro ao criar categoria: {e}")
        
        return None
    
    def migrar_produto(self, produto):
        """Migra um produto para o Marketplace"""
        codigo, titulo, preco_atacado, preco_varejo, peso, lote, descricao, imagem_url = produto
        
        try:
            # Preparar dados do produto
            payload = {
                'title': titulo or f"Produto {codigo}",
                'slug': codigo.lower().replace('#', '').replace('-', ''),
                'description': descricao or f"Código: {codigo}\nPeso: {peso}g\nLote mínimo: {lote} unidades",
                'status': 'Active',
                'primaryImageUrl': imagem_url,
                'variants': [
                    {
                        'sku': codigo,
                        'title': 'Padrão',
                        'price': int(preco_varejo * 100),  # Converter para centavos
                        'compareAtPrice': None,
                        'costPrice': int(preco_atacado * 100) if preco_atacado else None,
                        'stock': 100,  # Estoque inicial padrão
                        'weight': peso,
                        'isDefault': True
                    }
                ]
            }
            
            # Criar produto via API
            response = requests.post(
                f"{self.api_url}/api/admin/products",
                json=payload,
                headers=self.headers,
                verify=CONFIG['verify_ssl']
            )
            
            if response.status_code in [200, 201]:
                self.migrados += 1
                print(f"✅ [{self.migrados}] {codigo} - {titulo[:40]}... | R$ {preco_varejo:.2f}")
                return True
            else:
                self.erros += 1
                print(f"❌ [{self.erros}] {codigo} - Erro {response.status_code}: {response.text[:100]}")
                return False
                
        except Exception as e:
            self.erros += 1
            print(f"❌ [{self.erros}] {codigo} - Exceção: {str(e)[:100]}")
            return False
    
    def validar_config(self):
        """Valida se as configurações estão corretas"""
        if self.tenant_id == 'SEU_TENANT_ID_AQUI' or not self.tenant_id:
            print("\n" + "="*70)
            print("⚠️  ATENÇÃO: TENANT ID NÃO CONFIGURADO!")
            print("="*70)
            print("\n📋 Passos necessários:")
            print("1. Suba o MarketplaceBuilder (API + Admin)")
            print("2. Acesse a UI Admin e crie o tenant 'Griffe da Prata'")
            print("3. Copie o Tenant ID (GUID) gerado")
            print("4. Edite este arquivo e cole o ID na variável CONFIG['tenant_id']")
            print("5. Execute novamente: python migrate_to_marketplace.py")
            print("="*70 + "\n")
            return False
        return True
    
    def testar_conexao(self):
        """Testa conexão com a API do Marketplace"""
        print("🔍 Testando conexão com API do Marketplace...")
        try:
            response = requests.get(
                f"{self.api_url}/health",
                verify=CONFIG['verify_ssl'],
                timeout=5
            )
            
            if response.status_code == 200:
                print("✅ API do Marketplace está respondendo!\n")
                return True
            else:
                print(f"⚠️ API respondeu com status {response.status_code}\n")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Não foi possível conectar à API do Marketplace")
            print("   Certifique-se de que está rodando em https://localhost:5001\n")
            return False
        except Exception as e:
            print(f"❌ Erro ao testar conexão: {e}\n")
            return False
    
    def executar_migracao(self):
        """Executa a migração completa"""
        print("\n" + "="*70)
        print("🚀 MIGRAÇÃO: GRIFFE DA PRATA → MARKETPLACEBUILDER")
        print("="*70 + "\n")
        
        # Validações
        if not self.validar_config():
            return
        
        if not self.testar_conexao():
            return
        
        # Obter produtos
        produtos = self.obter_produtos_sqlite()
        
        if not produtos:
            print("❌ Nenhum produto encontrado no SQLite!")
            return
        
        # Confirmar migração
        print(f"📦 Pronto para migrar {len(produtos)} produtos")
        confirma = 's'  # Auto-confirmar para automação
        
        if confirma != 's':
            print("❌ Migração cancelada pelo usuário")
            return
        
        print("\n🔄 Iniciando migração...\n")
        inicio = datetime.now()
        
        # Migrar cada produto
        for i, produto in enumerate(produtos, 1):
            self.migrar_produto(produto)
        
        # Relatório final
        duracao = (datetime.now() - inicio).total_seconds()
        print("\n" + "="*70)
        print("📊 RELATÓRIO DE MIGRAÇÃO")
        print("="*70)
        print(f"✅ Migrados com sucesso: {self.migrados}")
        print(f"❌ Erros: {self.erros}")
        print(f"📦 Total processado: {len(produtos)}")
        print(f"⏱️  Tempo decorrido: {duracao:.2f}s")
        print(f"🎯 Taxa de sucesso: {(self.migrados/len(produtos)*100):.1f}%")
        print("="*70 + "\n")
        
        if self.migrados > 0:
            print("🎉 Migração concluída! Seus produtos estão no MarketplaceBuilder!")
            print(f"🔗 Acesse: {self.api_url.replace('5001', '5003')}/griffedaprata\n")

if __name__ == '__main__':
    migrator = MarketplaceMigrator()
    migrator.executar_migracao()
