"""
Script para baixar imagens do Atacado de Prata
Usa os dados já coletados e busca as imagens no site
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json
import requests
import hashlib
from pathlib import Path


def baixar_imagens():
    # Carregar dados
    json_path = Path("atacadodeprata_completo/dados/produtos_atacado_completo.json")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    produtos = data['produtos']
    images_dir = Path("atacadodeprata_completo/imagens")
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # Configurar Selenium
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    print("🚀 Inicializando navegador...")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://atacadodeprata.rdi.store/s/jessica")
    
    print("⏳ Aguardando página carregar...")
    time.sleep(5)
    
    print("📜 Fazendo scroll para carregar imagens...\n")
    for i in range(15):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        print(f"   Scroll {i+1}/15...")
    
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)
    
    print(f"\n🖼️  Buscando imagens para {len(produtos)} produtos...\n")
    
    imagens_baixadas = 0
    
    for idx, produto in enumerate(produtos, 1):
        codigo = produto['codigo']
        
        try:
            # Buscar elemento que contém o código
            elementos = driver.find_elements(By.XPATH, f"//*[contains(text(), '{codigo}')]")
            
            for elem in elementos:
                # Buscar imagem no elemento pai ou próximo
                try:
                    # Tentar encontrar img no mesmo container
                    container = elem.find_element(By.XPATH, "./ancestor::*[contains(@class, 'item') or contains(@class, 'product') or contains(@class, 'card')]")
                    imgs = container.find_elements(By.TAG_NAME, 'img')
                    
                    for img in imgs:
                        img_url = (img.get_attribute('src') or 
                                  img.get_attribute('data-src') or
                                  img.get_attribute('data-lazy-src'))
                        
                        if img_url and 'data:image' not in img_url and 'placeholder' not in img_url.lower():
                            # Baixar imagem
                            if img_url.startswith('//'):
                                img_url = 'https:' + img_url
                            
                            try:
                                img_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
                                filename = f"{codigo}_{img_hash}.jpg"
                                filepath = images_dir / filename
                                
                                if not filepath.exists():
                                    response = requests.get(img_url, timeout=10)
                                    response.raise_for_status()
                                    with open(filepath, 'wb') as f:
                                        f.write(response.content)
                                    
                                    imagens_baixadas += 1
                                    print(f"   ✅ {idx}/{len(produtos)} - {codigo} - Imagem baixada!")
                                    
                                    # Atualizar JSON
                                    produto['imagem_url'] = img_url
                                    produto['imagem_local'] = str(filepath.relative_to("atacadodeprata_completo"))
                                    break
                            except Exception as e:
                                continue
                    
                    if produto.get('imagem_local'):
                        break
                        
                except Exception as e:
                    continue
            
            if not produto.get('imagem_local'):
                print(f"   ⚠️  {idx}/{len(produtos)} - {codigo} - Sem imagem")
                
        except Exception as e:
            print(f"   ❌ {idx}/{len(produtos)} - {codigo} - Erro: {e}")
    
    driver.quit()
    
    # Salvar JSON atualizado
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ CONCLUÍDO!")
    print(f"{'='*60}")
    print(f"🖼️  Imagens baixadas: {imagens_baixadas}/{len(produtos)}")
    print(f"📁 Pasta: {images_dir.absolute()}")


if __name__ == "__main__":
    baixar_imagens()
