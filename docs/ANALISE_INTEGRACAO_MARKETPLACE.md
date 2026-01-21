# 🔗 Análise de Integração: Griffe da Prata ↔️ MarketplaceBuilder

## 📊 Visão Geral dos Projetos

### **Projeto 1: Griffe da Prata** (Atual)
- **Stack**: Python 3.10 + Flask + SQLite
- **Função**: Sistema de gestão de pedidos e scraping de fornecedor
- **Componentes**:
  - Scrapers (Selenium + BeautifulSoup)
  - Backend API REST (Flask)
  - Dashboard Admin (HTML/JS)
  - Banco SQLite com 211 produtos
  - Integração WhatsApp com fornecedor
  - Cálculo automático de margem 250%

### **Projeto 2: MarketplaceBuilder**
- **Stack**: .NET 8 + ASP.NET Core + PostgreSQL + Redis + MinIO
- **Função**: Plataforma multi-tenant de e-commerce completa
- **Componentes**:
  - API REST com autenticação Identity
  - Sistema de permissões RBAC
  - Carrinho + Checkout Stripe
  - Multi-tenant (subdomínios)
  - Catálogo de produtos
  - Gestão de pedidos
  - Storefront personalizado
  - Webhooks Stripe
  - AI para geração de conteúdo

---

## 🎯 Cenários de Integração Possíveis

### **OPÇÃO 1: Griffe da Prata como Tenant no Marketplace** ⭐ RECOMENDADO
**Descrição**: Usar o MarketplaceBuilder como plataforma principal e migrar os dados da Griffe da Prata para dentro dele como um tenant.

**Vantagens**:
- ✅ Frontend profissional pronto (Storefront)
- ✅ Checkout completo com Stripe
- ✅ Gestão de pedidos enterprise-grade
- ✅ Escalabilidade (PostgreSQL + Redis)
- ✅ Multi-tenant permite expandir para outras lojas
- ✅ Sistema de permissões robusto
- ✅ Infraestrutura completa (Docker)

**Como Implementar**:
1. **Migrar produtos**: Criar script Python que lê do SQLite e cria produtos via API do Marketplace
2. **Manter scrapers**: Scrapers Python continuam rodando e atualizando via API
3. **Integrar WhatsApp**: Adicionar endpoint customizado no Marketplace para WhatsApp do fornecedor
4. **Configurar tenant**: `griffedaprata.marketplace.local` ou `griffedaprata.com.br`

**Arquitetura**:
```
┌─────────────────────────────────────────────────────┐
│         MarketplaceBuilder (.NET)                    │
│  ┌─────────────────────────────────────────────┐   │
│  │  Tenant: Griffe da Prata                     │   │
│  │  - Storefront: griffedaprata.marketplace.com │   │
│  │  - 211 produtos sincronizados                │   │
│  │  - Checkout Stripe                           │   │
│  │  - Pedidos integrados                        │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
           ↑ API REST (.NET)
           │
┌──────────┴──────────┐
│  Python Services     │
│  - Scraper Atacado   │ ← Atualiza produtos via API
│  - WhatsApp Handler  │ ← Envia pedidos ao fornecedor
└─────────────────────┘
```

---

### **OPÇÃO 2: API Gateway com Integração Híbrida**
**Descrição**: Manter ambos os sistemas separados, mas integrados via API.

**Vantagens**:
- ✅ Mantém a simplicidade do Flask atual
- ✅ Aproveita funcionalidades do Marketplace gradualmente
- ✅ Menor esforço inicial

**Desvantagens**:
- ❌ Duplicação de dados
- ❌ Sincronização complexa
- ❌ Dois backends para manter

**Arquitetura**:
```
Frontend Griffe da Prata (HTML/JS)
        ↓
┌───────────────┬──────────────────┐
│  Flask API    │  Marketplace API  │
│  (pedidos)    │  (catálogo)       │
└───────────────┴──────────────────┘
```

---

### **OPÇÃO 3: Usar Marketplace apenas como Catálogo Público**
**Descrição**: MarketplaceBuilder serve o storefront público, Flask gerencia pedidos internos.

**Vantagens**:
- ✅ Frontend profissional para clientes
- ✅ Backend simplificado para gestão interna

**Desvantagens**:
- ❌ Pedidos desconectados entre sistemas
- ❌ Sincronização manual necessária

---

## 🚀 Plano de Implementação - OPÇÃO 1 (Recomendado)

### **FASE 1: Preparação e Migração de Dados** (2-3 dias)

#### 1.1. Setup do MarketplaceBuilder
```bash
# Clonar e configurar
cd d:\Projetos\Marketplace
docker compose -f infra/docker-compose.yml up -d

# Aplicar migrations
cd src/MarketplaceBuilder.Api
dotnet ef database update

# Rodar API
dotnet run --urls "https://localhost:5001"
```

