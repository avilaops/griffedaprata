"""
Web Scraper para Silver Crown - Atacado de Prata 925
Extrai informações de produtos, categorias e imagens do site
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin
from typing import List, Dict


class SilverCrownScraper:
    def __init__(self):
        self.base_url = "https://silvercrown.com.br"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_page_content(self, url: str) -> BeautifulSoup:
        """Obtém o conteúdo HTML de uma página"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Erro ao acessar {url}: {e}")
            return None

    def extract_categories(self) -> List[Dict]:
        """Extrai todas as categorias de produtos"""
        print("Extraindo categorias...")
        soup = self.get_page_content(self.base_url)
        if not soup:
            return []

        categories = []
        
        # Procura por links de categorias no menu
        category_links = soup.find_all('a', href=re.compile(r'/categoria-'))
        
        for link in category_links:
            category = {
                'nome': link.get_text(strip=True),
                'url': urljoin(self.base_url, link.get('href')),
                'slug': link.get('href')
            }
            if category not in categories:
                categories.append(category)
        
        print(f"✓ {len(categories)} categorias encontradas")
        return categories

    def extract_product_info(self, product_url: str) -> Dict:
        """Extrai informações detalhadas de um produto específico"""
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
            'imagens': [],
            'especificacoes': {},
            'estoque': ''
        }

        # Título do produto
        title_tag = soup.find('h1', class_='product-title') or soup.find('h1')
        if title_tag:
            product['titulo'] = title_tag.get_text(strip=True)

        # Preços
        price_tag = soup.find('span', class_='price-compare') or soup.find('span', {'id': 'price_display'})
        if price_tag:
            product['preco'] = price_tag.get_text(strip=True)

        # Preço original (se tiver desconto)
        original_price = soup.find('span', class_='price-original')
        if original_price:
            product['preco_original'] = original_price.get_text(strip=True)

        # Desconto
        discount_tag = soup.find('span', class_='badge-product')
        if discount_tag:
            product['desconto'] = discount_tag.get_text(strip=True)

        # Descrição
        desc_tag = soup.find('div', class_='product-description') or soup.find('div', {'id': 'description'})
        if desc_tag:
            product['descricao'] = desc_tag.get_text(strip=True)

        # Imagens
        image_tags = soup.find_all('img', {'data-src': True})
        for img in image_tags:
            img_url = img.get('data-src') or img.get('src')
            if img_url and 'producto' in img_url:
                product['imagens'].append(urljoin(self.base_url, img_url))

        # Especificações (tamanho, material, etc)
        specs_div = soup.find('div', class_='product-specs')
        if specs_div:
            specs = specs_div.find_all('li')
            for spec in specs:
                text = spec.get_text(strip=True)
                if ':' in text:
                    key, value = text.split(':', 1)
                    product['especificacoes'][key.strip()] = value.strip()

        return product

    def extract_products_from_category(self, category_url: str, max_products: int = 20) -> List[Dict]:
        """Extrai produtos de uma categoria específica"""
        print(f"Extraindo produtos de: {category_url}")
        soup = self.get_page_content(category_url)
        if not soup:
            return []

        products = []
        
        # Procura por links de produtos
        product_links = soup.find_all('a', href=re.compile(r'/produtos/'))
        
        unique_urls = set()
        for link in product_links:
            product_url = urljoin(self.base_url, link.get('href'))
            if product_url not in unique_urls and len(unique_urls) < max_products:
                unique_urls.add(product_url)
                
                # Extrai informações básicas do card do produto
                product_card = link.find_parent('div', class_='item-product')
                product = {
                    'url': product_url,
                    'titulo': '',
                    'preco': '',
                    'desconto': '',
                    'imagem': ''
                }
                
                # Título
                title_tag = link.find('h4') or link.find('h3') or link.find('div', class_='title')
                if title_tag:
                    product['titulo'] = title_tag.get_text(strip=True)
                else:
                    product['titulo'] = link.get('title', '')

                # Imagem
                img_tag = link.find('img')
                if img_tag:
                    product['imagem'] = img_tag.get('data-src') or img_tag.get('src', '')

                # Desconto
                if product_card:
                    badge = product_card.find('span', class_='badge')
                    if badge:
                        product['desconto'] = badge.get_text(strip=True)

                products.append(product)
                
                # Delay para não sobrecarregar o servidor
                time.sleep(0.5)

        print(f"✓ {len(products)} produtos encontrados")
        return products

    def scrape_all(self, max_products_per_category: int = 10) -> Dict:
        """Realiza scraping completo do site"""
        print("=== Iniciando Scraping Silver Crown ===\n")
        
        data = {
            'site': 'Silver Crown',
            'url': self.base_url,
            'data_coleta': time.strftime('%Y-%m-%d %H:%M:%S'),
            'categorias': [],
            'total_produtos': 0
        }

        # Extrai categorias
        categories = self.extract_categories()
        
        # Limita a 5 categorias para exemplo
        for category in categories[:5]:
            print(f"\n--- Categoria: {category['nome']} ---")
            
            # Extrai produtos da categoria
            products = self.extract_products_from_category(
                category['url'], 
                max_products=max_products_per_category
            )
            
            category['produtos'] = products
            data['categorias'].append(category)
            data['total_produtos'] += len(products)
            
            # Delay entre categorias
            time.sleep(1)

        print(f"\n=== Scraping Concluído ===")
        print(f"Total de produtos coletados: {data['total_produtos']}")
        
        return data

    def save_to_json(self, data: Dict, filename: str = 'silvercrown_produtos.json'):
        """Salva os dados em formato JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✓ Dados salvos em: {filename}")

    def save_to_csv(self, data: Dict, filename: str = 'silvercrown_produtos.csv'):
        """Salva os dados em formato CSV"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['categoria', 'titulo', 'preco', 'desconto', 'url', 'imagem']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for category in data['categorias']:
                for product in category['produtos']:
                    writer.writerow({
                        'categoria': category['nome'],
                        'titulo': product['titulo'],
                        'preco': product.get('preco', ''),
                        'desconto': product.get('desconto', ''),
                        'url': product['url'],
                        'imagem': product.get('imagem', '')
                    })
        
        print(f"✓ Dados salvos em: {filename}")


def main():
    """Função principal"""
    scraper = SilverCrownScraper()
    
    # Realiza scraping
    data = scraper.scrape_all(max_products_per_category=10)
    
    # Salva resultados
    scraper.save_to_json(data)
    scraper.save_to_csv(data)
    
    # Exibe resumo
    print("\n=== RESUMO ===")
    print(f"Categorias: {len(data['categorias'])}")
    print(f"Total de produtos: {data['total_produtos']}")
    
    print("\nCategorias coletadas:")
    for cat in data['categorias']:
        print(f"  - {cat['nome']}: {len(cat['produtos'])} produtos")


if __name__ == "__main__":
    main()
