"""
Setup Simplificado: Criação direta no banco + Migração
Bypassa problemas de autenticação criando tenant direto no PostgreSQL
"""

import sqlite3
import subprocess
import uuid
import time
from datetime import datetime

print("\n" + "="*70)
print("🚀 SETUP SIMPLIFICADO: GRIFFE DA PRATA")
print("="*70 + "\n")

# Verificar se já existe Tenant ID
tenant_id = None
try:
    with open('TENANT_ID.txt', 'r') as f:
        tenant_id = f.read().strip()
        if tenant_id:
            print(f"📋 Tenant ID existente encontrado: {tenant_id}\n")
except:
    pass

# Gerar novo Tenant ID se necessário
if not tenant_id:
    tenant_id = str(uuid.uuid4())
    print(f"📋 Novo Tenant ID gerado: {tenant_id}\n")

# ETAPA 1: Criar tenant direto no PostgreSQL
print("📦 ETAPA 1: Criando tenant no PostgreSQL...")

sql_tenant = f"""
CREATE TABLE IF NOT EXISTS "Tenants" (
    "Id" uuid PRIMARY KEY,
    "Name" text NOT NULL,
    "Subdomain" text UNIQUE NOT NULL,
    "PrimaryDomain" text,
    "Locale" text NOT NULL DEFAULT 'pt-BR',
    "Currency" text NOT NULL DEFAULT 'BRL',
    "IsActive" boolean NOT NULL DEFAULT true,
    "CreatedAt" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "UpdatedAt" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO "Tenants" 
("Id", "Name", "Subdomain", "PrimaryDomain", "Locale", "Currency", "IsActive", "CreatedAt", "UpdatedAt")
VALUES 
('{tenant_id}', 'Griffe da Prata', 'griffedaprata', 'griffedaprata.com.br', 'pt-BR', 'BRL', true, NOW(), NOW())
ON CONFLICT ("Subdomain") 
DO UPDATE SET 
    "Name" = 'Griffe da Prata',
    "PrimaryDomain" = 'griffedaprata.com.br',
    "UpdatedAt" = NOW()
RETURNING "Id";
"""

try:
    result = subprocess.run(
        ['docker', 'exec', 'marketplace-postgres', 
         'psql', '-U', 'marketplace', '-d', 'marketplacebuilder',
         '-c', sql_tenant],
        capture_output=True,
        text=True
    )
    
    if "INSERT" in result.stdout or "UPDATE" in result.stdout or tenant_id in result.stdout:
        print("✅ Tenant criado/atualizado com sucesso!")
    else:
        print(f"⚠️ Resultado: {result.stdout}")
        print(f"   Erro: {result.stderr}")
except Exception as e:
    print(f"❌ Erro: {e}")
    print("   Continuando mesmo assim...")

# ETAPA 2: Criar tabela de produtos
print("\n📦 ETAPA 2: Criando tabelas necessárias...")

sql_produtos = """
CREATE TABLE IF NOT EXISTS "Products" (
    "Id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    "TenantId" uuid NOT NULL,
    "CategoryId" uuid,
    "Title" text NOT NULL,
    "Slug" text NOT NULL,
    "Description" text,
    "Status" integer NOT NULL DEFAULT 0,
    "PrimaryImageUrl" text,
    "CreatedAt" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "UpdatedAt" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "FK_Products_Tenants" FOREIGN KEY ("TenantId") REFERENCES "Tenants"("Id")
);

CREATE TABLE IF NOT EXISTS "ProductVariants" (
    "Id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    "ProductId" uuid NOT NULL,
    "Title" text NOT NULL DEFAULT 'Padrão',
    "Sku" text NOT NULL,
    "Price" bigint NOT NULL,
    "CompareAtPrice" bigint,
    "CostPrice" bigint,
    "Stock" integer NOT NULL DEFAULT 0,
    "Weight" real,
    "IsDefault" boolean NOT NULL DEFAULT false,
    "CreatedAt" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "UpdatedAt" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "FK_ProductVariants_Products" FOREIGN KEY ("ProductId") REFERENCES "Products"("Id") ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS "IX_Products_TenantId" ON "Products"("TenantId");
CREATE INDEX IF NOT EXISTS "IX_Products_Slug" ON "Products"("Slug");
CREATE INDEX IF NOT EXISTS "IX_ProductVariants_ProductId" ON "ProductVariants"("ProductId");
CREATE INDEX IF NOT EXISTS "IX_ProductVariants_Sku" ON "ProductVariants"("Sku");
"""

try:
    result = subprocess.run(
        ['docker', 'exec', 'marketplace-postgres',
         'psql', '-U', 'marketplace', '-d', 'marketplacebuilder',
         '-c', sql_produtos],
        capture_output=True,
        text=True
    )
    
    if "CREATE TABLE" in result.stdout or "CREATE INDEX" in result.stdout:
        print("✅ Tabelas criadas com sucesso!")
    else:
        print("ℹ️  Tabelas já existem")
