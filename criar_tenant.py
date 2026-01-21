import sqlite3
import uuid
from datetime import datetime

# Conectar ao banco SQLite
db_path = r"D:\Projetos\Marketplace\marketplacebuilder.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Tenant ID
tenant_id = "f5852246-a25a-4848-80cf-7637d0218177"

# Verificar se tenant já existe
cursor.execute("SELECT Id FROM tenants WHERE Id = ?", (tenant_id,))
if cursor.fetchone():
    print(f"✅ Tenant {tenant_id} já existe!")
else:
    # Inserir tenant
    now = datetime.utcnow().isoformat()
    cursor.execute("""
        INSERT INTO tenants (Id, Name, Slug, IsActive, CreatedAt, UpdatedAt)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        tenant_id,
        "Griffe da Prata",
        "griffedaprata",
        1,  # True
        now,
        now
    ))
    
    # Inserir domínio
    domain_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO domains (Id, TenantId, Hostname, IsActive, CreatedAt)
        VALUES (?, ?, ?, ?, ?)
    """, (
        domain_id,
        tenant_id,
        "localhost",
        1,
        now
    ))
    
    conn.commit()
    print(f"✅ Tenant criado: {tenant_id}")
    print(f"✅ Domínio criado: localhost")

# Criar categoria padrão
now_cat = datetime.utcnow().isoformat()
cursor.execute("SELECT Id FROM categories WHERE TenantId = ?", (tenant_id,))
if not cursor.fetchone():
    category_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO categories (Id, TenantId, Name, Slug, CreatedAt, UpdatedAt)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        category_id,
        tenant_id,
        "Joias",
        "joias",
        now_cat,
        now_cat
    ))
    conn.commit()
    print(f"✅ Categoria 'Joias' criada: {category_id}")
else:
    print("✅ Categoria já existe")

conn.close()
print("\n🎉 Setup do tenant concluído!")
