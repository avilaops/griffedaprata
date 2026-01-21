# 🚀 Scraper Selenium - Atacado de Prata (Fornecedor)

## 💰 Objetivo

Extrair **TODOS** os produtos do seu fornecedor (Atacado de Prata) e aplicar margem de **250%** automaticamente.

## 📦 Instalação

```bash
# 1. Instalar Selenium
pip install selenium

# 2. Baixar ChromeDriver
# Acesse: https://chromedriver.chromium.org/
# Baixe a versão compatível com seu Chrome
# Extraia e coloque no PATH do sistema
```

### Como verificar a versão do Chrome:
1. Abra o Chrome
2. Digite: `chrome://settings/help`
3. Veja a versão (ex: 120.0.6099.109)
4. Baixe o ChromeDriver correspondente

### Colocar no PATH:
- **Windows**: Coloque `chromedriver.exe` em `C:\Windows\System32\`
- Ou coloque na mesma pasta do script

## 🚀 Execução

```bash
python scraper_selenium_atacado.py
```

O scraper irá:
1. ✅ Abrir o Chrome (modo headless)
2. ✅ Acessar o site do Atacado de Prata
3. ✅ Fazer scroll para carregar TODOS os produtos
4. ✅ Extrair códigos, preços, peso, lote
5. ✅ Baixar todas as imagens
6. ✅ **Calcular preço de varejo (margem 250%)**
7. ✅ Salvar em JSON, CSV e HTML

## 📊 Margem de 250%

### Fórmula aplicada:
```
Preço Varejo = Preço Atacado × 3.5
```

### Exemplo:
- **Atacado**: R$ 10,00
- **Varejo**: R$ 35,00 (250% de margem)

### Como funciona:
- 100% = 2x (dobro)
- 150% = 2.5x
- 200% = 3x (triplo)
- **250% = 3.5x** ✅

## 📁 Arquivos Gerados

```
atacadodeprata_completo/
├── imagens/                        # Todas as fotos
│   ├── K2-80_abc123.jpg
│   ├── P3-10_def456.jpg
│   └── ...
└── dados/
    ├── produtos_atacado_completo.json    # Dados completos
    ├── produtos_atacado_completo.csv     # Para Excel
    └── catalogo_precos.html              # Visualização
```

## 🌐 Catálogo HTML

O arquivo `catalogo_precos.html` mostra:
- ✅ Preço do atacado (riscado)
- ✅ Preço de varejo (destaque)
- ✅ Badge "MARGEM 250%"
- ✅ Comparação lado a lado
- ✅ Todas as imagens

**Abra no navegador para ver os preços calculados!**

## 📊 Estrutura do JSON

```json
{
  "fornecedor": "Atacado de Prata",
  "total_produtos": 150,
  "margem_aplicada": "250%",
  "produtos": [
    {
      "codigo": "K2-80",
      "titulo": "Brinco Cravejado Importado",
      "preco_atacado": "R$ 10,00",
      "preco_varejo": "R$ 35,00",
      "peso": "1,7g",
      "lote": "18",
      "imagem_local": "imagens/K2-80_abc123.jpg"
    }
  ]
}
```

## 📈 Estrutura do CSV

| codigo | titulo | preco_atacado | preco_varejo | margem | peso | lote |
|--------|--------|---------------|--------------|--------|------|------|
| K2-80  | Brinco...| R$ 10,00   | R$ 35,00     | 250%   | 1,7g | 18   |

## ⚙️ Configurações

### Alterar margem:
No arquivo `scraper_selenium_atacado.py`, linha ~176:
```python
preco_varejo = preco_num * 3.5  # 250% = 3.5x

# Para 200%: preco_varejo = preco_num * 3
# Para 300%: preco_varejo = preco_num * 4
# Para 150%: preco_varejo = preco_num * 2.5
```

### Modo visual (ver o Chrome funcionando):
Linha ~28, comente:
```python
# chrome_options.add_argument('--headless')  # Comentar esta linha
```

## 🔧 Solução de Problemas

### Erro: "chromedriver not found"
```bash
# Baixe em: https://chromedriver.chromium.org/
# Coloque na pasta do projeto ou no PATH
```

### Erro: "session not created"
- Versão do ChromeDriver incompatível com o Chrome
- Baixe a versão correta

### Poucos produtos extraídos
- Aumente o tempo de scroll (linha ~66)
- Aumente o sleep após scroll (linha ~72)

### Imagens não baixam
- Verifique conexão com internet
- O site pode ter proteção anti-bot

## 💡 Dicas

1. **Execute em horários de baixo tráfego** do site
2. **Não execute muito frequentemente** (1-2x por dia no máximo)
3. **Verifique os preços** no HTML gerado antes de usar
4. **Backup**: Os dados ficam salvos localmente

## 🎯 Próximos Passos

Depois de ter os dados:
1. ✅ Revisar preços no catálogo HTML
2. ✅ Ajustar margem se necessário
3. ✅ Importar CSV para seu sistema
4. ✅ Usar imagens baixadas no seu site

## 📞 Suporte

Se o scraper não funcionar:
1. Verifique se o Chrome e ChromeDriver estão instalados
2. Teste sem headless mode
3. Veja os logs de erro
4. O site pode ter mudado estrutura

---

**Tempo de execução estimado**: 5-15 minutos (depende do número de produtos)

**Margem aplicada**: 250% (configurável)
