"""
Conversor de Catálogo PDF para SQL com OCR
Para PDFs com imagens escaneadas
"""

import os
from datetime import datetime

CATALOGO_DIR = "Catalogo"
OUTPUT_SQL = "catalogo_produtos.sql"

def criar_sql_template():
    """Cria um template SQL para entrada manual de produtos"""
    
    arquivos_pdf = [f for f in os.listdir(CATALOGO_DIR) if f.endswith('.pdf')]
    
    sql = []
    
    # Header
    sql.append("-- ================================================")
    sql.append("-- Script SQL: Catálogo Griffe da Prata")
    sql.append(f"-- Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    sql.append("-- ATENÇÃO: PDFs são imagens - Preencher manualmente")
    sql.append("-- ================================================\n")
    
    # Criar tabela
    sql.append("""-- Criar tabela de produtos do catálogo
CREATE TABLE IF NOT EXISTS produtos_catalogo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    titulo TEXT NOT NULL,
    categoria TEXT,
    preco_atacado REAL NOT NULL,
    preco_varejo REAL NOT NULL,
    peso TEXT,
    material TEXT DEFAULT 'Prata 925',
    descricao TEXT,
    imagem TEXT,
    estoque INTEGER DEFAULT 0,
    ativo INTEGER DEFAULT 1,
    fonte TEXT,
    data_importacao TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_codigo ON produtos_catalogo(codigo);
CREATE INDEX IF NOT EXISTS idx_categoria ON produtos_catalogo(categoria);
CREATE INDEX IF NOT EXISTS idx_ativo ON produtos_catalogo(ativo);
""")
    
    sql.append("\n-- ================================================")
    sql.append("-- PRODUTOS PARA INSERIR MANUALMENTE")
    sql.append("-- ================================================")
    sql.append("-- Arquivos encontrados no catálogo:")
    
    for arquivo in sorted(arquivos_pdf):
        categoria = arquivo.replace('.pdf', '').replace('_', ' ')
        sql.append(f"-- • {categoria}")
    
    sql.append("\n-- Template de INSERT (copie e preencha para cada produto):")
    sql.append("BEGIN TRANSACTION;\n")
    
    # Templates para cada categoria
    categorias_exemplos = {
        "FEMININA": [
            ("F001", "Anel Solitário Prata 925", 25.00, 62.50, "3g"),
            ("F002", "Brinco Argola Média", 30.00, 75.00, "4g"),
            ("F003", "Colar Corrente Veneziana", 45.00, 112.50, "5g"),
        ],
        "MASCULINA": [
            ("M001", "Pulseira Groumet 8mm", 120.00, 300.00, "25g"),
            ("M002", "Corrente Cartier 60cm", 180.00, 450.00, "30g"),
            ("M003", "Anel Quadrado Liso", 55.00, 137.50, "8g"),
        ],
        "FECHO": [
            ("FC01", "Fecho Lagosta 10mm", 5.00, 12.50, "0.5g"),
            ("FC02", "Fecho Boia 8mm", 4.00, 10.00, "0.3g"),
        ],
        "LINHA ESPECIAL": [
            ("LE01", "Pingente Cruz Cravejada", 85.00, 212.50, "6g"),
            ("LE02", "Conjunto Coração Zircônia", 150.00, 375.00, "10g"),
        ]
    }
    
    sql.append("-- EXEMPLOS (substitua com seus dados reais):\n")
    
    for categoria, produtos in categorias_exemplos.items():
        sql.append(f"\n-- Categoria: {categoria}")
        for codigo, titulo, preco_atac, preco_var, peso in produtos:
            insert = f"""INSERT INTO produtos_catalogo (codigo, titulo, categoria, preco_atacado, preco_varejo, peso, fonte)
VALUES ('{codigo}', '{titulo}', '{categoria}', {preco_atac}, {preco_var}, '{peso}', '{categoria}.pdf');
"""
            sql.append(insert)
    
    sql.append("\nCOMMIT;\n")
    
    # Queries úteis
    sql.append("\n-- ================================================")
    sql.append("-- QUERIES ÚTEIS")
    sql.append("-- ================================================\n")
    
    sql.append("-- Ver todos os produtos por categoria")
    sql.append("-- SELECT categoria, COUNT(*) as total FROM produtos_catalogo GROUP BY categoria;\n")
    
    sql.append("-- Ver produtos mais caros")
    sql.append("-- SELECT codigo, titulo, preco_varejo FROM produtos_catalogo ORDER BY preco_varejo DESC LIMIT 10;\n")
    
    sql.append("-- Calcular preço médio por categoria")
    sql.append("-- SELECT categoria, AVG(preco_atacado) as media_atacado, AVG(preco_varejo) as media_varejo FROM produtos_catalogo GROUP BY categoria;\n")
    
    sql.append("-- Total de produtos ativos")
    sql.append("-- SELECT COUNT(*) as total_ativos FROM produtos_catalogo WHERE ativo = 1;\n")
    
    sql.append("-- Produtos sem estoque")
    sql.append("-- SELECT codigo, titulo, categoria FROM produtos_catalogo WHERE estoque = 0;\n")
    
    return '\n'.join(sql)

def criar_csv_template():
    """Cria arquivo CSV para facilitar entrada de dados"""
    csv = []
    csv.append("codigo,titulo,categoria,preco_atacado,preco_varejo,peso,descricao,fonte")
    csv.append("# PREENCHA OS DADOS ABAIXO (pode importar depois para SQL)")
    csv.append("# Formato: CODIGO,TITULO,CATEGORIA,PREÇO_ATACADO,PREÇO_VAREJO,PESO,DESCRIÇÃO,FONTE_PDF")
    csv.append("# Exemplo:")
    csv.append("F001,Anel Solitário Prata 925,FEMININA,25.00,62.50,3g,Anel de prata com zircônia,FEMININA.pdf")
    csv.append("M001,Pulseira Groumet 8mm,MASCULINA,120.00,300.00,25g,Pulseira masculina groumet,MASCULINA.pdf")
    csv.append("")
    csv.append("# SEUS PRODUTOS:")
    csv.append("#codigo,titulo,categoria,preco_atacado,preco_varejo,peso,descricao,fonte")
    
    with open("catalogo_template.csv", 'w', encoding='utf-8') as f:
        f.write('\n'.join(csv))
    
    print("📋 Criado: catalogo_template.csv (para entrada manual de dados)")

def main():
    print("="*70)
    print("📚 CONVERSOR DE CATÁLOGO PDF PARA SQL")
    print("="*70)
    print()
    
    if not os.path.exists(CATALOGO_DIR):
        print(f"❌ Pasta {CATALOGO_DIR} não encontrada!")
        return
    
    arquivos_pdf = [f for f in os.listdir(CATALOGO_DIR) if f.endswith('.pdf')]
    
    if not arquivos_pdf:
        print("❌ Nenhum arquivo PDF encontrado!")
        return
    
    print(f"📄 Encontrados {len(arquivos_pdf)} arquivos PDF:")
    for arquivo in sorted(arquivos_pdf):
        print(f"   • {arquivo}")
    
    print()
    print("⚠️  ATENÇÃO: Os PDFs contêm imagens escaneadas!")
    print("   Não é possível extrair texto automaticamente.")
    print()
    print("💡 SOLUÇÃO: Criando templates para entrada manual...")
    print()
    
    # Criar SQL template
    sql_content = criar_sql_template()
    
    with open(OUTPUT_SQL, 'w', encoding='utf-8') as f:
        f.write(sql_content)
    
    print(f"✅ Criado: {OUTPUT_SQL}")
    
    # Criar CSV template
    criar_csv_template()
    
    print()
    print("="*70)
    print("📝 PRÓXIMOS PASSOS:")
    print("="*70)
    print()
    print("1. Abra os PDFs do catálogo manualmente")
    print("2. Preencha o arquivo catalogo_template.csv com os dados")
    print("3. OU edite catalogo_produtos.sql diretamente")
    print("4. Execute o SQL no banco de dados:")
    print("   sqlite3 pedidos.db < catalogo_produtos.sql")
    print()
    print("💡 DICA: Use o CSV se tiver muitos produtos (mais fácil editar)")
    print()
    print("="*70)

if __name__ == "__main__":
    main()
