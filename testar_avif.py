"""
Teste de conversão de imagens para AVIF
"""
from PIL import Image
import pillow_avif  # Plugin AVIF
import io
import base64
import re

def converter_para_avif(imagem_base64):
    """Converte qualquer imagem para formato AVIF"""
    try:
        if not imagem_base64:
            return None
        
        # Extrair o tipo de imagem e os dados base64
        match = re.match(r'data:image/(\w+);base64,(.+)', imagem_base64)
        if not match:
            img_data = imagem_base64
            formato_original = "unknown"
        else:
            formato_original = match.group(1)
            img_data = match.group(2)
            
            if formato_original.lower() == 'avif':
                print("✅ Imagem já está em formato AVIF")
                return imagem_base64
        
        print(f"🔄 Convertendo de {formato_original.upper()} para AVIF...")
        
        # Decodificar base64
        img_bytes = base64.b64decode(img_data)
        tamanho_original = len(img_bytes)
        
        # Abrir imagem
        img = Image.open(io.BytesIO(img_bytes))
        print(f"📐 Dimensões: {img.size[0]}x{img.size[1]} pixels")
        print(f"🎨 Modo de cor: {img.mode}")
        
        # Converter para RGB se necessário
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1])
            else:
                background.paste(img)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Redimensionar se muito grande
        max_size = 1920
        if max(img.size) > max_size:
            print(f"📉 Redimensionando para máximo de {max_size}px...")
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Salvar como AVIF
        output = io.BytesIO()
        img.save(output, format='AVIF', quality=85, speed=6)
        output.seek(0)
        
        # Converter para base64
        avif_base64 = base64.b64encode(output.read()).decode('utf-8')
        tamanho_final = len(base64.b64decode(avif_base64))
        
        reducao = ((tamanho_original - tamanho_final) / tamanho_original) * 100
        
        print(f"📦 Tamanho original: {tamanho_original:,} bytes ({tamanho_original/1024:.1f} KB)")
        print(f"📦 Tamanho AVIF: {tamanho_final:,} bytes ({tamanho_final/1024:.1f} KB)")
        print(f"💚 Redução: {reducao:.1f}%")
        print("✅ Conversão concluída!")
        
        return f"data:image/avif;base64,{avif_base64}"
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return imagem_base64

# Teste básico
print("=" * 60)
print("🧪 TESTE DE CONVERSÃO PARA AVIF")
print("=" * 60)

# Criar uma imagem de teste
print("\n1️⃣ Criando imagem de teste PNG...")
img_test = Image.new('RGB', (800, 600), color='blue')
buffer = io.BytesIO()
img_test.save(buffer, format='PNG')
buffer.seek(0)
png_base64 = f"data:image/png;base64,{base64.b64encode(buffer.read()).decode('utf-8')}"

print("\n2️⃣ Testando conversão...")
avif_result = converter_para_avif(png_base64)

if avif_result and avif_result.startswith('data:image/avif'):
    print("\n✅ SUCESSO! Sistema de conversão AVIF está funcionando!")
else:
    print("\n❌ FALHA na conversão")

print("\n" + "=" * 60)
