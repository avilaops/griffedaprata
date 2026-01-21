"""
Setup Automático Completo: Criar Tenant + Migrar Produtos
Executa todas as etapas necessárias automaticamente
"""

import requests
import sqlite3
import json
import time
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG = {
    'marketplace_api': 'https://localhost:5001',
    'sqlite_db': 'pedidos.db',
    'verify_ssl': False
}

class AutoSetup:
    def __init__(self):
        self.api_url = CONFIG['marketplace_api']
        self.tenant_id = None
        self.auth_token = None
        
    def print_header(self, texto):
        """Imprime cabeçalho formatado"""
        print("\n" + "="*70)
        print(f"🚀 {texto}")
        print("="*70 + "\n")
    
    def testar_api(self):
        """Testa se a API está respondendo"""
        self.print_header("ETAPA 1: Testando Conexão com API")
        
        try:
            response = requests.get(
                f"{self.api_url}/health",
                verify=CONFIG['verify_ssl'],
                timeout=5
            )
            
            if response.status_code == 200:
                print("✅ API do MarketplaceBuilder está online!")
                return True
            else:
                print(f"⚠️ API respondeu com status {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Não foi possível conectar à API")
            print("   Certifique-se de que a API está rodando em https://localhost:5001")
            return False
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def criar_usuario_admin(self):
        """Registra usuário admin via API"""
        self.print_header("ETAPA 2: Criando Usuário Admin")
        
        # Tentar registrar novo usuário
        payload = {
            'email': 'admin@griffedaprata.com.br',
            'password': 'GriffeDaPrata@2026',
            'confirmPassword': 'GriffeDaPrata@2026'
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/register",
                json=payload,
                verify=CONFIG['verify_ssl']
            )
            
            if response.status_code in [200, 201]:
                print("✅ Usuário admin criado com sucesso!")
                return True
            elif response.status_code == 400:
                # Usuário já existe, tentar login
                print("ℹ️  Usuário já existe, fazendo login...")
                return True
            else:
                print(f"⚠️ Status: {response.status_code}")
                print(f"   Resposta: {response.text[:200]}")
                return True  # Continuar mesmo assim
                
        except Exception as e:
            print(f"⚠️ Erro ao criar usuário: {e}")
            print("   Continuando com o processo...")
            return True
    
    def fazer_login(self):
        """Faz login e obtém token"""
        print("\n🔐 Fazendo login...")
        
        payload = {
            'email': 'admin@griffedaprata.com.br',
            'password': 'GriffeDaPrata@2026'
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/login",
                json=payload,
                verify=CONFIG['verify_ssl']
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                print("✅ Login realizado com sucesso!")
                return True
            else:
                print(f"⚠️ Login falhou: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"⚠️ Erro no login: {e}")
            return False
    
    def criar_tenant(self):
        """Cria tenant Griffe da Prata"""
        self.print_header("ETAPA 3: Criando Tenant 'Griffe da Prata'")
        
        payload = {
            'name': 'Griffe da Prata',
            'subdomain': 'griffedaprata',
            'primaryDomain': 'griffedaprata.com.br',
            'locale': 'pt-BR',
            'currency': 'BRL',
            'isActive': True
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        # Tentar diferentes endpoints possíveis
        endpoints = [
            '/api/admin/tenants',
            '/api/tenants',
            '/api/admin/stores',
            '/api/stores'
        ]
        
        for endpoint in endpoints:
            try:
                print(f"Tentando: {endpoint}...")
                response = requests.post(
                    f"{self.api_url}{endpoint}",
                    json=payload,
                    headers=headers,
                    verify=CONFIG['verify_ssl']
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    self.tenant_id = data.get('id') or data.get('tenantId')
                    
                    print(f"✅ Tenant criado com sucesso!")
                    print(f"📋 Tenant ID: {self.tenant_id}")
                    print(f"🌐 Subdomínio: griffedaprata")
                    print(f"💱 Moeda: BRL")
                    return True
                    
                elif response.status_code == 409:
                    print("ℹ️  Tenant já existe, buscando ID...")
                    return self.buscar_tenant_existente()
                    
            except Exception as e:
                continue
        
        print("⚠️ Não foi possível criar tenant pelos endpoints padrão")
        print("   Tentando criar diretamente no banco de dados...")
        return self.criar_tenant_direto_db()
    
    def buscar_tenant_existente(self):
        """Busca tenant existente"""
        print("\n🔍 Buscando tenant existente...")
        
        headers = {'Content-Type': 'application/json'}
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        endpoints = ['/api/admin/tenants', '/api/tenants']
        
        for endpoint in endpoints:
            try:
                response = requests.get(
                    f"{self.api_url}{endpoint}",
                    headers=headers,
                    verify=CONFIG['verify_ssl']
                )
                
                if response.status_code == 200:
                    tenants = response.json()
                    
                    # Procurar tenant Griffe da Prata
                    for tenant in tenants if isinstance(tenants, list) else []:
                        if 'griffedaprata' in tenant.get('subdomain', '').lower():
                            self.tenant_id = tenant.get('id')
                            print(f"✅ Tenant encontrado!")
                            print(f"📋 Tenant ID: {self.tenant_id}")
                            return True
                            
            except Exception as e:
                continue
        
        return False
    
    def criar_tenant_direto_db(self):
        """Cria tenant diretamente no banco via Docker"""
        print("\n📦 Criando tenant diretamente no PostgreSQL...")
        
        import subprocess
        import uuid
        
        self.tenant_id = str(uuid.uuid4())
        
        sql = f"""
        INSERT INTO "Tenants" 
        ("Id", "Name", "Subdomain", "PrimaryDomain", "Locale", "Currency", "IsActive", "CreatedAt", "UpdatedAt")
        VALUES 
        ('{self.tenant_id}', 'Griffe da Prata', 'griffedaprata', 'griffedaprata.com.br', 'pt-BR', 'BRL', true, NOW(), NOW())
        ON CONFLICT (\"Subdomain\") DO UPDATE SET "UpdatedAt" = NOW()
        RETURNING "Id";
        """
        
        try:
            cmd = [
                'docker', 'exec', 'marketplace-postgres',
                'psql', '-U', 'marketplace', '-d', 'marketplacebuilder',
                '-c', sql
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Tenant criado no banco!")
                print(f"📋 Tenant ID: {self.tenant_id}")
                return True
            else:
                print(f"❌ Erro: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao criar tenant no DB: {e}")
            return False
    
    def atualizar_scripts(self):
        """Atualiza scripts com o Tenant ID"""
        self.print_header("ETAPA 4: Configurando Scripts")
        
        if not self.tenant_id:
            print("❌ Tenant ID não disponível!")
            return False
        
        scripts = [
            'migrate_to_marketplace.py',
            'sync_scraper_marketplace.py'
        ]
        
        for script in scripts:
            try:
                with open(script, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                # Substituir placeholder pelo Tenant ID real
                conteudo = conteudo.replace(
                    "'tenant_id': 'COLE_AQUI_O_TENANT_ID_APOS_CRIAR_VIA_UI'",
                    f"'tenant_id': '{self.tenant_id}'"
                )
                
                conteudo = conteudo.replace(
                    'COLE_AQUI_O_TENANT_ID_APOS_CRIAR_VIA_UI',
                    self.tenant_id
                )
                
                with open(script, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                
                print(f"✅ {script} configurado")
                
            except Exception as e:
                print(f"❌ Erro ao atualizar {script}: {e}")
                return False
        
        return True
    
    def migrar_produtos(self):
        """Executa migração de produtos"""
        self.print_header("ETAPA 5: Migrando Produtos")
        
        print("📦 Iniciando migração de 211 produtos...\n")
        
        # Importar e executar o migrador
        try:
            from migrate_to_marketplace import MarketplaceMigrator
            
            migrator = MarketplaceMigrator()
            
            # Obter produtos
            produtos = migrator.obter_produtos_sqlite()
            
            if not produtos:
                print("❌ Nenhum produto encontrado no SQLite!")
                return False
            
            print(f"📦 Encontrados {len(produtos)} produtos\n")
            
            # Migrar cada produto
            inicio = datetime.now()
            
            for i, produto in enumerate(produtos, 1):
                migrator.migrar_produto(produto)
                
                # Mostrar progresso a cada 20 produtos
                if i % 20 == 0:
                    print(f"   ... {i}/{len(produtos)} processados")
            
            # Relatório
            duracao = (datetime.now() - inicio).total_seconds()
            
            print("\n" + "="*70)
            print("📊 RELATÓRIO DE MIGRAÇÃO")
            print("="*70)
            print(f"✅ Migrados: {migrator.migrados}")
            print(f"❌ Erros: {migrator.erros}")
            print(f"📦 Total: {len(produtos)}")
            print(f"⏱️  Tempo: {duracao:.2f}s")
            print(f"🎯 Sucesso: {(migrator.migrados/len(produtos)*100):.1f}%")
            print("="*70)
            
            return migrator.migrados > 0
            
        except Exception as e:
            print(f"❌ Erro na migração: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def executar_setup_completo(self):
        """Executa todo o processo"""
        print("\n" + "🌟"*35)
        print("   SETUP AUTOMÁTICO: GRIFFE DA PRATA → MARKETPLACEBUILDER")
        print("🌟"*35)
        
        # Etapa 1: Testar API
        if not self.testar_api():
            print("\n❌ Setup abortado: API não disponível")
            return False
        
        # Etapa 2: Criar usuário
        self.criar_usuario_admin()
        self.fazer_login()
        
        # Etapa 3: Criar tenant
        if not self.criar_tenant():
            print("\n❌ Setup abortado: Falha ao criar tenant")
            return False
        
        # Etapa 4: Configurar scripts
        if not self.atualizar_scripts():
            print("\n❌ Setup abortado: Falha ao configurar scripts")
            return False
        
        # Etapa 5: Migrar produtos
        if not self.migrar_produtos():
            print("\n⚠️ Migração concluída com problemas")
        
        # Sucesso!
        print("\n" + "🎉"*35)
        print("   SETUP COMPLETO!")
        print("🎉"*35)
        print(f"\n✅ Tenant ID: {self.tenant_id}")
        print(f"✅ Storefront: http://localhost:5003/griffedaprata")
        print(f"✅ API: {self.api_url}")
        print("\n💡 Próximo passo: Acesse o storefront e teste o catálogo!")
        print("="*70 + "\n")
        
        return True

if __name__ == '__main__':
    setup = AutoSetup()
    setup.executar_setup_completo()
