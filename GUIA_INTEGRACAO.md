# 🚀 Guia de Integração: Griffe da Prata + MarketplaceBuilder

## 📋 Passo a Passo Completo

### **ETAPA 1: Subir o MarketplaceBuilder** ⏱️ 5-10 minutos

#### 1.1. Iniciar Infraestrutura (PostgreSQL, Redis, MinIO)
```bash
cd d:\Projetos\Marketplace\infra
docker compose up -d
```

#### 1.2. Aplicar Migrations
```bash
cd ..\src\MarketplaceBuilder.Api
dotnet ef database update
```

#### 1.3. Iniciar API Backend
```bash
# Terminal 1
dotnet run --urls "https://localhost:5001"
```

#### 1.4. Iniciar Admin UI
```bash
# Terminal 2 (nova janela)
cd ..\MarketplaceBuilder.Admin
dotnet run --urls "https://localhost:5002"
```

#### 1.5. Iniciar Storefront
```bash
# Terminal 3 (nova janela)
cd ..\MarketplaceBuilder.Storefront
dotnet run --urls "http://localhost:5003"
```

---

### **ETAPA 2: Criar Tenant via UI** ⏱️ 2-3 minutos

1. Acesse: `https://localhost:5002`
2. Faça login com credenciais de admin
3. Navegue para **"Stores"** ou **"Tenants"**
4. Clique em **"Create New Store"**
5. Preencha:
   - **Store Name**: `Griffe da Prata`
   - **Subdomain**: `griffedaprata`
   - **Currency**: `BRL`
   - **Locale**: `pt-BR`
6. **IMPORTANTE**: Copie o **Tenant ID** (GUID) gerado
   - Exemplo: `a1b2c3d4-5678-90ab-cdef-1234567890ab`

---

### **ETAPA 3: Configurar Scripts** ⏱️ 1 minuto

Edite **ambos** os arquivos e cole o Tenant ID:

#### `migrate_to_marketplace.py` - Linha 14:
```python
'tenant_id': 'COLE_AQUI_SEU_TENANT_ID',
```

#### `sync_scraper_marketplace.py` - Linha 11:
```python
'tenant_id': 'COLE_AQUI_SEU_TENANT_ID',
```

---

### **ETAPA 4: Instalar Dependências** ⏱️ 1 minuto

```bash
cd d:\Projetos\Landing-Pages\griffedaprata.com.br
python -m pip install --user schedule
```

---

### **ETAPA 5: Migração Inicial** ⏱️ 2-5 minutos

```bash
python migrate_to_marketplace.py
```

**O que faz**:
- Lê 211 produtos do `pedidos.db` (SQLite)
- Cria cada produto no MarketplaceBuilder via API
- Mostra progresso em tempo real
- Relatório final de sucesso/erros

**Resultado esperado**:
```
📊 RELATÓRIO DE MIGRAÇÃO
✅ Migrados com sucesso: 211
❌ Erros: 0
📦 Total processado: 211
⏱️  Tempo decorrido: 45.32s
🎯 Taxa de sucesso: 100.0%
```

---

### **ETAPA 6: Testar Storefront** ⏱️ 1 minuto

Acesse: `http://localhost:5003/griffedaprata`

**Verificar**:
- ✅ Produtos aparecem na listagem
- ✅ Preços corretos (R$ com margem de 250%)
- ✅ Imagens carregando
- ✅ Detalhes do produto acessíveis

---

### **ETAPA 7: Configurar Sincronização Automática** (Opcional)

#### Opção A: Sincronização Manual
```bash
python sync_scraper_marketplace.py
```

#### Opção B: Scraper + Sincronização Integrada
```bash
python scraper_with_sync.py
```

#### Opção C: Agendamento Automático (3h da manhã)
```bash
python cron_scraper_marketplace.py
```

---

## 🔧 Arquivos Criados

| Arquivo | Função |
|---------|--------|
| `migrate_to_marketplace.py` | Migração inicial (SQLite → Marketplace) |
| `sync_scraper_marketplace.py` | Sincronização sob demanda |
| `scraper_with_sync.py` | Scraper + sincronização em uma execução |
| `cron_scraper_marketplace.py` | Agendador automático (diário às 3h) |
| `requirements_marketplace.txt` | Dependências adicionais |

---

## 🎯 Fluxo de Dados

```
┌─────────────────────────────────────────────┐
│  ATACADO DE PRATA (Fornecedor)              │
│  https://atacadodeprata.rdi.store           │
└─────────────┬───────────────────────────────┘
              │ Scraper (Selenium)
              ↓
┌─────────────────────────────────────────────┐
│  SQLITE LOCAL (pedidos.db)                  │
│  211 produtos com preços atualizados        │
└─────────────┬───────────────────────────────┘
              │ Sincronização (API REST)
              ↓
┌─────────────────────────────────────────────┐
│  MARKETPLACEBUILDER (PostgreSQL)            │
│  Tenant: Griffe da Prata                    │
│  - Catálogo completo                        │
│  - Checkout Stripe                          │
│  - Gestão de pedidos                        │
└─────────────┬───────────────────────────────┘
              │ Storefront
              ↓
┌─────────────────────────────────────────────┐
│  CLIENTES FINAIS                            │
│  http://localhost:5003/griffedaprata        │
│  - Navegam produtos                         │
│  - Adicionam ao carrinho                    │
│  - Checkout com Stripe                      │
└─────────────────────────────────────────────┘
```

---

## 🐛 Troubleshooting

### Erro: "Não foi possível conectar à API do Marketplace"
**Solução**: Certifique-se de que a API está rodando:
```bash
curl -k https://localhost:5001/health
```

### Erro: "TENANT ID NÃO CONFIGURADO"
**Solução**: Edite os arquivos `.py` e cole o GUID correto

### Erro: "Invalid Tenant ID"
**Solução**: Verifique se copiou o ID completo (formato GUID)

### Produtos não aparecem no Storefront
**Soluções**:
1. Verificar se produtos têm `status: 'Active'`
2. Limpar cache do navegador
3. Verificar logs da API: `dotnet run --urls "https://localhost:5001"`

---

## 📞 Próximos Passos

Após a integração:

1. ✅ **Configurar domínio**: `griffedaprata.com.br` → Storefront
2. ✅ **Stripe**: Adicionar chaves reais para pagamentos
3. ✅ **WhatsApp**: Integrar endpoint customizado para fornecedor
4. ✅ **Design**: Personalizar cores/logo do storefront
5. ✅ **SEO**: Configurar meta tags e sitemap

---

## 🎉 Benefícios da Integração

| Antes (Flask + SQLite) | Depois (Marketplace) |
|------------------------|----------------------|
| Frontend simples HTML  | Storefront profissional |
| Sem carrinho de compras | Carrinho completo |
| Sem checkout | Checkout Stripe integrado |
| Gestão manual de pedidos | Dashboard automático |
| SQLite (não escala) | PostgreSQL + Redis |
| Uma loja apenas | Multi-tenant (escalável) |

---

**🚀 Boa integração!**
