"""
Web Scraper Completo para Atacado de Prata
Extrai informações de produtos, categorias e FAZ DOWNLOAD DE TODAS AS IMAGENS
Site: https://atacadodeprata.rdi.store/s/jessica
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os
from urllib.parse import urljoin, urlparse, parse_qs
from pathlib import Path
from typing import List, Dict
import hashlib


class AtacadoDePrataScraper:
    def __init__(self, base_dir: str = "atacadodeprata_data"):
        self.base_url = "https://atacadodeprata.rdi.store"
        self.store_path = "/s/jessica"
        self.full_url = self.base_url + self.store_path
        
        self.base_dir = Path(base_dir)
        self.images_dir = self.base_dir / "imagens"
        self.data_dir = self.base_dir / "dados"
        
        # Criar diretórios
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
            # Limpar nomes
            safe_category = re.sub(r'[^\w\s-]', '', category_name).strip().replace(' ', '_')
            safe_product = re.sub(r'[^\w\s-]', '', product_name).strip().replace(' ', '_')[:50]
            
            # Criar subdiretório por categoria
            category_dir = self.images_dir / safe_category
            category_dir.mkdir(exist_ok=True)
            
            # Nome único para imagem
            img_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
            ext = Path(urlparse(img_url).path).suffix or '.jpg'
            filename = f"{safe_product}_{img_hash}{ext}"
            filepath = category_dir / filename
            
            # Baixar se não existir
            if not filepath.exists():
                # URL completa da imagem
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = self.base_url + img_url
                
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
            print(f"   ⚠️  Erro ao baixar imagem: {e}")
            self.stats['erros'] += 1
            return None

    def extract_categories(self) -> List[Dict]:
        """Extrai todas as categorias"""
        print("\n🔍 Extraindo categorias...")
        soup = self.get_page_content(self.full_url)
        if not soup:
            return []

        categories = []
        seen_cats = set()
        
        # Procura por categorias na barra lateral ou menu
        category_elements = soup.find_all(['a', 'button'], string=re.compile(r'\w+'))
        
        # Lista de categorias conhecidas do site
        known_categories = [
            'ALIANÇA', 'ANEIS', 'ANEIS MASCULINO', 'ARGOLAS', 'BERLOQUES', 
            'BRINCO BABY', 'BRINCOS', 'CHOCKER', 'COLAR + GARGANTILHAS', 
            'CONJUNTO', 'CORRENTE MASCULINA', 'CORRENTES FEMININAS', 
            'GARGANTILHA LETRA', 'PANDORAS', 'PIERCING', 'PINGENTE CRAVAÇÃO INGLESA',
            'PINGENTE MASCULINO', 'PINGENTES FEMININOS', 'PONTO DE LUZ',
            'PULSEIRA', 'PULSEIRA BABY', 'PULSEIRA FEMININA ESPECIAL',
            'PULSEIRA FEMININA ITALIANA', 'PULSEIRA MASCULINA', 'RIVIERAS',
            'TERÇO', 'TORNOZELEIRA'
        ]
        
        # Adicionar categorias conhecidas
        for cat_name in known_categories:
            if cat_name not in seen_cats:
                seen_cats.add(cat_name)
                # URL com filtro de categoria
                cat_url = f"{self.full_url}?categoria={cat_name.replace(' ', '%20')}"
                categories.append({
                    'nome': cat_name,
                    'url': cat_url,
                    'slug': cat_name.lower().replace(' ', '-')
                })
        
        self.stats['categorias'] = len(categories)
        print(f"✅ {len(categories)} categorias encontradas")
        return categories

    def extract_products_from_page(self, page_url: str, category_name: str = "Geral") -> List[Dict]:
        """Extrai produtos de uma página"""
        print(f"\n📂 Extraindo produtos de: {category_name}")
        soup = self.get_page_content(page_url)
        if not soup:
            return []

        products = []
        
        # Procurar por todos os elementos que contêm código de produto (K2-80, P3-10, etc)
        all_text_elements = soup.find_all(string=re.compile(r'[A-Z][0-9]+-[0-9]+'))
        
        product_containers = []
        for text_elem in all_text_elements:
            # Pegar o container pai que tem o produto completo
            container = text_elem.find_parent(['div', 'article', 'li', 'tr'])
            if container and container not in product_containers:
                product_containers.append(container)
        
        # Fallback: procurar por divs/cards de produtos
        if not product_containers:
            product_containers = soup.find_all(['div', 'article'], class_=re.compile(r'product|item|card', re.I))
        
        # Outro fallback: procurar por qualquer div que contenha preço
        if not product_containers:
            price_elements = soup.find_all(string=re.compile(r'R\$'))
            for price_elem in price_elements:
                container = price_elem.find_parent(['div', 'article', 'li'])
                if container and container not in product_containers:
                    product_containers.append(container)
        
        print(f"   🔍 Encontrados {len(product_containers)} possíveis produtos")
        
        for card in product_containers[:50]:  # Limitar a 50 produtos por categoria
            try:
                product = {
                    'categoria': category_name,
                    'titulo': '',
                    'codigo': '',
                    'preco': '',
                    'peso': '',
                    'lote': '',
                    'url': page_url,
                    'imagens': []
                }
                
                # Pegar todo o texto do container
                full_text = card.get_text(separator=' ', strip=True)
                
                # Extrair código do produto (padrão: K2-80, P3-10, J2-49, etc)
                codigo_match = re.search(r'([A-Z][0-9]+-[0-9]+)', full_text)
                if codigo_match:
                    product['codigo'] = codigo_match.group(1)
                
                # Extrair título completo
                title_elem = card.find(string=re.compile(r'[A-Z][0-9]+-[0-9]+'))
                if title_elem:
                    # Pegar a linha inteira que contém o código
                    title_parent = title_elem.find_parent()
                    if title_parent:
                        product['titulo'] = title_parent.get_text(strip=True)
                
                # Extrair preço
                price_elem = card.find(string=re.compile(r'R\$\s*[\d,\.]+'))
                if price_elem:
                    product['preco'] = price_elem.strip()
                
                # Extrair peso
                peso_elem = card.find(string=re.compile(r'Peso.*?([\d,\.]+)g', re.I))
                if peso_elem:
                    peso_match = re.search(r'([\d,\.]+)g', peso_elem)
                    if peso_match:
                        product['peso'] = peso_match.group(1) + 'g'
                
                # Extrair lote
                lote_elem = card.find(string=re.compile(r'Lote.*?([0-9]+)', re.I))
                if lote_elem:
                    lote_match = re.search(r'Lote.*?([0-9]+)', lote_elem, re.I)
                    if lote_match:
                        product['lote'] = lote_match.group(1)
                
                # Extrair imagens
                images = card.find_all('img')
                for img in images:
                    img_url = img.get('src') or img.get('data-src')
                    if img_url and 'placeholder' not in img_url.lower():
                        local_path = self.download_image(img_url, product['codigo'] or product['titulo'], category_name)
                        if local_path:
                            product['imagens'].append({
                                'url_original': img_url,
                                'caminho_local': local_path
                            })
                
                # Só adicionar se tiver pelo menos título ou código
                if product['titulo'] or product['codigo']:
                    products.append(product)
                    self.stats['produtos'] += 1
                    if product['codigo']:
                        print(f"   📦 {product['codigo']} - {product['preco']} - {len(product['imagens'])} imgs")
                    
                time.sleep(0.3)  # Delay entre produtos
                
            except Exception as e:
                print(f"   ⚠️  Erro ao processar produto: {e}")
                self.stats['erros'] += 1
                continue
        
        print(f"   ✅ {len(products)} produtos coletados")
        return products

    def scrape_all(self, max_products_per_category: int = 30, max_categories: int = 10) -> Dict:
        """Realiza scraping completo"""
        print("="*60)
        print("🚀 INICIANDO SCRAPING - ATACADO DE PRATA")
        print("="*60)
        
        data = {
            'site': 'Atacado de Prata',
            'url': self.full_url,
            'data_coleta': time.strftime('%Y-%m-%d %H:%M:%S'),
            'categorias': [],
            'estatisticas': {}
        }

        # Primeiro, coletar produtos da página principal
        print("\n📄 Coletando produtos da página principal...")
        main_products = self.extract_products_from_page(self.full_url, "Página Principal")
        if main_products:
            data['categorias'].append({
                'nome': 'Página Principal',
                'url': self.full_url,
                'produtos': main_products,
                'total_produtos': len(main_products)
            })
        
        # Extrair categorias
        categories = self.extract_categories()
        
        # Limitar categorias
        if max_categories:
            categories = categories[:max_categories]
        
        # Processar cada categoria
        for i, category in enumerate(categories, 1):
            print(f"\n{'='*60}")
            print(f"📊 Progresso: {i}/{len(categories)} categorias")
            print(f"{'='*60}")
            
            products = self.extract_products_from_page(category['url'], category['nome'])
            
            category['produtos'] = products
            category['total_produtos'] = len(products)
            data['categorias'].append(category)
            
            # Salvar backup
            self.save_progress(data, f"backup_categoria_{i}.json")
            
            time.sleep(2)  # Delay entre categorias

        # Estatísticas finais
        data['estatisticas'] = self.stats
        
        print("\n" + "="*60)
        print("✅ SCRAPING CONCLUÍDO!")
        print("="*60)
        self.print_statistics()
        
        return data

    def save_progress(self, data: Dict, filename: str):
        """Salva progresso"""
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_to_json(self, data: Dict, filename: str = 'atacadodeprata_completo.json'):
        """Salva em JSON"""
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Dados salvos em: {filepath}")

    def save_to_csv(self, data: Dict, filename: str = 'atacadodeprata_completo.csv'):
        """Salva em CSV"""
        import csv
        
        filepath = self.data_dir / filename
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'categoria', 'codigo', 'titulo', 'preco', 'peso', 'lote',
                'url', 'total_imagens', 'primeira_imagem_local'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for category in data['categorias']:
                for product in category['produtos']:
                    primeira_imagem = product['imagens'][0]['caminho_local'] if product['imagens'] else ''
                    writer.writerow({
                        'categoria': category['nome'],
                        'codigo': product.get('codigo', ''),
                        'titulo': product.get('titulo', ''),
                        'preco': product.get('preco', ''),
                        'peso': product.get('peso', ''),
                        'lote': product.get('lote', ''),
                        'url': product.get('url', ''),
                        'total_imagens': len(product['imagens']),
                        'primeira_imagem_local': primeira_imagem
                    })
        
        print(f"💾 CSV salvo em: {filepath}")

    def create_html_catalog(self, data: Dict, filename: str = 'catalogo_atacadodeprata.html'):
        """Cria catálogo HTML"""
        filepath = self.data_dir / filename
        
        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catálogo Atacado de Prata - {data['data_coleta']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; margin-bottom: 30px; }}
        .stats {{ background: white; padding: 20px; margin-bottom: 30px; border-radius: 8px; }}
        .category {{ margin-bottom: 40px; }}
        .category-title {{ background: #3498db; color: white; padding: 15px; font-size: 24px; margin-bottom: 20px; }}
        .products {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }}
        .product {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .product img {{ width: 100%; height: 200px; object-fit: cover; border-radius: 4px; }}
        .product-code {{ font-weight: bold; color: #2c3e50; margin: 10px 0; }}
        .product-price {{ color: #27ae60; font-size: 20px; font-weight: bold; }}
        .product-info {{ font-size: 12px; color: #7f8c8d; margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>💎 Catálogo Atacado de Prata</h1>
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
                <img src="{img_path}" alt="{product.get('titulo', 'Produto')}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22%3E%3Crect fill=%22%23ddd%22 width=%22200%22 height=%22200%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22%3ESem imagem%3C/text%3E%3C/svg%3E'">
                <div class="product-code">{product.get('codigo', 'N/A')}</div>
                <div class="product-price">{product.get('preco', 'Consulte')}</div>
                <div class="product-info">Peso: {product.get('peso', 'N/A')}</div>
                <div class="product-info">Lote: {product.get('lote', 'N/A')}</div>
                <div class="product-info">{len(product['imagens'])} imagens</div>
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
        """Imprime estatísticas"""
        print(f"\n📈 ESTATÍSTICAS:")
        print(f"   ✅ Categorias: {self.stats['categorias']}")
        print(f"   ✅ Produtos: {self.stats['produtos']}")
        print(f"   ✅ Imagens baixadas: {self.stats['imagens']}")
        print(f"   ❌ Erros: {self.stats['erros']}")
        print(f"\n📁 Arquivos salvos em: {self.base_dir.absolute()}")


def main():
    """Função principal"""
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║       🚀 SCRAPER COMPLETO ATACADO DE PRATA 🚀               ║
║                                                              ║
║  📦 Coleta produtos com códigos, preços e pesos             ║
║  💾 Salva tudo localmente                                    ║
║  🖼️  Baixa todas as fotos dos produtos                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    scraper = AtacadoDePrataScraper(base_dir="atacadodeprata_data")
    
    # Realiza scraping
    data = scraper.scrape_all(
        max_products_per_category=30,
        max_categories=10
    )
    
    # Salva resultados
    scraper.save_to_json(data)
    scraper.save_to_csv(data)
    scraper.create_html_catalog(data)
    
    print(f"\n{'='*60}")
    print("🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
