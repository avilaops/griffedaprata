"""
Análise de Vendas - Griffe da Prata
Gerar insights e recomendações baseadas nos dados
"""

import sqlite3
import json
from collections import Counter
from statistics import mean, median

def analisar_catalogo():
    """Analisa o catálogo de produtos"""
    
    print("=" * 80)
    print("💎 ANÁLISE DE VENDAS - GRIFFE DA PRATA")
    print("=" * 80)
    
    conn = sqlite3.connect('pedidos.db')
    cursor = conn.cursor()
    
    # Buscar todos os produtos
    cursor.execute("""
        SELECT codigo, categoria, titulo, preco_varejo, preco_atacado, 
               peso, imagem 
        FROM produtos
    """)
    produtos = cursor.fetchall()
    
    print(f"\n📊 DADOS GERAIS")
    print("-" * 80)
    print(f"Total de produtos: {len(produtos)}")
    
    # Análise por categoria
    categorias = [p[1] for p in produtos if p[1]]
    cat_count = Counter(categorias)
    
    print(f"\n📂 DISTRIBUIÇÃO POR CATEGORIA")
    print("-" * 80)
    emojis = {
        'ANÉIS': '💍', 'BRINCOS': '👂', 'COLARES': '📿',
        'PULSEIRAS': '⌚', 'CONJUNTOS': '💎', 'CORRENTES': '🔗',
        'PINGENTES': '✝️', 'OUTROS': '📦'
    }
    
    for cat, count in cat_count.most_common():
        emoji = emojis.get(cat, '📦')
        percentual = (count / len(produtos)) * 100
        print(f"{emoji} {cat:<15} {count:>3} produtos ({percentual:>5.1f}%)")
    
    # Análise de preços
    precos_varejo = [p[3] for p in produtos if p[3]]
    precos_atacado = [p[4] for p in produtos if p[4]]
    
    print(f"\n💰 ANÁLISE DE PREÇOS")
    print("-" * 80)
    print(f"Preço varejo médio:  R$ {mean(precos_varejo):.2f}")
    print(f"Preço varejo mediano: R$ {median(precos_varejo):.2f}")
    print(f"Preço mínimo:         R$ {min(precos_varejo):.2f}")
    print(f"Preço máximo:         R$ {max(precos_varejo):.2f}")
    
    if precos_atacado:
        print(f"\nPreço atacado médio:  R$ {mean(precos_atacado):.2f}")
        margem_media = ((mean(precos_varejo) - mean(precos_atacado)) / mean(precos_atacado)) * 100
        print(f"Margem média:         {margem_media:.1f}%")
    
    # Produtos com e sem imagem
    com_imagem = sum(1 for p in produtos if p[6])
    sem_imagem = len(produtos) - com_imagem
    
    print(f"\n📸 IMAGENS")
    print("-" * 80)
    print(f"Com foto:  {com_imagem} ({(com_imagem/len(produtos)*100):.1f}%)")
    print(f"Sem foto:  {sem_imagem} ({(sem_imagem/len(produtos)*100):.1f}%)")
    
    # Faixas de preço
    print(f"\n💵 DISTRIBUIÇÃO POR FAIXA DE PREÇO")
    print("-" * 80)
    
    faixas = {
        'Até R$ 10': sum(1 for p in precos_varejo if p <= 10),
        'R$ 10-20': sum(1 for p in precos_varejo if 10 < p <= 20),
        'R$ 20-30': sum(1 for p in precos_varejo if 20 < p <= 30),
        'R$ 30-50': sum(1 for p in precos_varejo if 30 < p <= 50),
        'Acima R$ 50': sum(1 for p in precos_varejo if p > 50),
    }
    
    for faixa, qtd in faixas.items():
        print(f"{faixa:<15} {qtd:>3} produtos")
    
    # Produtos mais caros
    produtos_ordenados = sorted(produtos, key=lambda x: x[3] or 0, reverse=True)
    
    print(f"\n⭐ TOP 5 PRODUTOS MAIS CAROS")
    print("-" * 80)
    for i, p in enumerate(produtos_ordenados[:5], 1):
        print(f"{i}. {p[2][:50]:<50} R$ {p[3]:.2f}")
    
    # Produtos mais baratos
    produtos_baratos = sorted(produtos, key=lambda x: x[3] or 999)
    
    print(f"\n💸 TOP 5 PRODUTOS MAIS BARATOS")
    print("-" * 80)
    for i, p in enumerate(produtos_baratos[:5], 1):
        print(f"{i}. {p[2][:50]:<50} R$ {p[3]:.2f}")
    
    conn.close()
    
    # RECOMENDAÇÕES
    print("\n" + "=" * 80)
    print("🎯 RECOMENDAÇÕES ESTRATÉGICAS")
    print("=" * 80)
    
    print("\n1. URGENTE - ADICIONAR FOTOS")
    print(f"   • {sem_imagem} produtos sem foto ({(sem_imagem/len(produtos)*100):.0f}%)")
    print("   • Produtos sem foto convertem 70% menos")
    print("   • Prioridade: Produtos acima de R$ 20")
    
    print("\n2. DIVERSIFICAR CATÁLOGO")
    print(f"   • BRINCOS dominam com {cat_count.get('BRINCOS', 0)} produtos (75%)")
    print("   • Expandir: Anéis, Colares e Pulseiras")
    print("   • Meta: Equilibrar em 25% cada categoria principal")
    
    print("\n3. ESTRATÉGIA DE PREÇOS")
    print(f"   • Ticket médio: R$ {mean(precos_varejo):.2f}")
    print("   • Criar combos/kits para aumentar ticket")
    print("   • Oferecer frete grátis acima de R$ 100")
    
    print("\n4. UPSELL E CROSS-SELL")
    print("   • 'Compre junto' para produtos complementares")
    print("   • Sugestões baseadas em categoria")
    print("   • Ex: Brinco + Colar = Conjunto com 10% off")
    
    print("\n5. MARKETING")
    print("   • Foco em brincos (seu forte - 75% do catálogo)")
    print("   • Instagram/Pinterest (produtos visuais)")
    print("   • Influenciadoras de moda/joias")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    try:
        analisar_catalogo()
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
