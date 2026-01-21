# 🚀 Scraper Completo Silver Crown

Scraper profissional que extrai **TODOS os dados e imagens** do site Silver Crown.

## ✨ Características

✅ **Extração completa de produtos**
✅ **Download automático de TODAS as imagens**
✅ **Organização por categorias**
✅ **Múltiplos formatos de exportação** (JSON, CSV, HTML)
✅ **Catálogo HTML navegável**
✅ **Sistema de backup automático**
✅ **Estatísticas detalhadas**

## 📁 Estrutura de Arquivos Criada

```
silvercrown_scraper/
├── scraper_completo.py          # Script principal
├── requirements.txt             # Dependências
├── README.md                    # Esta documentação
├── imagens/                     # Pasta com todas as imagens
│   ├── Aneis/                   # Imagens da categoria Anéis
│   ├── Brincos/                 # Imagens da categoria Brincos
│   ├── Colares/                 # E assim por diante...
│   └── ...
└── dados/                       # Dados extraídos
    ├── silvercrown_completo.json       # JSON completo
    ├── silvercrown_completo.csv        # CSV para Excel
    ├── catalogo.html                   # Catálogo visual
    └── backup_categoria_*.json         # Backups de progresso
```

## 🚀 Como Usar

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Executar o Scraper

```bash
python scraper_completo.py
```

### 3. Aguardar a Coleta

O scraper irá:
- ✅ Extrair todas as categorias
- ✅ Coletar produtos de cada categoria
- ✅ Baixar TODAS as imagens dos produtos
- ✅ Salvar tudo localmente
- ✅ Criar um catálogo HTML

## ⚙️ Configurações

Edite no arquivo `scraper_completo.py`:

```python
# Linha ~480
MAX_PRODUTOS_POR_CATEGORIA = 15  # Produtos por categoria
MAX_CATEGORIAS = 10              # Limite de categorias (None = todas)
```

## 📊 Formatos de Saída

### 1. JSON Completo (`silvercrown_completo.json`)
Dados estruturados com TODAS as informações:
```json
{
  "site": "Silver Crown",
  "categorias": [
    {
      "nome": "Anéis",
      "produtos": [
        {
          "titulo": "Anel...",
          "preco": "R$ 50,00",
          "imagens": [
            {
              "url_original": "https://...",
              "caminho_local": "imagens/Aneis/anel_abc123.jpg"
            }
          ]
        }
      ]
    }
  ],
  "estatisticas": {
    "produtos": 150,
    "imagens": 450
  }
}
```

### 2. CSV (`silvercrown_completo.csv`)
Planilha para Excel/Google Sheets com:
- Categoria
- Título
- Preço
- Desconto
- URL
- Caminho das imagens locais

### 3. Catálogo HTML (`catalogo.html`)
Página web navegável com:
- 🖼️ Todas as imagens
- 💰 Preços e descontos
- 📦 Produtos organizados por categoria
- 🔗 Links para produtos originais

**Para visualizar**: Abra o arquivo `dados/catalogo.html` no navegador!

## 📈 Estatísticas em Tempo Real

Durante a execução, você verá:

```
🔍 Extraindo categorias...
✅ 25 categorias encontradas

📂 Categoria: Anéis
   📦 Processando: https://...
      🖼️  5 imagens baixadas
   ✅ 15 produtos coletados

📊 Progresso: 3/25 categorias
```

## 🎯 Dados Coletados por Produto

- ✅ Título completo
- ✅ Preço atual
- ✅ Preço original (se houver desconto)
- ✅ Percentual de desconto
- ✅ Descrição curta
- ✅ Descrição completa
- ✅ SKU / Código
- ✅ URL do produto
- ✅ **TODAS as imagens (baixadas localmente)**
- ✅ Especificações técnicas
- ✅ Categoria

## 🛡️ Recursos de Segurança

✅ **Sistema de backup**: Salva progresso a cada categoria processada
✅ **Controle de duplicatas**: Não baixa imagens repetidas
✅ **Tratamento de erros**: Continua mesmo se algum produto falhar
✅ **Delays automáticos**: Respeita o servidor (1-2s entre requisições)
✅ **Timeout configurável**: Evita travamentos

## 💡 Dicas de Uso

### Para coletar TUDO (pode demorar horas):
```python
MAX_PRODUTOS_POR_CATEGORIA = None  # Todos os produtos
MAX_CATEGORIAS = None              # Todas as categorias
```

### Para teste rápido:
```python
MAX_PRODUTOS_POR_CATEGORIA = 5     # Apenas 5 produtos
MAX_CATEGORIAS = 2                 # Apenas 2 categorias
```

### Para categorias específicas:
Modifique a linha ~465:
```python
# Filtrar categorias específicas
categories = [c for c in categories if 'Anéis' in c['nome'] or 'Brincos' in c['nome']]
```

## 🔍 Encontrando Suas Imagens

As imagens são organizadas por categoria:

```
imagens/
├── Aneis/
│   ├── Anel_Solitario_Zirconia_abc123.jpg
│   ├── Anel_Solitario_Zirconia_def456.jpg
│   └── ...
├── Brincos/
│   ├── Brinco_Argola_xyz789.jpg
│   └── ...
```

## ⚠️ Avisos Importantes

1. **Espaço em disco**: Muitas imagens ocupam espaço (pode chegar a GBs)
2. **Tempo de execução**: Scraping completo pode levar horas
3. **Conexão estável**: Mantenha internet estável durante todo o processo
4. **Respeite o site**: Use delays adequados entre requisições

## 🐛 Solução de Problemas

### Erro: "Connection timeout"
- Aumente o timeout na linha 47: `timeout=30`
- Verifique sua conexão com a internet

### Erro: "Permission denied" ao salvar
- Execute como administrador
- Verifique permissões da pasta

### Muitos erros de download
- Aumente os delays (linhas 366, 478)
- Verifique firewall/antivírus

## 📞 Recursos Úteis

- **JSON Viewer**: Para visualizar o JSON completo
- **Excel**: Para abrir o arquivo CSV
- **Navegador Web**: Para ver o catálogo HTML

## 🎉 Resultado Final

Ao final, você terá:
- ✅ Todas as imagens salvas localmente
- ✅ Dados completos em JSON
- ✅ Planilha CSV para análise
- ✅ Catálogo HTML navegável
- ✅ Backup de progresso

## 📝 Licença

Uso educacional e pessoal. Respeite os termos de uso do site.

---

**Desenvolvido para scraping ético e responsável** 🤝