#### 1.2. Criar Tenant "Griffe da Prata" via UI Admin
1. Acessar painel admin: `https://localhost:5002/admin` (ou porta configurada)
2. Fazer login com usuário PlatformSuperAdmin
3. Navegar para "Stores" ou "Tenants"
4. Clicar em "Create New Store"
5. Preencher formulário:
   - **Store Name**: `Griffe da Prata`
   - **Subdomain**: `griffedaprata`
   - **Currency**: `BRL`
   - **Locale**: `pt-BR`
6. Salvar e copiar o **Tenant ID** gerado (GUID)

#### 1.3. Script de Migração de Produtos
Criar `migrate_to_marketplace.py`:
```python
import requests
import sqlite3
import json

# Conectar ao SQLite atual
conn = sqlite3.connect('pedidos.db')
cursor = conn.cursor()

# Obter todos os produtos
cursor.execute("SELECT * FROM produtos")
produtos = cursor.fetchall()

# API do Marketplace
MARKETPLACE_API = "https://localhost:5001/api"
TENANT_ID = "GUID_DO_TENANT"  # Obtido na criação

for produto in produtos:
    codigo, titulo, preco_atacado, preco_varejo, *rest = produto
    
    # Criar produto via API
    payload = {
        "title": titulo,
        "description": f"Código: {codigo}",
        "status": "Active",
        "variants": [{
            "sku": codigo,
            "price": int(preco_varejo * 100),  # centavos
            "stock": 100,
            "isDefault": True
        }]
    }
    
    response = requests.post(
        f"{MARKETPLACE_API}/admin/products",
        json=payload,
        headers={
            "X-Tenant-Id": TENANT_ID,
            "Content-Type": "application/json"
        },
        verify=False
    )
    
    print(f"✅ Migrado: {titulo} - Status: {response.status_code}")
```

---

### **FASE 2: Integração de Scrapers** (1-2 dias)

#### 2.1. Modificar `scraper_atacado_FINAL.py`
Adicionar sincronização automática com Marketplace:

```python
def sincronizar_com_marketplace(produtos):
    """Atualiza produtos no Marketplace via API"""
    MARKETPLACE_API = "https://localhost:5001/api"
    
    for produto in produtos:
        # Verificar se existe
        response = requests.get(
            f"{MARKETPLACE_API}/admin/products/by-sku/{produto['codigo']}",
            headers={"X-Tenant-Id": TENANT_ID}
        )
        
        if response.status_code == 404:
            # Criar novo
            criar_produto_marketplace(produto)
        else:
            # Atualizar preço
            atualizar_preco_marketplace(produto)
```

#### 2.2. Agendar Execução
```python
# cron_scraper.py
import schedule
import time
from scraper_atacado_FINAL import executar_scraper, sincronizar_com_marketplace

def job():
    print("🔄 Executando scraper...")
    produtos = executar_scraper()
    sincronizar_com_marketplace(produtos)
    print(f"✅ {len(produtos)} produtos atualizados!")

# Rodar todo dia às 3h da manhã
schedule.every().day.at("03:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

### **FASE 3: Extensão WhatsApp no Marketplace** (2-3 dias)

#### 3.1. Criar Endpoint Customizado
Adicionar em `MarketplaceBuilder.Api/Endpoints/CustomEndpoints.cs`:

```csharp
public static class CustomEndpoints
{
    public static void MapGriffeDaPrataEndpoints(this WebApplication app)
    {
        var group = app.MapGroup("/api/griffedaprata")
            .RequireAuthorization("OrdersRead");
        
        // Gerar mensagem WhatsApp para fornecedor
        group.MapGet("/orders/{orderId:guid}/whatsapp-supplier", 
            async (Guid orderId, ApplicationDbContext db) =>
        {
            var order = await db.Orders
                .Include(o => o.Items)
                .FirstOrDefaultAsync(o => o.Id == orderId);
            
            if (order == null) return Results.NotFound();
            
            var mensagem = $"🛒 *NOVO PEDIDO - GRIFFE DA PRATA*\n\n";
            mensagem += $"📋 Pedido: #{order.Id.ToString()[..8]}\n";
            mensagem += $"📅 Data: {order.CreatedAt:dd/MM/yyyy HH:mm}\n\n";
            mensagem += "*PRODUTOS:*\n";
            
            foreach (var item in order.Items)
            {
                var precoAtacado = item.UnitPriceAmount / 3.5m; // Reverter margem
                mensagem += $"• {item.Sku} - {item.Quantity}x - R$ {precoAtacado:F2}\n";
            }
            
            var totalAtacado = order.TotalAmount / 3.5m;
            mensagem += $"\n💰 *Total: R$ {totalAtacado/100:F2}*\n\n";
            mensagem += "Confirma disponibilidade? 🙏";
            
            return Results.Ok(new {
                whatsapp = "5582981602651",
                mensagem
            });
        });
    }
}

