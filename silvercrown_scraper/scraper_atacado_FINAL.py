"""
Scraper FINAL para Atacado de Prata - COM IMAGENS
Baseado na estrutura real do site
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import csv
import requests
import hashlib
from pathlib import Path
import re


class AtacadoDePrataFinal:
    def __init__(self):
        self.url = "https://atacadodeprata.rdi.store/products"
        self.base_dir = Path("atacadodeprata_completo")
        self.images_dir = self.base_dir / "imagens"
        self.data_dir = self.base_dir / "dados"
        
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.produtos = []
        self.stats = {'produtos': 0, 'imagens': 0, 'erros': 0}
        
        # Configurar Selenium
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        print("🚀 Inicializando navegador...")
        self.driver = webdriver.Chrome(options=chrome_options)
        print("✅ Navegador iniciado!\n")

    def scroll_completo(self):
        """Scroll até carregar TODOS os produtos"""
        print("📜 Fazendo scroll para carregar TODOS os produtos...")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scrolls = 30
        
        while scroll_attempts < max_scrolls:
            # Scroll até o fim
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Aguardar imagens carregarem
            
            # Verificar nova altura
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
            
            last_height = new_height
            scroll_attempts += 1
            print(f"   Scroll {scroll_attempts}/{max_scrolls}...")
        
        # Voltar ao topo
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        print("✅ Scroll completo!\n")

    def baixar_imagem(self, img_url, codigo):
        """Baixa imagem do produto"""
        try:
            if not img_url or 'placeholder' in img_url.lower() or 'data:image' in img_url:
                return None
            
            # Garantir URL completa
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                img_url = 'https://atacadodeprata.rdi.store' + img_url
            
            # Criar nome de arquivo único
            img_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
            filename = f"{codigo}_{img_hash}.jpg"
            filepath = self.images_dir / filename
            
            if not filepath.exists():
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(img_url, timeout=15, headers=headers)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                self.stats['imagens'] += 1
                
            return str(filepath.relative_to(self.base_dir))
            
        except Exception as e:
            self.stats['erros'] += 1
            return None

    def extrair_produtos(self):
        """Extrai todos os produtos da página"""
        print("📦 Acessando página de produtos...\n")
        
        self.driver.get(self.url)
        time.sleep(5)  # Aguardar carregamento inicial
        
        self.scroll_completo()
        
        # Buscar TODAS as imagens de produtos
        print("🔍 Buscando produtos...\n")
        
        try:
            # Esperar imagens carregarem
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "img"))
            )
            
            # Buscar todas as imagens
            imgs = self.driver.find_elements(By.TAG_NAME, 'img')
            
            print(f"📸 Encontradas {len(imgs)} imagens\n")
            
            codigos_vistos = set()  # Evitar duplicatas
            
            for idx, img in enumerate(imgs, 1):
                try:
                    # Pegar atributos da imagem
                    img_url = img.get_attribute('src')
                    img_alt = img.get_attribute('alt') or ''
                    
                    # Filtrar apenas imagens de produtos (mais flexível)
                    if not img_url or 'assets.rediredi.com' not in img_url:
                        continue
                    
                    # Pular imagens de logo/banner
                    if '/stores/' in img_url or '/banners/' in img_url:
                        continue
                    
                    # Buscar container do produto (elemento pai)
                    try:
                        # O produto está em um div que contém a imagem, código e preço
                        produto_div = img.find_element(By.XPATH, './ancestor::div[contains(@class, "flex-col")]')
                        texto_completo = produto_div.text
                        
                        # Extrair código (formato: X#-## ou XX-##)
                        codigo_match = re.search(r'([A-Z][0-9A-Z]?-\d+)', texto_completo)
                        if not codigo_match:
                            continue
                        
                        codigo = codigo_match.group(1)
                        
                        # Evitar duplicatas
                        if codigo in codigos_vistos:
                            continue
                        codigos_vistos.add(codigo)
                        
                        # Extrair preço
                        preco_match = re.search(r'R\$[\d,\.]+', texto_completo)
                        preco_atacado = preco_match.group(0) if preco_match else ''
                        
                        # Calcular preço varejo (250% = x3.5)
                        preco_varejo = ''
                        if preco_atacado:
                            try:
                                valor = float(re.sub(r'[^\d,]', '', preco_atacado).replace(',', '.'))
                                preco_varejo = f"R$ {(valor * 3.5):.2f}".replace('.', ',')
                            except:
                                pass
                        
                        # Extrair título/descrição
                        linhas = texto_completo.split('\n')
                        titulo = ''
                        for linha in linhas:
                            if codigo in linha:
                                titulo = linha.strip()
                                break
                        
                        # Baixar imagem
                        print(f"   📥 {idx}/{len(imgs)} - {codigo} - {preco_atacado}...")
                        imagem_local = self.baixar_imagem(img_url, codigo)
                        
                        if imagem_local:
                            print(f"      ✅ Imagem baixada!")
                        
                        # Criar registro do produto
                        produto = {
                            'codigo': codigo,
                            'titulo': titulo,
                            'preco_atacado': preco_atacado,
                            'preco_varejo': preco_varejo,
                            'descricao': texto_completo[:200],
                            'imagem_url': img_url,
                            'imagem_local': imagem_local
                        }
                        
                        self.produtos.append(produto)
                        self.stats['produtos'] += 1
                        
                    except Exception as e:
                        continue
                        
                except Exception as e:
                    continue
            
            print(f"\n✅ Total de produtos extraídos: {len(self.produtos)}")
            
        except Exception as e:
            print(f"❌ Erro ao buscar produtos: {e}")

    def salvar_json(self):
        """Salva em JSON"""
        filepath = self.data_dir / 'produtos_atacado_FINAL.json'
        data = {
            'fornecedor': 'Atacado de Prata',
            'url': self.url,
            'total_produtos': len(self.produtos),
            'margem_aplicada': '250%',
            'produtos': self.produtos,
            'estatisticas': self.stats
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 JSON salvo: {filepath}")

    def salvar_csv(self):
        """Salva em CSV"""
        filepath = self.data_dir / 'produtos_atacado_FINAL.csv'
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['codigo', 'titulo', 'preco_atacado', 'preco_varejo', 'margem', 'imagem_local']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for p in self.produtos:
                writer.writerow({
                    'codigo': p['codigo'],
                    'titulo': p['titulo'],
                    'preco_atacado': p['preco_atacado'],
                    'preco_varejo': p['preco_varejo'],
                    'margem': '250%',
                    'imagem_local': p['imagem_local'] or ''
                })
        
        print(f"💾 CSV salvo: {filepath}")

    def criar_catalogo(self):
        """Cria catálogo HTML"""
        filepath = self.data_dir / 'catalogo_FINAL.html'
        
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Catálogo Atacado de Prata - Margem 250%</title>
    <style>
        body {{ font-family: Arial; padding: 20px; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; margin-bottom: 20px; }}
        .stats {{ background: white; padding: 15px; margin-bottom: 20px; border-radius: 8px; }}
        .produtos {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
        .produto {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .produto img {{ width: 100%; height: 200px; object-fit: contain; border-radius: 4px; background: #f9f9f9; }}
        .codigo {{ font-weight: bold; color: #2c3e50; margin: 10px 0; font-size: 16px; }}
        .preco-atacado {{ color: #e74c3c; font-size: 14px; text-decoration: line-through; }}
        .preco-varejo {{ color: #27ae60; font-size: 22px; font-weight: bold; margin: 5px 0; }}
        .margem {{ background: #3498db; color: white; padding: 5px 10px; border-radius: 4px; font-size: 12px; display: inline-block; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>💰 Catálogo Atacado de Prata</h1>
        <p>Preços com Margem de 250%</p>
    </div>
    
    <div class="stats">
        <h2>📊 Estatísticas</h2>
        <p><strong>Total de produtos:</strong> {len(self.produtos)}</p>
        <p><strong>Imagens baixadas:</strong> {self.stats['imagens']}</p>
        <p><strong>Margem aplicada:</strong> 250% (Preço Varejo = Atacado × 3.5)</p>
    </div>
    
    <div class="produtos">
"""
        
        for p in self.produtos:
            img_path = '../' + p['imagem_local'].replace('\\', '/') if p['imagem_local'] else ''
            
            html += f"""
        <div class="produto">
            <img src="{img_path}" alt="{p['codigo']}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22%3E%3Crect fill=%22%23ddd%22 width=%22200%22 height=%22200%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22%3ESem imagem%3C/text%3E%3C/svg%3E'">
            <div class="codigo">{p['codigo']}</div>
            <div class="preco-atacado">Atacado: {p['preco_atacado']}</div>
            <div class="preco-varejo">Varejo: {p['preco_varejo']}</div>
            <span class="margem">MARGEM 250%</span>
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"🌐 Catálogo HTML: {filepath}")

    def executar(self):
        """Executa scraping completo"""
        print("="*60)
        print("🚀 SCRAPER ATACADO DE PRATA - VERSÃO FINAL")
        print("="*60)
        
        try:
            self.extrair_produtos()
            
            if self.produtos:
                self.salvar_json()
                self.salvar_csv()
                self.criar_catalogo()
                
                print("\n" + "="*60)
                print("✅ SCRAPING CONCLUÍDO COM SUCESSO!")
                print("="*60)
                print(f"\n📊 Resultados:")
                print(f"   ✅ Produtos: {self.stats['produtos']}")
                print(f"   ✅ Imagens: {self.stats['imagens']}")
                print(f"   ❌ Erros: {self.stats['erros']}")
                print(f"\n📁 Pasta: {self.base_dir.absolute()}")
            else:
                print("\n❌ Nenhum produto extraído!")
                
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.driver.quit()
            print("\n✅ Navegador fechado")


if __name__ == "__main__":
    scraper = AtacadoDePrataFinal()
    scraper.executar()
