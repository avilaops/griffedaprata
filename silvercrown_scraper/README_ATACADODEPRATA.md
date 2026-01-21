# 🚀 Scraper Atacado de Prata

Scraper completo para extrair produtos, códigos, preços e imagens do **Atacado de Prata**.

## 🎯 Site Alvo

https://atacadodeprata.rdi.store/s/jessica

## ✨ Características

✅ **Extração de produtos** com códigos, preços, peso e lote
✅ **Download automático de imagens**
✅ **Organização por categorias**
✅ **Exportação em JSON, CSV e HTML**
✅ **Catálogo visual navegável**

## 📁 Estrutura Criada

```
atacadodeprata_data/
├── imagens/                    # Todas as fotos baixadas
│   ├── ANEIS/
│   ├── BRINCOS/
│   ├── PULSEIRA/
│   └── ...
└── dados/                      # Dados extraídos
    ├── atacadodeprata_completo.json
    ├── atacadodeprata_completo.csv
    └── catalogo_atacadodeprata.html
```

## 🚀 Como Usar

### 1. Executar o scraper

```bash
python scraper_atacadodeprata.py
```

### 2. Aguardar a coleta

O scraper irá:
- ✅ Coletar produtos da página principal
- ✅ Extrair produtos por categoria
- ✅ Baixar todas as imagens
- ✅ Salvar em múltiplos formatos

### 3. Visualizar resultados

Abra o catálogo HTML no navegador:
```bash
start atacadodeprata_data\dados\catalogo_atacadodeprata.html
```

## 📊 Dados Coletados

Por produto:
- ✅ Código (ex: K2-80, P3-10)
- ✅ Título/Nome
- ✅ Preço
- ✅ Peso aproximado
- ✅ Número do lote
- ✅ Categoria
- ✅ Imagens (todas disponíveis)

## ⚙️ Configurações

Edite no arquivo `scraper_atacadodeprata.py`:

```python
# Linha ~280
max_products_per_category = 30   # Produtos por categoria
max_categories = 10              # Limite de categorias
```

## 📋 Categorias Disponíveis

- ALIANÇA
- ANEIS / ANEIS MASCULINO
- ARGOLAS
- BERLOQUES
- BRINCO BABY / BRINCOS
- CHOCKER
- COLAR + GARGANTILHAS
- CONJUNTO
- CORRENTE MASCULINA / FEMININA
- GARGANTILHA LETRA
- PANDORAS
- PIERCING
- PINGENTES (Masculino/Feminino)
- PONTO DE LUZ
- PULSEIRAS (várias categorias)
- RIVIERAS
- TERÇO
- TORNOZELEIRA

## 🔍 Estrutura dos Dados

### JSON
```json
{
  "site": "Atacado de Prata",
  "categorias": [
    {
      "nome": "ANEIS",
      "produtos": [
        {
          "codigo": "K2-80",
          "titulo": "Brinco Cravejado Importado",
          "preco": "R$1,70",
          "peso": "1,7g",
          "lote": "18",
          "imagens": [...]
        }
      ]
    }
  ]
}
```

### CSV
Colunas: categoria, codigo, titulo, preco, peso, lote, url, total_imagens, primeira_imagem_local

## 💡 Dicas

### Coletar tudo
```python
scraper.scrape_all(
    max_products_per_category=None,  # Sem limite
    max_categories=None              # Todas as categorias
)
```

### Categorias específicas
Edite a lista `known_categories` no código (linha ~120)

## ⚠️ Observações

- O site tem estrutura dinâmica, pode precisar ajustes
- Respeite os limites do servidor (delays incluídos)
- Imagens são salvas organizadas por categoria
- Backups automáticos a cada categoria processada

## 📧 Contato do Site

- Email: bsladora78@gmail.com
- WhatsApp: +55 82 98160-2651

---

**Desenvolvido para scraping ético e responsável** 🤝