except Exception as e:
    print(f"⚠️ Erro ao criar tabelas: {e}")

# ETAPA 3: Migrar produtos
print("\n📦 ETAPA 3: Migrando produtos do SQLite...")

conn = sqlite3.connect('pedidos.db')
cursor = conn.cursor()
cursor.execute("SELECT codigo, titulo, preco_atacado, preco_varejo, peso, lote, descricao, imagem_url FROM produtos")
produtos = cursor.fetchall()
conn.close()

print(f"   Encontrados {len(produtos)} produtos\n")

migrados = 0
erros = 0
inicio = datetime.now()

for i, produto in enumerate(produtos, 1):
    codigo, titulo, preco_atacado, preco_varejo, peso, lote, descricao, imagem_url = produto
    
    # Gerar IDs
    product_id = str(uuid.uuid4())
    variant_id = str(uuid.uuid4())
    
    # Preparar dados
    titulo_clean = (titulo or f"Produto {codigo}").replace("'", "''")
    descricao_clean = (descricao or f"Código: {codigo}").replace("'", "''")
    slug = codigo.lower().replace('#', '').replace('-', '')
    preco_centavos = int(preco_varejo * 100) if preco_varejo else 0
    custo_centavos = int(preco_atacado * 100) if preco_atacado else 0
    
    # Limpar peso (remover 'g' e converter para número)
    if isinstance(peso, str):
        peso_str = peso.replace('g', '').replace('G', '').replace(',', '.').strip()
        peso_value = float(peso_str) if peso_str else 0
    else:
        peso_value = float(peso) if peso else 0
    
    # SQL para inserir produto e variante
    sql_insert = f"""
    BEGIN;
    INSERT INTO "Products" 
    ("Id", "TenantId", "Title", "Slug", "Description", "Status", "PrimaryImageUrl", "CreatedAt", "UpdatedAt")
    VALUES 
    ('{product_id}', '{tenant_id}', '{titulo_clean}', '{slug}', '{descricao_clean}', 1, '{imagem_url or ''}', NOW(), NOW());
    
    INSERT INTO "ProductVariants"
    ("Id", "ProductId", "Title", "Sku", "Price", "CostPrice", "Stock", "Weight", "IsDefault", "CreatedAt", "UpdatedAt")
    VALUES
    ('{variant_id}', '{product_id}', 'Padrão', '{codigo}', {preco_centavos}, {custo_centavos}, 100, {peso_value}, true, NOW(), NOW());
    COMMIT;
    """
    
    try:
        result = subprocess.run(
            ['docker', 'exec', 'marketplace-postgres',
             'psql', '-U', 'marketplace', '-d', 'marketplacebuilder',
             '-c', sql_insert],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if "COMMIT" in result.stdout:
            migrados += 1
            if i % 20 == 0:
                print(f"   ✅ {i}/{len(produtos)} produtos migrados...")
        else:
            erros += 1
            if erros <= 5:  # Mostrar apenas os primeiros 5 erros
                print(f"   ❌ Erro em {codigo}: {result.stderr[:100]}")
            
    except subprocess.TimeoutExpired:
        erros += 1
        print(f"   ⏱️  Timeout em {codigo}")
    except Exception as e:
        erros += 1
        if erros <= 5:
            print(f"   ❌ Exceção em {codigo}: {str(e)[:100]}")

# Relatório final
duracao = (datetime.now() - inicio).total_seconds()

print("\n" + "="*70)
print("📊 RELATÓRIO FINAL")
print("="*70)
print(f"✅ Migrados com sucesso: {migrados}")
print(f"❌ Erros: {erros}")
print(f"📦 Total processado: {len(produtos)}")
print(f"⏱️  Tempo decorrido: {duracao:.2f}s")
if len(produtos) > 0:
    print(f"🎯 Taxa de sucesso: {(migrados/len(produtos)*100):.1f}%")
print("="*70)

# Salvar configuração
print(f"\n💾 Salvando Tenant ID...")
with open('TENANT_ID.txt', 'w') as f:
    f.write(tenant_id)

# Atualizar scripts
print("🔧 Atualizando scripts de sincronização...")
for script in ['migrate_to_marketplace.py', 'sync_scraper_marketplace.py']:
    try:
        with open(script, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        conteudo = conteudo.replace(
            'COLE_AQUI_O_TENANT_ID_APOS_CRIAR_VIA_UI',
            tenant_id
        )
        
        with open(script, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print(f"   ✅ {script}")
    except:
        pass

print("\n" + "🎉"*35)
print("   SETUP CONCLUÍDO!")
print("🎉"*35)
print(f"\n📋 Tenant ID: {tenant_id}")
print(f"📁 Salvo em: TENANT_ID.txt")
print(f"\n🌐 Acesse seu storefront:")
print(f"   http://localhost:5003/griffedaprata")
print("\n💡 Para sincronizar no futuro:")
print(f"   python sync_scraper_marketplace.py")
print("="*70 + "\n")
