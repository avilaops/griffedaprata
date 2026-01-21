"""
Conversor de Logos para AVIF - Alta Qualidade
Converte todas as imagens PNG da pasta Logo para AVIF
"""

import os
from PIL import Image
import pillow_avif

# Diretórios
LOGO_DIR = "Logo"
OUTPUT_DIR = "Logo"

def converter_logo_para_avif(caminho_origem, caminho_destino):
    """Converte uma imagem para AVIF com máxima qualidade"""
    try:
        # Abrir imagem original
        with Image.open(caminho_origem) as img:
            # Manter modo original (RGBA para transparência)
            if img.mode not in ('RGB', 'RGBA'):
                if img.mode == 'P' and 'transparency' in img.info:
                    img = img.convert('RGBA')
                else:
                    img = img.convert('RGB')
            
            # Salvar como AVIF com qualidade máxima
            img.save(
                caminho_destino,
                format='AVIF',
                quality=95,  # Qualidade máxima
                speed=0      # Compressão mais lenta mas melhor qualidade
            )
            
            # Calcular redução
            tamanho_original = os.path.getsize(caminho_origem)
            tamanho_avif = os.path.getsize(caminho_destino)
            reducao = ((tamanho_original - tamanho_avif) / tamanho_original) * 100
            
            print(f"✅ {os.path.basename(caminho_origem)}")
            print(f"   Original: {tamanho_original/1024:.1f}KB → AVIF: {tamanho_avif/1024:.1f}KB")
            print(f"   Redução: {reducao:.1f}%")
            print()
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao converter {caminho_origem}: {e}")
        return False

def converter_todas_logos():
    """Converte todas as logos PNG para AVIF"""
    if not os.path.exists(LOGO_DIR):
        print(f"❌ Pasta {LOGO_DIR} não encontrada!")
        return
    
    # Listar arquivos PNG
    arquivos = [f for f in os.listdir(LOGO_DIR) if f.lower().endswith('.png')]
    
    if not arquivos:
        print("❌ Nenhum arquivo PNG encontrado na pasta Logo!")
        return
    
    print(f"🎨 Convertendo {len(arquivos)} logos para AVIF com qualidade máxima...\n")
    
    sucesso = 0
    falha = 0
    
    for arquivo in sorted(arquivos):
        caminho_origem = os.path.join(LOGO_DIR, arquivo)
        nome_sem_ext = os.path.splitext(arquivo)[0]
        caminho_destino = os.path.join(OUTPUT_DIR, f"{nome_sem_ext}.avif")
        
        if converter_logo_para_avif(caminho_origem, caminho_destino):
            sucesso += 1
        else:
            falha += 1
    
    print("\n" + "="*50)
    print(f"✨ Conversão concluída!")
    print(f"✅ Sucesso: {sucesso}")
    if falha > 0:
        print(f"❌ Falhas: {falha}")
    print("="*50)

if __name__ == "__main__":
    converter_todas_logos()
