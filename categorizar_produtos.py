"""
Script para Organizar Produtos por Categorias
Categoriza automaticamente baseado no nome/descrição
"""

import sqlite3
import re

# Categorias de joias
CATEGORIAS = {
    'ANÉIS': [
        'anel', 'anel solitario', 'anel alianca', 'anel de prata', 'solitario'
    ],
    'BRINCOS': [
        'brinco', 'brincos', 'argola', 'piercing', 'ear', 'stud'
    ],
    'COLARES': [
        'colar', 'gargantilha', 'choker', 'corrente', 'pingente', 'correntinha',
        'cordao', 'cordão'
    ],
    'PULSEIRAS': [
        'pulseira', 'bracelete', 'tornozeleira', 'berloque', 'charm'
    ],
    'CONJUNTOS': [
        'conjunto', 'kit', 'set'
    ],
    'CORRENTES': [
        'corrente', 'correntes', 'cordao', 'cordão', 'chain'
    ],
    'PINGENTES': [
        'pingente', 'crucifixo', 'cruz', 'medalha', 'sao jorge', 'santo'
    ],
    'OUTROS': []  # Fallback
}

def detectar_categoria(titulo, descricao=''):
    """Detecta a categoria baseado no título e descrição"""
    texto = f"{titulo} {descricao}".lower()
    
    # Verificar cada categoria
    for categoria, palavras_chave in CATEGORIAS.items():
        if categoria == 'OUTROS':
            continue
            
        for palavra in palavras_chave:
            if palavra.lower() in texto:
                return categoria
    
    return 'OUTROS'

def categorizar_produtos():
    """Categoriza todos os produtos do banco de dados"""
    
    print("=" * 60)
    print("🏷️  ORGANIZANDO PRODUTOS POR CATEGORIAS")
    print("=" * 60)
    
    # Conectar ao banco
    conn = sqlite3.connect('pedidos.db')
    cursor = conn.cursor()
    
    # Buscar todos os produtos
    cursor.execute("SELECT codigo, titulo, descricao, categoria FROM produtos")
    produtos = cursor.fetchall()
    
    print(f"\n📦 Total de produtos: {len(produtos)}")
    print("\n🔄 Categorizando...\n")
    
    # Estatísticas
    stats = {cat: 0 for cat in CATEGORIAS.keys()}
    atualizados = 0
    
    # Processar cada produto
    for codigo, titulo, descricao, categoria_atual in produtos:
        # Detectar categoria correta
        categoria_nova = detectar_categoria(titulo, descricao or '')
        
        # Atualizar se diferente
        if categoria_nova != categoria_atual:
            cursor.execute(
                "UPDATE produtos SET categoria = ? WHERE codigo = ?",
                (categoria_nova, codigo)
            )
            atualizados += 1
            print(f"✅ {codigo[:30]:<30} → {categoria_nova}")
        
        stats[categoria_nova] += 1
    
    # Salvar mudanças
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("📊 ESTATÍSTICAS POR CATEGORIA")
    print("=" * 60)
    
    for categoria, quantidade in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        if quantidade > 0:
            emoji = {
                'ANÉIS': '💍',
                'BRINCOS': '👂',
                'COLARES': '📿',
                'PULSEIRAS': '⌚',
                'CONJUNTOS': '💎',
                'CORRENTES': '🔗',
                'PINGENTES': '✝️',
                'OUTROS': '📦'
            }.get(categoria, '📦')
            
            print(f"{emoji} {categoria:<15} {quantidade:>3} produtos")
    
    print("\n" + "=" * 60)
    print(f"✅ {atualizados} produtos atualizados com sucesso!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        categorizar_produtos()
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
