"""
Scraper FUNCIONAL para Atacado de Prata usando Selenium
Extrai TODOS os produtos do fornecedor com preços para aplicar margem
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import csv
from pathlib import Path
import re
import requests
from urllib.parse import urljoin
import hashlib


class AtacadoDePrataSelenium:
    def __init__(self, base_dir="atacadodeprata_completo"):
        self.url = "https://atacadodeprata.rdi.store/s/jessica"
        self.base_dir = Path(base_dir)
        self.images_dir = self.base_dir / "imagens"
        self.data_dir = self.base_dir / "dados"
        
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.produtos = []
        self.stats = {'produtos': 0, 'imagens': 0, 'erros': 0}
        
        # Configurar Selenium
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Rodar sem abrir janela
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        print("🚀 Inicializando navegador Chrome...")
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✅ Navegador iniciado com sucesso!\n")
        except Exception as e:
            print(f"❌ Erro ao iniciar Chrome: {e}")
            print("\n💡 Você precisa instalar:")
            print("1. pip install selenium")
            print("2. Baixar ChromeDriver: https://chromedriver.chromium.org/")
            raise

    def aguardar_carregamento(self, timeout=10):
        """Aguarda a página carregar completamente"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            time.sleep(2)  # Aguardar JavaScript executar
        except TimeoutException:
            print("⚠️  Timeout ao aguardar carregamento")

    def scroll_para_carregar_tudo(self):
        """Faz scroll para carregar todos os produtos (lazy loading)"""
        print("📜 Fazendo scroll para carregar todos os produtos...")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_count = 0
        
        while scroll_count < 20:  # Máximo 20 scrolls
            # Scroll até o fim
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2.5)  # Aumentado para 2.5s para imagens carregarem
            
            # Calcular nova altura
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
                
            last_height = new_height
            scroll_count += 1
            print(f"   Scroll {scroll_count}...")
        
        # Scroll de volta ao topo
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)  # Aguardar imagens do topo carregarem
        print("✅ Scroll completo!\n")

    def extrair_preco(self, texto):
        """Extrai preço do texto"""
        if not texto:
            return None
        match = re.search(r'R\$\s*([\d,\.]+)', texto)
        if match:
            return match.group(0)
        return None

    def extrair_peso(self, texto):
        """Extrai peso do texto"""
        if not texto:
            return None
        match = re.search(r'([\d,\.]+)\s*g', texto, re.I)
        if match:
            return match.group(0)
        return None

    def baixar_imagem(self, img_url, codigo):
        """Baixa imagem do produto"""
        try:
            if not img_url or 'placeholder' in img_url.lower():
                return None
            
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            
            img_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
            filename = f"{codigo}_{img_hash}.jpg"
            filepath = self.images_dir / filename
            
            if not filepath.exists():
                response = requests.get(img_url, timeout=10)
                response.raise_for_status()
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                self.stats['imagens'] += 1
                
            return str(filepath.relative_to(self.base_dir))
        except Exception as e:
            print(f"   ⚠️  Erro ao baixar imagem: {e}")
            self.stats['erros'] += 1
            return None

    def extrair_produtos(self):
        """Extrai todos os produtos da página"""
        print("📦 Acessando site e extraindo produtos...\n")
        
        self.driver.get(self.url)
        self.aguardar_carregamento()
        self.scroll_para_carregar_tudo()
        
        # Tentar vários seletores possíveis
        seletores = [
            "//div[contains(@class, 'product')]",
            "//article[contains(@class, 'product')]",
            "//div[contains(@class, 'item')]",
            "//*[contains(text(), 'R$')]/..",
            "//*[contains(text(), 'Peso')]/..",
        ]
        
        elementos_produtos = []
        for seletor in seletores:
            try:
                elementos = self.driver.find_elements(By.XPATH, seletor)
                if elementos:
                    print(f"✅ Encontrados {len(elementos)} elementos com: {seletor}")
                    elementos_produtos.extend(elementos)
            except:
                continue
        
        # Remover duplicatas
        elementos_produtos = list(set(elementos_produtos))
        print(f"\n📊 Total de elementos únicos: {len(elementos_produtos)}\n")
        
        for idx, elemento in enumerate(elementos_produtos, 1):
            try:
                texto_completo = elemento.text
                
                # Extrair código do produto
                codigo_match = re.search(r'([A-Z][0-9]+-[0-9]+)', texto_completo)
                if not codigo_match:
                    continue
                
                codigo = codigo_match.group(1)
                
                # Extrair informações
                produto = {
                    'codigo': codigo,
                    'titulo': '',
                    'preco_atacado': '',
                    'preco_varejo': '',  # Será calculado com margem 250%
                    'peso': '',
                    'lote': '',
                    'descricao': texto_completo[:200],
                    'imagem_local': None,
                    'imagem_url': None
                }
                
                # Extrair título (linha com código)
                linhas = texto_completo.split('\n')
                for linha in linhas:
                    if codigo in linha:
                        produto['titulo'] = linha.strip()
                        break
                
                # Extrair preço
                produto['preco_atacado'] = self.extrair_preco(texto_completo)
                
                # Extrair peso
                produto['peso'] = self.extrair_peso(texto_completo)
                
                # Extrair lote
                lote_match = re.search(r'Lote.*?([0-9]+)', texto_completo, re.I)
                if lote_match:
                    produto['lote'] = lote_match.group(1)
                
                # Calcular preço de varejo (250% de margem)
                if produto['preco_atacado']:
                    try:
                        preco_num = float(re.sub(r'[^\d,]', '', produto['preco_atacado']).replace(',', '.'))
                        preco_varejo = preco_num * 3.5  # 250% = 3.5x
                        produto['preco_varejo'] = f"R$ {preco_varejo:.2f}".replace('.', ',')
                    except:
                        pass
                
                # Extrair imagem (tentar múltiplas formas)
                try:
                    img_elem = elemento.find_element(By.TAG_NAME, 'img')
                    # Tentar src, data-src, data-lazy-src
                    img_url = (img_elem.get_attribute('src') or 
                              img_elem.get_attribute('data-src') or 
                              img_elem.get_attribute('data-lazy-src') or
                              img_elem.get_attribute('data-original'))
                    
                    if img_url and 'data:image' not in img_url:
                        produto['imagem_url'] = img_url
                        produto['imagem_local'] = self.baixar_imagem(img_url, codigo)
                except Exception as e:
                    try:
                        # Tentar encontrar background-image no CSS
                        style = elemento.get_attribute('style')
                        if style and 'background-image' in style:
                            match = re.search(r'url\([\'"]?(.*?)[\'"]?\)', style)
                            if match:
                                img_url = match.group(1)
                                produto['imagem_url'] = img_url
                                produto['imagem_local'] = self.baixar_imagem(img_url, codigo)
                    except:
                        pass
                
                self.produtos.append(produto)
                self.stats['produtos'] += 1
                
                print(f"   ✅ {idx}/{len(elementos_produtos)} - {codigo} - {produto['preco_atacado']} → {produto['preco_varejo']}")
                
            except Exception as e:
                print(f"   ⚠️  Erro ao processar elemento {idx}: {e}")
                self.stats['erros'] += 1
                continue

    def salvar_json(self):
        """Salva dados em JSON"""
        filepath = self.data_dir / 'produtos_atacado_completo.json'
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
        """Salva dados em CSV"""
        filepath = self.data_dir / 'produtos_atacado_completo.csv'
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'codigo', 'titulo', 'preco_atacado', 'preco_varejo', 
                'margem', 'peso', 'lote', 'imagem_local'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for p in self.produtos:
                writer.writerow({
                    'codigo': p['codigo'],
                    'titulo': p['titulo'],
                    'preco_atacado': p['preco_atacado'],
                    'preco_varejo': p['preco_varejo'],
                    'margem': '250%',
                    'peso': p['peso'],
                    'lote': p['lote'],
                    'imagem_local': p['imagem_local'] or ''
                })
        
        print(f"💾 CSV salvo: {filepath}")

    def criar_catalogo_html(self):
        """Cria catálogo HTML com preços comparados"""
        filepath = self.data_dir / 'catalogo_precos.html'
        
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Catálogo com Margem 250%</title>
    <style>
        body {{ font-family: Arial; padding: 20px; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; margin-bottom: 20px; }}
        .stats {{ background: white; padding: 15px; margin-bottom: 20px; border-radius: 8px; }}
        .produtos {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
        .produto {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .produto img {{ width: 100%; height: 200px; object-fit: cover; border-radius: 4px; }}
        .codigo {{ font-weight: bold; color: #2c3e50; margin: 10px 0; }}
        .preco-atacado {{ color: #e74c3c; font-size: 14px; text-decoration: line-through; }}
        .preco-varejo {{ color: #27ae60; font-size: 22px; font-weight: bold; margin: 5px 0; }}
        .margem {{ background: #3498db; color: white; padding: 5px 10px; border-radius: 4px; font-size: 12px; }}
        .info {{ font-size: 13px; color: #7f8c8d; margin: 3px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>💰 Catálogo com Margem 250%</h1>
        <p>Atacado de Prata → Varejo</p>
    </div>
    
    <div class="stats">
        <h2>📊 Estatísticas</h2>
        <p><strong>Total de produtos:</strong> {len(self.produtos)}</p>
        <p><strong>Imagens baixadas:</strong> {self.stats['imagens']}</p>
        <p><strong>Margem aplicada:</strong> 250% (Preço final = Atacado × 3.5)</p>
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
            <div class="info">Peso: {p['peso']}</div>
            <div class="info">Lote: {p['lote']}</div>
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

    def fechar(self):
        """Fecha o navegador"""
        self.driver.quit()
        print("\n✅ Navegador fechado")

    def executar(self):
        """Executa o scraping completo"""
        print("="*60)
        print("🚀 SCRAPER ATACADO DE PRATA - COM MARGEM 250%")
        print("="*60)
        
        try:
            self.extrair_produtos()
            
            if self.produtos:
                self.salvar_json()
                self.salvar_csv()
                self.criar_catalogo_html()
                
                print("\n" + "="*60)
                print("✅ SCRAPING CONCLUÍDO!")
                print("="*60)
                print(f"\n📊 Resultados:")
                print(f"   ✅ Produtos extraídos: {self.stats['produtos']}")
                print(f"   ✅ Imagens baixadas: {self.stats['imagens']}")
                print(f"   ❌ Erros: {self.stats['erros']}")
                print(f"   💰 Margem aplicada: 250%")
                print(f"\n📁 Pasta: {self.base_dir.absolute()}")
            else:
                print("\n❌ Nenhum produto foi extraído!")
                print("💡 Verifique se o site está acessível")
                
        except Exception as e:
            print(f"\n❌ Erro durante execução: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.fechar()


if __name__ == "__main__":
    scraper = AtacadoDePrataSelenium()
    scraper.executar()
