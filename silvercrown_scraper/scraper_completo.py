"""
Web Scraper Completo para Silver Crown - Atacado de Prata 925
Extrai informações de produtos, categorias e FAZ DOWNLOAD DE TODAS AS IMAGENS
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os
from urllib.parse import urljoin, urlparse
from pathlib import Path
from typing import List, Dict
import hashlib


class SilverCrownScraperCompleto:
    def __init__(self, base_dir: str = "."):
        self.base_url = "https://silvercrown.com.br"
        self.base_dir = Path(base_dir)
        self.images_dir = self.base_dir / "imagens"
        self.data_dir = self.base_dir / "dados"
        
        # Criar diretórios se não existirem
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        self.downloaded_images = set()
        self.stats = {
            'produtos': 0,
            'categorias': 0,
            'imagens': 0,
            'erros': 0
        }

    def get_page_content(self, url: str) -> BeautifulSoup:
        """Obtém o conteúdo HTML de uma página"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"❌ Erro ao acessar {url}: {e}")
            self.stats['erros'] += 1
            return None

    def download_image(self, img_url: str, product_name: str, category_name: str) -> str:
        """Baixa uma imagem e salva localmente"""
        if not img_url or img_url in self.downloaded_images:
            return None
        
        try:
            # Limpar nomes para usar como diretório
            safe_category = re.sub(r'[^\w\s-]', '', category_name).strip().replace(' ', '_')
            safe_product = re.sub(r'[^\w\s-]', '', product_name).strip().replace(' ', '_')[:50]
            
            # Criar subdiretório por categoria
            category_dir = self.images_dir / safe_category
            category_dir.mkdir(exist_ok=True)
            
            # Gerar nome único para a imagem
            img_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
            ext = Path(urlparse(img_url).path).suffix or '.jpg'
            filename = f"{safe_product}_{img_hash}{ext}"
            filepath = category_dir / filename
            
            # Baixar imagem se não existir
            if not filepath.exists():
                response = self.session.get(img_url, timeout=10, stream=True)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self.downloaded_images.add(img_url)
                self.stats['imagens'] += 1
                print(f"   📥 Imagem baixada: {filename}")
                
            return str(filepath.relative_to(self.base_dir))
        
        except Exception as e:
            print(f"   ⚠️  Erro ao baixar imagem {img_url}: {e}")
            self.stats['erros'] += 1
            return None

    def extract_categories(self) -> List[Dict]:
        """Extrai todas as categorias de produtos"""
        print("\n🔍 Extraindo categorias...")
        soup = self.get_page_content(self.base_url)
        if not soup:
            return []

        categories = []
        seen_urls = set()
        
        # Procura por links de categorias no menu e no corpo
        category_patterns = [
            soup.find_all('a', href=re.compile(r'/categoria-')),
            soup.find_all('a', href=re.compile(r'/categoria'))
        ]
        
        for pattern in category_patterns:
            for link in pattern:
                href = link.get('href')
                if not href:
                    continue
                    
                full_url = urljoin(self.base_url, href)
                
                if full_url not in seen_urls and '/categoria' in full_url:
                    seen_urls.add(full_url)
                    category = {
                        'nome': link.get_text(strip=True),
                        'url': full_url,
                        'slug': href
                    }
                    categories.append(category)
        
        self.stats['categorias'] = len(categories)
        print(f"✅ {len(categories)} categorias encontradas")
        return categories

    def extract_all_images_from_product_page(self, product_url: str, product_name: str, category_name: str) -> List[str]:
        """Extrai e baixa todas as imagens de um produto"""
        soup = self.get_page_content(product_url)
        if not soup:
            return []
        
        images = []
        
        # Procurar imagens em várias tags possíveis
        img_selectors = [
            soup.find_all('img', {'data-src': True}),
            soup.find_all('img', {'src': True}),
            soup.find_all('img', class_=re.compile(r'product|image')),
            soup.find_all('div', {'data-image': True})
        ]
        
        for selector in img_selectors:
            for tag in selector:
                img_url = tag.get('data-src') or tag.get('src') or tag.get('data-image')
                
                if img_url and any(x in img_url.lower() for x in ['product', 'stores', '.jpg', '.png', '.webp']):
                    full_img_url = urljoin(self.base_url, img_url)
                    local_path = self.download_image(full_img_url, product_name, category_name)
                    if local_path:
                        images.append({
                            'url_original': full_img_url,
                            'caminho_local': local_path
                        })
        
        return images

    def extract_product_info(self, product_url: str, category_name: str) -> Dict:
        """Extrai informações COMPLETAS de um produto"""
        print(f"   📦 Processando: {product_url}")
        soup = self.get_page_content(product_url)
        if not soup:
            return None

        product = {
            'url': product_url,
            'titulo': '',
            'preco': '',
            'preco_original': '',
            'desconto': '',
            'descricao': '',
            'descricao_completa': '',
            'imagens': [],
            'especificacoes': {},
            'estoque': '',
            'sku': '',
            'categoria': category_name
        }

        # Título
        title_selectors = [
            soup.find('h1', class_='product-title'),
            soup.find('h1', itemprop='name'),
            soup.find('h1')
        ]
        for selector in title_selectors:
            if selector:
                product['titulo'] = selector.get_text(strip=True)
                break

        # Preços
        price_selectors = [
            soup.find('span', class_='price-compare'),
            soup.find('span', id='price_display'),
            soup.find('span', itemprop='price')
        ]
        for selector in price_selectors:
            if selector:
                product['preco'] = selector.get_text(strip=True)
                break

        # Preço original
        original_price = soup.find('span', class_='price-original')
        if original_price:
            product['preco_original'] = original_price.get_text(strip=True)

        # Desconto
        discount_selectors = [
            soup.find('span', class_='badge-product'),
            soup.find('span', class_='badge'),
            soup.find('div', class_='discount-badge')
        ]
        for selector in discount_selectors:
            if selector:
                product['desconto'] = selector.get_text(strip=True)
                break

        # Descrição curta
        desc_tag = soup.find('div', class_='product-description')
        if desc_tag:
            product['descricao'] = desc_tag.get_text(strip=True)

        # Descrição completa
        full_desc = soup.find('div', id='description') or soup.find('div', class_='description')
        if full_desc:
            product['descricao_completa'] = full_desc.get_text(strip=True)

        # SKU
        sku_tag = soup.find('span', class_='sku') or soup.find('div', class_='sku')
        if sku_tag:
            product['sku'] = sku_tag.get_text(strip=True)

        # Baixar TODAS as imagens do produto
        if product['titulo']:
            product['imagens'] = self.extract_all_images_from_product_page(
                product_url, 
                product['titulo'], 
                category_name
            )
            print(f"      🖼️  {len(product['imagens'])} imagens baixadas")

        self.stats['produtos'] += 1
        return product

    def extract_products_from_category(self, category_url: str, category_name: str, max_products: int = 50) -> List[Dict]:
        """Extrai produtos de uma categoria"""
        print(f"\n📂 Categoria: {category_name}")
        print(f"   🔗 URL: {category_url}")
        
        soup = self.get_page_content(category_url)
        if not soup:
            return []

        products = []
        unique_urls = set()
        
        # Procura por links de produtos
        product_links = soup.find_all('a', href=re.compile(r'/produtos/'))
        
        for link in product_links:
            product_url = urljoin(self.base_url, link.get('href'))
            
            if product_url not in unique_urls and len(unique_urls) < max_products:
                unique_urls.add(product_url)
                
                # Extrai informações COMPLETAS do produto
                product = self.extract_product_info(product_url, category_name)
                if product:
                    products.append(product)
                
                # Delay para não sobrecarregar
                time.sleep(1)

        print(f"   ✅ {len(products)} produtos coletados\n")
        return products

    def scrape_all(self, max_products_per_category: int = 20, max_categories: int = None) -> Dict:
        """Realiza scraping COMPLETO com download de imagens"""
        print("="*60)
        print("🚀 INICIANDO SCRAPING COMPLETO - SILVER CROWN")
        print("="*60)
        
        data = {
            'site': 'Silver Crown',
            'url': self.base_url,
            'data_coleta': time.strftime('%Y-%m-%d %H:%M:%S'),
            'categorias': [],
            'estatisticas': {}
        }

        # Extrai categorias
        categories = self.extract_categories()
        
        # Limita categorias se especificado
        if max_categories:
            categories = categories[:max_categories]
        
        # Processa cada categoria
        for i, category in enumerate(categories, 1):
            print(f"\n{'='*60}")
            print(f"📊 Progresso: {i}/{len(categories)} categorias")
            print(f"{'='*60}")
            
            # Extrai produtos com todas as imagens
            products = self.extract_products_from_category(
                category['url'],
                category['nome'],
                max_products=max_products_per_category
            )
            
            category['produtos'] = products
            category['total_produtos'] = len(products)
            data['categorias'].append(category)
            
            # Salvar progresso a cada categoria
            self.save_progress(data, f"backup_categoria_{i}.json")
            
            # Delay entre categorias
            time.sleep(2)

        # Estatísticas finais
        data['estatisticas'] = self.stats
        
        print("\n" + "="*60)
        print("✅ SCRAPING CONCLUÍDO!")
        print("="*60)
        self.print_statistics()
        
        return data

    def save_progress(self, data: Dict, filename: str):
        """Salva progresso durante o scraping"""
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_to_json(self, data: Dict, filename: str = 'silvercrown_completo.json'):
        """Salva dados completos em JSON"""
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Dados salvos em: {filepath}")

    def save_to_csv(self, data: Dict, filename: str = 'silvercrown_completo.csv'):
        """Salva dados em CSV"""
        import csv
        
        filepath = self.data_dir / filename
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'categoria', 'titulo', 'preco', 'preco_original', 'desconto', 
                'url', 'sku', 'total_imagens', 'primeira_imagem_local'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for category in data['categorias']:
                for product in category['produtos']:
                    primeira_imagem = product['imagens'][0]['caminho_local'] if product['imagens'] else ''
                    writer.writerow({
                        'categoria': category['nome'],
                        'titulo': product['titulo'],
                        'preco': product.get('preco', ''),
                        'preco_original': product.get('preco_original', ''),
                        'desconto': product.get('desconto', ''),
                        'url': product['url'],
                        'sku': product.get('sku', ''),
                        'total_imagens': len(product['imagens']),
                        'primeira_imagem_local': primeira_imagem
                    })
        
        print(f"💾 CSV salvo em: {filepath}")

    def create_html_catalog(self, data: Dict, filename: str = 'catalogo.html'):
        """Cria um catálogo HTML com as imagens locais"""
        filepath = self.data_dir / filename
        
        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catálogo Silver Crown - {data['data_coleta']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
        .header {{ background: #333; color: white; padding: 20px; text-align: center; margin-bottom: 30px; }}
        .stats {{ background: white; padding: 20px; margin-bottom: 30px; border-radius: 8px; }}
        .category {{ margin-bottom: 40px; }}
        .category-title {{ background: #2196F3; color: white; padding: 15px; font-size: 24px; margin-bottom: 20px; }}
        .products {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }}
        .product {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .product img {{ width: 100%; height: 200px; object-fit: cover; border-radius: 4px; }}
        .product-title {{ font-size: 14px; margin: 10px 0; font-weight: bold; min-height: 40px; }}
        .product-price {{ color: #4CAF50; font-size: 18px; font-weight: bold; }}
        .product-discount {{ background: #ff5722; color: white; padding: 5px 10px; display: inline-block; border-radius: 4px; }}
        .product-link {{ display: block; margin-top: 10px; color: #2196F3; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏆 Catálogo Silver Crown</h1>
        <p>Dados coletados em: {data['data_coleta']}</p>
    </div>
    
    <div class="stats">
        <h2>📊 Estatísticas</h2>
        <p><strong>Categorias:</strong> {len(data['categorias'])}</p>
        <p><strong>Produtos:</strong> {data['estatisticas']['produtos']}</p>
        <p><strong>Imagens baixadas:</strong> {data['estatisticas']['imagens']}</p>
    </div>
"""
        
        for category in data['categorias']:
            html_content += f"""
    <div class="category">
        <div class="category-title">{category['nome']} ({len(category['produtos'])} produtos)</div>
        <div class="products">
"""
            for product in category['produtos']:
                first_image = product['imagens'][0]['caminho_local'] if product['imagens'] else ''
                img_path = '../' + first_image.replace('\\', '/') if first_image else ''
                
                html_content += f"""
            <div class="product">
                <img src="{img_path}" alt="{product['titulo']}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22%3E%3Crect fill=%22%23ddd%22 width=%22200%22 height=%22200%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22%3ESem imagem%3C/text%3E%3C/svg%3E'">
                <div class="product-title">{product['titulo']}</div>
                {f'<span class="product-discount">{product["desconto"]}</span>' if product['desconto'] else ''}
                <div class="product-price">{product['preco']}</div>
                {f'<div style="text-decoration: line-through; color: #999;">{product["preco_original"]}</div>' if product['preco_original'] else ''}
                <a href="{product['url']}" class="product-link" target="_blank">Ver online</a>
                <p style="font-size: 12px; color: #666; margin-top: 5px;">{len(product['imagens'])} imagens</p>
            </div>
"""
            
            html_content += """
        </div>
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"🌐 Catálogo HTML criado em: {filepath}")

    def print_statistics(self):
        """Imprime estatísticas do scraping"""
        print(f"\n📈 ESTATÍSTICAS:")
        print(f"   ✅ Categorias: {self.stats['categorias']}")
        print(f"   ✅ Produtos: {self.stats['produtos']}")
        print(f"   ✅ Imagens baixadas: {self.stats['imagens']}")
        print(f"   ❌ Erros: {self.stats['erros']}")
        print(f"\n📁 Arquivos salvos em: {self.base_dir.absolute()}")


def main():
    """Função principal"""
    
    # Configurações
    BASE_DIR = "."  # Diretório atual
    MAX_PRODUTOS_POR_CATEGORIA = 15  # Ajuste conforme necessário
    MAX_CATEGORIAS = 10  # None para todas, ou número para limitar
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          🚀 SCRAPER COMPLETO SILVER CROWN 🚀                ║
║                                                              ║
║  📦 Coleta produtos, categorias e imagens                   ║
║  💾 Salva tudo localmente                                    ║
║  🖼️  Baixa todas as fotos dos produtos                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    scraper = SilverCrownScraperCompleto(base_dir=BASE_DIR)
    
    # Realiza scraping completo
    data = scraper.scrape_all(
        max_products_per_category=MAX_PRODUTOS_POR_CATEGORIA,
        max_categories=MAX_CATEGORIAS
    )
    
    # Salva resultados em múltiplos formatos
    scraper.save_to_json(data)
    scraper.save_to_csv(data)
    scraper.create_html_catalog(data)
    
    print(f"\n{'='*60}")
    print("🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