// Em Program.cs, adicionar:
app.MapGriffeDaPrataEndpoints();
```

---

### **FASE 4: Frontend Customizado** (1-2 dias)

#### 4.1. Personalizar Storefront
Editar `MarketplaceBuilder.Storefront/Pages/Shared/_Layout.cshtml`:

```html
<!-- Adicionar logo e cores da Griffe da Prata -->
<style>
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
    }
    .navbar-brand {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
</style>
```

#### 4.2. Adicionar Botão "Enviar ao Fornecedor"
No admin de pedidos, adicionar botão que chama o endpoint customizado.

---

## 📈 Melhorias Sugeridas para Ambos os Projetos

### **Para Griffe da Prata (Python/Flask)**

#### 1. **Separar em Microserviços**
```
griffe-scraper/        # Scraping service
  ├── scraper.py
  ├── scheduler.py
  └── requirements.txt

griffe-api/           # API Flask
  ├── app.py
  ├── models.py
  └── requirements.txt
```

#### 2. **Adicionar Cache Redis**
```python
from redis import Redis
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379'
})

@app.route('/api/produtos')
@cache.cached(timeout=300)  # 5 minutos
def get_produtos():
    return jsonify(produtos)
```

#### 3. **Containerizar com Docker**
```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "backend_api.py"]
```

```yaml
# docker-compose.yml
services:
  griffe-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=sqlite:///pedidos.db
  
  griffe-scraper:
    build: .
    command: python cron_scraper.py
    depends_on:
      - griffe-api
```

#### 4. **Adicionar Testes**
```python
# tests/test_api.py
import pytest
from backend_api import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_criar_pedido(client):
    response = client.post('/api/pedidos', json={
        'cliente_nome': 'Teste',
        'cliente_whatsapp': '5511999999999',
        'items': [{'codigo': 'K2-80', 'quantidade': 2}]
    })
    assert response.status_code == 201
```

#### 5. **Adicionar Logging Estruturado**
```python
import logging
import structlog

logging.basicConfig(
    format="%(message)s",
    level=logging.INFO
)

log = structlog.get_logger()

@app.route('/api/pedidos', methods=['POST'])
def criar_pedido():
    log.info("pedido.criado", 
             cliente=data['cliente_nome'],
             total=total_varejo)
```

---

### **Para MarketplaceBuilder (.NET)**

#### 1. **Adicionar Suporte a BRL e Localização**
```csharp
// Em appsettings.json
"SupportedCurrencies": ["USD", "BRL", "EUR"],
"DefaultLocale": "pt-BR"

// Ajustar formatação de moeda no Storefront
@product.Price.ToString("C", new CultureInfo("pt-BR"))
```

#### 2. **Integração com Pagamento Local (PagSeguro/Mercado Pago)**
```csharp
public interface IPaymentGateway
{
    Task<CheckoutSession> CreateSessionAsync(Order order);
}

public class MercadoPagoGateway : IPaymentGateway
{
    // Implementação para mercado brasileiro
}
```

#### 3. **Adicionar Cálculo de Frete (Correios API)**
```csharp
public class FreightCalculator
{
    public async Task<decimal> CalculateAsync(
        string cep, decimal weight)
    {
        // Integração com API Correios
    }
}
```

#### 4. **Dashboard com Métricas em Tempo Real**
```csharp
// SignalR para atualizações em tempo real
services.AddSignalR();

public class DashboardHub : Hub
{
    public async Task BroadcastNewOrder(Order order)
    {
        await Clients.All.SendAsync("NewOrder", order);
    }
}
```

#### 5. **Exportação de Relatórios**
```csharp
// Adicionar endpoint de exportação
app.MapGet("/api/admin/orders/export", 
    async (ApplicationDbContext db) =>
{
    var orders = await db.Orders.ToListAsync();
    var csv = ConvertToCsv(orders);
    return Results.File(csv, "text/csv", "pedidos.csv");
});
```

---

## 🎯 Recomendação Final

**Para o seu caso específico, recomendo a OPÇÃO 1** pela seguinte razão:

1. **Você já tem o MarketplaceBuilder completo** - aproveitá-lo economiza meses de desenvolvimento
2. **Frontend profissional** - melhor experiência para seus clientes
3. **Escalabilidade** - quando quiser adicionar novas lojas, já está preparado
4. **Scrapers Python** - continuam funcionando, apenas mudam o destino da API
5. **Pagamentos** - Stripe já integrado (ou pode adicionar Mercado Pago/PagSeguro)

### **Cronograma Estimado**:
- **Semana 1**: Setup Marketplace + Migração de dados
- **Semana 2**: Integração scrapers + Testes
- **Semana 3**: Customizações WhatsApp + Frontend
- **Semana 4**: Testes finais + Deploy

### **Próximos Passos Imediatos**:
1. ✅ Subir o MarketplaceBuilder localmente
2. ✅ Acessar UI Admin e criar tenant "Griffe da Prata"
3. ⏳ Copiar Tenant ID gerado
4. ⏳ Migrar os 211 produtos via script Python
5. ⏳ Configurar scrapers para sincronização automática
6. ⏳ Testar fluxo completo de compra

**Importante**: Após criar o tenant via UI, você precisará do **Tenant ID** (GUID) para os scripts de migração e integração.

Quer que eu crie os scripts de migração e integração? 🚀
