"""
Conversor de Catálogo PDF para SQL
Extrai informações dos PDFs e gera INSERT SQL
"""

import os
import re
import PyPDF2
from datetime import datetime

CATALOGO_DIR = "Catalogo"
OUTPUT_SQL = "catalogo_produtos.sql"

def extrair_texto_pdf(caminho_pdf):
    """Extrai texto de um arquivo PDF"""
    try:
        with open(caminho_pdf, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            texto = ""
            for page in reader.pages:
                texto += page.extract_text() + "\n"
            return texto
    except Exception as e:
        print(f"❌ Erro ao ler {caminho_pdf}: {e}")
        return ""

def processar_catalogo(arquivo, texto):
    """Processa o texto extraído e identifica produtos"""
    produtos = []
    
    # Remover nome do arquivo e extensão
    categoria = arquivo.replace('.pdf', '').replace('_', ' ')
    
    # Padrões comuns em catálogos de joias
    # Exemplo: "Código: 12345 - Descrição - R$ 45,90"
    
    # Pattern 1: Código + Descrição + Preço
    pattern1 = r'(\d{4,6})\s*[-–]\s*([^\n\r]+?)\s*[-–]?\s*R\$?\s*(\d+[,\.]\d{2})'
    matches1 = re.findall(pattern1, texto, re.IGNORECASE)
    
    for match in matches1:
        codigo, descricao, preco = match
        preco_float = float(preco.replace(',', '.'))
        
        produtos.append({
            'codigo': codigo.strip(),
            'titulo': descricao.strip()[:200],
            'categoria': categoria,
            'preco_atacado': preco_float,
            'preco_varejo': round(preco_float * 2.5, 2),  # Margem 250%
            'fonte': arquivo
        })
    
    # Pattern 2: Linhas com códigos
    pattern2 = r'(?:Cód|Código|REF|Ref)[:\s]*(\d{4,6})'
    codigos = re.findall(pattern2, texto, re.IGNORECASE)
    
    # Pattern 3: Preços
    pattern3 = r'R\$?\s*(\d+[,\.]\d{2})'
    precos = re.findall(pattern3, texto)
    
    # Se encontrou códigos mas não pelo pattern completo
    if codigos and not matches1:
        linhas = texto.split('\n')
        for linha in linhas:
            # Buscar código na linha
            cod_match = re.search(r'(\d{4,6})', linha)
            if cod_match:
                codigo = cod_match.group(1)
                # Buscar preço na mesma linha
                preco_match = re.search(r'R\$?\s*(\d+[,\.]\d{2})', linha)
                
                if preco_match:
                    preco = float(preco_match.group(1).replace(',', '.'))
                    descricao = linha.strip()[:200]
                    
                    produtos.append({
                        'codigo': codigo,
                        'titulo': descricao,
                        'categoria': categoria,
                        'preco_atacado': preco,
                        'preco_varejo': round(preco * 2.5, 2),
                        'fonte': arquivo
                    })
    
    return produtos

def gerar_sql(produtos):
    """Gera script SQL com os produtos"""
    sql = []
    
    # Header
    sql.append("-- ================================================")
    sql.append("-- Script SQL: Catálogo Griffe da Prata")
    sql.append(f"-- Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    sql.append(f"-- Total de produtos: {len(produtos)}")
    sql.append("-- ================================================\n")
    
    # Criar tabela se não existir
    sql.append("-- Criar tabela de produtos")
    sql.append("""
CREATE TABLE IF NOT EXISTS produtos_catalogo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    titulo TEXT NOT NULL,
    categoria TEXT,
    preco_atacado REAL NOT NULL,
    preco_varejo REAL NOT NULL,
    peso TEXT,
    descricao TEXT,
    imagem TEXT,
    fonte TEXT,
    data_importacao TEXT DEFAULT CURRENT_TIMESTAMP
);
""")
    
    sql.append("\n-- Inserir produtos do catálogo")
    sql.append("BEGIN TRANSACTION;\n")
    
    # Inserir produtos
    for produto in produtos:
        codigo = produto['codigo'].replace("'", "''")
        titulo = produto['titulo'].replace("'", "''")
        categoria = produto['categoria'].replace("'", "''")
        fonte = produto['fonte'].replace("'", "''")
        
        insert = f"""INSERT OR IGNORE INTO produtos_catalogo 
    (codigo, titulo, categoria, preco_atacado, preco_varejo, fonte)
VALUES 
    ('{codigo}', '{titulo}', '{categoria}', {produto['preco_atacado']}, {produto['preco_varejo']}, '{fonte}');
"""
        sql.append(insert)
    
    sql.append("\nCOMMIT;\n")
    
    # Estatísticas
    sql.append("\n-- ================================================")
    sql.append("-- Estatísticas da Importação")
    sql.append("-- ================================================")
    sql.append("SELECT categoria, COUNT(*) as total FROM produtos_catalogo GROUP BY categoria;")
    sql.append("SELECT COUNT(*) as total_produtos FROM produtos_catalogo;")
    sql.append("SELECT AVG(preco_atacado) as preco_medio_atacado, AVG(preco_varejo) as preco_medio_varejo FROM produtos_catalogo;")
    
    return '\n'.join(sql)

def main():
    """Função principal"""
    if not os.path.exists(CATALOGO_DIR):
        print(f"❌ Pasta {CATALOGO_DIR} não encontrada!")
        return
    
    print("="*60)
    print("📚 CONVERSOR DE CATÁLOGO PDF PARA SQL")
    print("="*60)
    print()
    
    arquivos_pdf = [f for f in os.listdir(CATALOGO_DIR) if f.endswith('.pdf')]
    
    if not arquivos_pdf:
        print("❌ Nenhum arquivo PDF encontrado no catálogo!")
        return
    
    print(f"📄 Encontrados {len(arquivos_pdf)} arquivos PDF\n")
    
    todos_produtos = []
    
    for arquivo in sorted(arquivos_pdf):
        caminho = os.path.join(CATALOGO_DIR, arquivo)
        print(f"🔍 Processando: {arquivo}...")
        
        texto = extrair_texto_pdf(caminho)
        
        if texto:
            produtos = processar_catalogo(arquivo, texto)
            todos_produtos.extend(produtos)
            print(f"   ✅ Encontrados {len(produtos)} produtos")
        else:
            print(f"   ⚠️  Não foi possível extrair texto")
        print()
    
    if not todos_produtos:
        print("❌ Nenhum produto foi encontrado nos PDFs!")
        print("💡 Os PDFs podem estar protegidos ou serem imagens escaneadas.")
        print("💡 Considere usar OCR (tesseract) para PDFs com imagens.")
        return
    
    # Gerar SQL
    print(f"📝 Gerando script SQL com {len(todos_produtos)} produtos...")
    sql_content = gerar_sql(todos_produtos)
    
    with open(OUTPUT_SQL, 'w', encoding='utf-8') as f:
        f.write(sql_content)
    
    print(f"✅ Arquivo SQL gerado: {OUTPUT_SQL}")
    print()
    print("="*60)
    print("📊 RESUMO DA CONVERSÃO")
    print("="*60)
    
    # Estatísticas por categoria
    categorias = {}
    for p in todos_produtos:
        cat = p['categoria']
        categorias[cat] = categorias.get(cat, 0) + 1
    
    for cat, total in sorted(categorias.items()):
        print(f"  • {cat}: {total} produtos")
    
    print()
    print(f"📦 Total de produtos: {len(todos_produtos)}")
    
    # Preço médio
    preco_medio = sum(p['preco_atacado'] for p in todos_produtos) / len(todos_produtos)
    print(f"💰 Preço médio atacado: R$ {preco_medio:.2f}")
    print()
    print("="*60)
    print("✨ Conversão concluída com sucesso!")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Erro durante a conversão: {e}")
        import traceback
        traceback.print_exc()
