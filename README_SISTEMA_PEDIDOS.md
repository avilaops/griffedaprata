# 🛒 Sistema de Pedidos - Griffe da Prata

Sistema completo para gerenciar pedidos e integração automática com fornecedor (Atacado de Prata).

## 📋 O que foi criado

### 1. **Backend Python** (`sistema_pedidos.py`)
- Gerencia pedidos em JSON
- Calcula automaticamente:
  - Preço de custo (atacado)
  - Preço de venda (varejo com 250%)
  - Lucro por pedido
- Gera mensagens formatadas para WhatsApp
- Controla status dos pedidos

### 2. **Painel Admin** (`painel_pedidos.html`)
- Interface visual para gerenciar pedidos
- Dashboard com estatísticas
- Filtros por status (Pendente, Enviado, Concluído)
- Botão para enviar direto ao fornecedor via WhatsApp
- Controle de status dos pedidos

## 🚀 Como Usar

### Criar um novo pedido (Python):

```python
from sistema_pedidos import SistemaPedidos

sistema = SistemaPedidos()

# Criar pedido
pedido = sistema.criar_pedido(
    cliente_nome="Maria Silva",
    cliente_whatsapp="5511999999999",
    items=[
        {'codigo': 'K2-80', 'quantidade': 2},
        {'codigo': 'P3-10', 'quantidade': 1}
    ]
)

print(f"Pedido #{pedido['id']} criado!")
print(f"Total: {pedido['total_varejo']}")
print(f"Lucro: {pedido['lucro']}")
```

### Abrir o painel admin:

1. Abra `painel_pedidos.html` no navegador
2. Veja todos os pedidos
3. Clique em "📱 Enviar ao Fornecedor" para abrir WhatsApp com mensagem pronta
4. Marque status conforme progresso

## 📊 Fluxo de Trabalho

```
1. Cliente compra no seu site
   ↓
2. Sistema cria pedido automaticamente
   (calcula custos, preços, lucro)
   ↓
3. Você abre o painel admin
   ↓
4. Clica em "Enviar ao Fornecedor"
   (abre WhatsApp com pedido formatado)
   ↓
5. Fornecedor confirma
   ↓
6. Marca pedido como "Enviado"
   ↓
7. Cliente recebe
   ↓
8. Marca como "Concluído"
```

## 💰 Cálculos Automáticos

Para cada pedido, o sistema calcula:

- **Custo Total (Atacado)**: Soma dos preços de atacado × quantidades
- **Venda Total (Varejo)**: Soma dos preços de varejo (atacado × 3.5)
- **Lucro**: Venda - Custo
- **Margem**: 250% fixo

### Exemplo:
```
Produto: K2-80
Atacado: R$ 1,70
Varejo: R$ 5,95 (1,70 × 3.5)
Quantidade: 2
Lucro: R$ 8,50
```

## 📱 Mensagem WhatsApp Gerada

Quando clicar em "Enviar ao Fornecedor", abre o WhatsApp com:

```
🛒 NOVO PEDIDO - GRIFFE DA PRATA

📋 Pedido: #a1b2c3d4
📅 Data: 20/01/2026 14:30

PRODUTOS:
• K2-80 - 2x - R$ 1,70
• P3-10 - 1x - R$ 18,90

💰 Total: R$ 22,30

Cliente: Maria Silva
Confirma disponibilidade? 🙏
```

## 🔗 Integração com seu Site

Para integrar com seu site em produção:

```javascript
// No checkout do seu site
async function finalizarCompra(carrinho, cliente) {
    const pedido = {
        cliente_nome: cliente.nome,
        cliente_whatsapp: cliente.whatsapp,
        items: carrinho.map(item => ({
            codigo: item.codigo,
            quantidade: item.quantidade
        }))
    };
    
    // Enviar para backend
    const response = await fetch('/api/criar-pedido', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pedido)
    });
    
    const resultado = await response.json();
    alert(`Pedido #${resultado.id} criado com sucesso!`);
}
```

## 📂 Estrutura de Arquivos

```
griffedaprata.com.br/
├── sistema_pedidos.py          # Backend de gerenciamento
├── painel_pedidos.html         # Interface admin
├── sistema_pedidos/            # Dados
│   └── pedidos.json            # Histórico de pedidos
└── atacadodeprata_completo/
    └── dados/
        └── produtos_atacado_FINAL.json  # Catálogo
```

## 🎯 Próximos Passos

1. **Testar**: Criar pedidos de teste
2. **Personalizar**: Ajustar cores/textos do painel
3. **Integrar**: Conectar com seu site de vendas
4. **Expandir**: Adicionar relatórios, gráficos, exportação

## 🔧 Requisitos

- Python 3.7+
- Navegador moderno (Chrome, Firefox, Edge)
- Catálogo de produtos do fornecedor (`produtos_atacado_FINAL.json`)

## 💡 Dicas

- Mantenha backup do `pedidos.json`
- Use o painel diariamente para acompanhar pedidos
- O WhatsApp do fornecedor está configurado: +55 82 98160-2651
- Personalize as mensagens em `sistema_pedidos.py`

---

**Desenvolvido para Griffe da Prata** 💎
Automação de pedidos com margem de 250%
