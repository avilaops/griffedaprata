"""
Scraper Atacado de Prata - Versão Simplificada
Foca na página principal que já tem produtos carregados
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from pathlib import Path
from urllib.parse import urljoin
import hashlib


def main():
    print("🚀 Scraper Atacado de Prata - Iniciando...\n")
    
    # Configuração
    base_url = "https://atacadodeprata.rdi.store"
    page_url = "https://atacadodeprata.rdi.store/s/jessica"
    
    # Criar diretórios
    base_dir = Path("atacadodeprata_data")
    images_dir = base_dir / "imagens" / "todos_produtos"
    data_dir = base_dir / "dados"
    images_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    # Buscar página
    print(f"📡 Acessando: {page_url}")
    response = requests.get(page_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Salvar HTML para debug
    with open(data_dir / "pagina_completa.html", 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("✅ HTML salvo para análise: dados/pagina_completa.html\n")
    
    # Estratégia 1: Buscar qualquer texto que pareça um produto
    print("🔍 Buscando produtos...")
    products = []
    
    # Procurar por códigos de produto (K2-80, P3-10, etc)
    codigo_pattern = r'([A-Z][0-9]+-[0-9]+)'
    preco_pattern = r'R\$\s*[\d,\.]+'
    peso_pattern = r'Peso.*?([\d,\.]+)g'
    lote_pattern = r'Lote.*?([0-9]+)'
    
    # Buscar todo o texto da página
    page_text = soup.get_text()
    
    # Encontrar todos os códigos de produto
    codigos = re.findall(codigo_pattern, page_text)
    print(f"   📦 Encontrados {len(codigos)} códigos de produto")
    
    # Para cada código, tentar encontrar informações relacionadas
    for codigo in set(codigos):  # Usar set para evitar duplicatas
        try:
            # Encontrar o elemento que contém este código
            elemento = soup.find(string=re.compile(re.escape(codigo)))
            if not elemento:
                continue
            
            # Pegar o container pai
            container = elemento.find_parent(['div', 'article', 'li', 'tr', 'td'])
            if not container:
                container = elemento.find_parent()
            
            if not container:
                continue
            
            # Extrair informações do container
            container_text = container.get_text(separator=' ', strip=True)
            
            product = {
                'codigo': codigo,
                'titulo': '',
                'preco': '',
                'peso': '',
                'lote': '',
                'imagens': []
            }
            
            # Buscar preço
            preco_match = re.search(preco_pattern, container_text)
            if preco_match:
                product['preco'] = preco_match.group(0)
            
            # Buscar peso
            peso_match = re.search(peso_pattern, container_text, re.I)
            if peso_match:
                product['peso'] = peso_match.group(1) + 'g'
            
            # Buscar lote
            lote_match = re.search(lote_pattern, container_text, re.I)
            if lote_match:
                product['lote'] = lote_match.group(1)
            
            # Título é a parte antes do peso
            titulo_match = re.search(rf'{re.escape(codigo)}(.+?)(?:Peso|R\$|$)', container_text, re.I)
            if titulo_match:
                product['titulo'] = (codigo + titulo_match.group(1)).strip()
            else:
                product['titulo'] = codigo
            
            # Buscar imagens no container
            images = container.find_all('img')
            for img in images:
                img_url = img.get('src') or img.get('data-src')
                if img_url and 'placeholder' not in img_url.lower():
                    # Completar URL
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = base_url + img_url
                    
                    # Baixar imagem
                    try:
                        img_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
                        ext = Path(img_url).suffix or '.jpg'
                        filename = f"{codigo}_{img_hash}{ext}"
                        filepath = images_dir / filename
                        
                        if not filepath.exists():
                            img_response = requests.get(img_url, timeout=10)
                            with open(filepath, 'wb') as f:
                                f.write(img_response.content)
                            print(f"   📥 {codigo} - Imagem baixada")
                        
                        product['imagens'].append({
                            'url_original': img_url,
                            'caminho_local': str(filepath.relative_to(base_dir))
                        })
                    except Exception as e:
                        print(f"   ⚠️  Erro ao baixar imagem: {e}")
                    
                    time.sleep(0.3)
            
            products.append(product)
            print(f"   ✅ {product['codigo']} - {product['preco']} - {len(product['imagens'])} imgs")
            
        except Exception as e:
            print(f"   ⚠️  Erro ao processar {codigo}: {e}")
            continue
    
    # Salvar resultados
    data = {
        'site': 'Atacado de Prata',
        'url': page_url,
        'total_produtos': len(products),
        'produtos': products
    }
    
    # JSON
    json_file = data_dir / 'atacadodeprata_produtos.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n💾 JSON salvo: {json_file}")
    
    # CSV
    import csv
    csv_file = data_dir / 'atacadodeprata_produtos.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['codigo', 'titulo', 'preco', 'peso', 'lote', 'total_imagens'])
        writer.writeheader()
        for p in products:
            writer.writerow({
                'codigo': p['codigo'],
                'titulo': p['titulo'],
                'preco': p['preco'],
                'peso': p['peso'],
                'lote': p['lote'],
                'total_imagens': len(p['imagens'])
            })
    print(f"💾 CSV salvo: {csv_file}")
    
    # HTML simples
    html_file = data_dir / 'catalogo_simples.html'
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Atacado de Prata - Produtos</title>
    <style>
        body {{ font-family: Arial; background: #f5f5f5; padding: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .products {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }}
        .product {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .product img {{ width: 100%; height: 200px; object-fit: cover; border-radius: 4px; }}
        .code {{ font-weight: bold; color: #2c3e50; margin: 10px 0; }}
        .price {{ color: #27ae60; font-size: 18px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>💎 Atacado de Prata</h1>
        <p>Total de produtos: {len(products)}</p>
    </div>
    <div class="products">
"""
    
    for product in products:
        first_img = product['imagens'][0]['caminho_local'] if product['imagens'] else ''
        img_path = '../' + first_img.replace('\\', '/') if first_img else ''
        
        html_content += f"""
        <div class="product">
            <img src="{img_path}" alt="{product['codigo']}">
            <div class="code">{product['codigo']}</div>
            <div class="price">{product['preco']}</div>
            <div>Peso: {product['peso']}</div>
            <div>Lote: {product['lote']}</div>
            <div style="font-size: 12px; color: #666;">{len(product['imagens'])} imagens</div>
        </div>
"""
    
    html_content += """
    </div>
</body>
</html>
"""
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"🌐 HTML salvo: {html_file}")
    
    print(f"\n{'='*60}")
    print(f"✅ CONCLUÍDO!")
    print(f"   📦 Produtos coletados: {len(products)}")
    print(f"   📁 Pasta: {base_dir.absolute()}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
