# 💎 Griffe da Prata - E-commerce de Joias em Prata

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.1.2-green.svg)

Plataforma completa de e-commerce para joias em prata com sistema de chatbot inteligente, integração WhatsApp e painel administrativo.

🌐 **Site:** [griffedaprata.com.br](https://griffedaprata.com.br)

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Tecnologias](#-tecnologias)
- [Arquitetura](#-arquitetura)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Uso](#-uso)
- [APIs e Endpoints](#-apis-e-endpoints)
- [Chatbot Inteligente](#-chatbot-inteligente)
- [Painel Administrativo](#-painel-administrativo)
- [Integração WhatsApp](#-integração-whatsapp)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

## ✨ Funcionalidades

### E-commerce
- 🛍️ Catálogo completo de produtos com 211+ itens
- 🔍 Sistema de busca e filtros avançados
- 🛒 Carrinho de compras integrado
- 💳 Checkout simplificado
- 📱 Design responsivo e mobile-first
- 👤 Área de conta do cliente
- 📦 Acompanhamento de pedidos

### Chatbot Inteligente
- 🤖 Sistema híbrido de IA com reconhecimento de intenções
- 💬 Respostas contextualizadas sobre produtos
- 🎯 Detecção inteligente de categorias (anéis, brincos, colares, pulseiras)
- 📊 Histórico de conversas
- 🔄 Integração com WhatsApp
- 🎨 Widget customizável para site

### Painel Administrativo
- 📸 Upload de fotos por drag-and-drop
- 🔄 **Conversão automática para AVIF (85% menor)**
- ✏️ CRUD completo de produtos
- 📊 Dashboard com estatísticas em tempo real
- 🔍 Busca e filtros avançados
- 💾 Armazenamento otimizado de imagens
- 📱 Interface responsiva com Bootstrap 5

### Integrações
- 🔄 Scraper automatizado de marketplaces
- 🤝 Sincronização com fornecedores (Silver Crown)
- 📲 Webhook WhatsApp (Twilio)
- 🗄️ Banco de dados SQLite

## 🛠️ Tecnologias

### Backend
- **Python 3.10+**
- **Flask 3.1.2** - Framework web
- **SQLite3** - Banco de dados
- **Pillow 10.2.0** - Processamento de imagens
- **pillow-avif-plugin** - Conversão AVIF
- **BeautifulSoup4** - Web scraping
- **Flask-CORS** - Cross-Origin Resource Sharing

### Frontend
- **HTML5 / CSS3**
- **JavaScript (ES6+)**
- **Bootstrap 5.3.0** - Framework CSS
- **Font Awesome 6.0** - Ícones
- **jQuery 3.6** - Manipulação DOM

### IA e NLP
- **Sistema Híbrido Proprietário** - Chatbot baseado em regras
- **Regex** - Detecção de padrões e intenções
- **Context-Aware Responses** - Respostas contextualizadas

## 🏗️ Arquitetura

```
┌─────────────────┐
│   Frontend      │
│  (HTML/CSS/JS)  │
└────────┬────────┘
         │
         ├──────────────────────────────────┐
         │                                  │
┌────────▼────────┐              ┌─────────▼─────────┐
│  Backend API    │              │   Chatbot API     │
│  (Port 5000)    │              │   (Port 5001)     │
│                 │              │                   │
│ • Produtos      │              │ • IA Híbrida      │
│ • Pedidos       │              │ • Conversas       │
│ • CRUD Admin    │              │ • Histórico       │
└────────┬────────┘              └─────────┬─────────┘
         │                                  │
         │                       ┌──────────▼──────────┐
         │                       │  WhatsApp Bot       │
         │                       │  (Port 5002)        │
         │                       │                     │
         │                       │ • Webhook Twilio    │
         │                       │ • Integração IA     │
         │                       └─────────────────────┘
         │
┌────────▼────────┐
│  SQLite DBs     │
│                 │
│ • pedidos.db    │
│ • conversas.db  │
└─────────────────┘
```

## 📥 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/avilaops/griffedaprata.git
cd griffedaprata
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
```

### 3. Ative o ambiente virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

## ⚙️ Configuração

### 1. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# APIs (Opcional - Sistema funciona sem)
OPENAI_API_KEY=sua_chave_aqui
GROK_API_KEY=sua_chave_aqui
HF_TOKEN=seu_token_aqui

# WhatsApp/Twilio
TWILIO_ACCOUNT_SID=seu_sid_aqui
TWILIO_AUTH_TOKEN=seu_token_aqui
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
NGROK_AUTH_TOKEN=seu_token_aqui

# Marketplace
MERCADOLIVRE_CLIENT_ID=seu_client_id
MERCADOLIVRE_CLIENT_SECRET=seu_secret
```

### 2. Inicialize o banco de dados

```bash
python setup_completo.py
```

### 3. (Opcional) Execute o scraper para importar produtos

```bash
python scraper_silvercrown.py
```

## 🚀 Uso

### Método 1: Script de inicialização (Recomendado)

**Windows:**
```bash
iniciar_sistema.bat
```

**Linux/Mac:**
```bash
chmod +x iniciar_sistema.sh
./iniciar_sistema.sh
```

### Método 2: Manual

Abra **3 terminais diferentes** e execute:

**Terminal 1 - Backend API:**
```bash
python backend_api.py
```

**Terminal 2 - Chatbot API:**
```bash
python chatbot_api.py
```

**Terminal 3 - WhatsApp Bot:**
```bash
python whatsapp_bot.py
```

### Acessar o sistema

- **Site principal:** `http://localhost:5000` ou abra `index.html`
- **Painel Admin:** `http://localhost:5000/admin_produtos.html`
- **Painel Pedidos:** `http://localhost:5000/painel_pedidos.html`
- **Painel Chatbot:** `http://localhost:5000/painel_chatbot.html`

## 🔌 APIs e Endpoints

### Backend API (Port 5000)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/produtos` | Lista todos os produtos |
| POST | `/api/produtos` | Adiciona/atualiza produto |
| DELETE | `/api/produtos/<codigo>` | Remove produto |
| POST | `/api/pedidos` | Cria novo pedido |
| GET | `/api/pedidos` | Lista pedidos |
| GET | `/api/pedidos/<id>` | Busca pedido específico |

### Chatbot API (Port 5001)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/chatbot/mensagem` | Envia mensagem ao chatbot |
| GET | `/api/chatbot/historico/<sessao>` | Busca histórico de conversa |
| GET | `/api/chatbot/estatisticas` | Estatísticas de uso |

### WhatsApp Bot (Port 5002)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/whatsapp/webhook` | Webhook Twilio |
| GET | `/whatsapp/webhook` | Verificação webhook |

## 🤖 Chatbot Inteligente

O sistema utiliza um chatbot híbrido proprietário baseado em regras e reconhecimento de padrões, **sem necessidade de APIs pagas**.

### Intenções Suportadas

- **Saudação** - Boas-vindas e apresentação
- **Produto** - Informações sobre itens específicos
- **Preço** - Consulta de valores e descontos
- **Compra** - Processo de aquisição
- **Entrega** - Prazos e frete
- **Pagamento** - Formas de pagamento
- **Qualidade** - Material e garantia
- **Troca** - Política de devolução
- **Dúvida** - Questões gerais

### Exemplo de Uso

```python
from chatbot_hibrido import gerar_resposta

# Enviar mensagem
resposta = gerar_resposta("Quero ver anéis de prata", sessao_id="user123")
print(resposta)
# "Temos lindos anéis de prata! Nossos anéis são confeccionados..."
```

## 🎨 Painel Administrativo

Acesse o painel em `admin_produtos.html` para gerenciar produtos.

### Funcionalidades

- ✅ **Adicionar produto** - Formulário completo com upload de imagem
- ✅ **Editar produto** - Atualização inline de informações
- ✅ **Excluir produto** - Remoção com confirmação
- ✅ **Upload de fotos** - Drag-and-drop ou seleção de arquivo
- ✅ **Busca** - Filtro por nome, código ou descrição
- ✅ **Estatísticas** - Total, em estoque, sem foto
- ✅ **Preview** - Visualização de imagens antes de salvar

### Como usar

1. Abra `admin_produtos.html` no navegador
2. Clique em **"Novo Produto"**
3. Preencha os dados obrigatórios
4. Arraste uma foto ou clique para selecionar (**qualquer formato: JPG, PNG, WEBP, GIF**)
5. O sistema converte automaticamente para **AVIF (85% menor)** 🚀
6. Clique em **"Salvar"**

💡 **A conversão é silenciosa e transparente - você não precisa fazer nada!**

## 📲 Integração WhatsApp

### Configuração Twilio

1. Crie uma conta em [Twilio](https://www.twilio.com)
2. Ative o WhatsApp Sandbox
3. Configure o webhook: `https://seu-dominio.com/whatsapp/webhook`
4. Adicione credenciais no `.env`

### Teste local com ngrok

```bash
ngrok http 5002
```

Configure a URL do ngrok no Twilio Console.

## 📁 Estrutura do Projeto

```
griffedaprata/
├── backend_api.py              # API principal
├── chatbot_api.py              # API do chatbot
├── whatsapp_bot.py             # Bot WhatsApp
├── chatbot_hibrido.py          # IA híbrida
├── index.html                  # Página inicial
├── admin_produtos.html         # Painel admin
├── painel_pedidos.html         # Gestão de pedidos
├── painel_chatbot.html         # Analytics chatbot
├── loja.html                   # Catálogo de produtos
├── produto.html                # Página de produto
├── checkout.html               # Finalização de compra
├── chatbot-widget.js           # Widget do chatbot
├── scraper_silvercrown.py      # Scraper marketplace
├── requirements.txt            # Dependências
├── .env                        # Configurações
├── pedidos.db                  # Banco de pedidos
├── chatbot_conversas.db        # Banco de conversas
├── whatsapp_conversas.db       # Banco WhatsApp
├── README.md                   # Este arquivo
└── CNAME                       # Domínio personalizado
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Siga os passos:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👤 Autor

**Griffe da Prata Team**

- Website: [griffedaprata.com.br](https://griffedaprata.com.br)
- GitHub: [@avilaops](https://github.com/avilaops)

## 🙏 Agradecimentos

- Silver Crown - Fornecedor de produtos
- Twilio - Integração WhatsApp
- Bootstrap Team - Framework CSS
- Comunidade Open Source

---

⭐ **Se este projeto foi útil, deixe uma estrela!**

📧 **Contato:** contato@griffedaprata.com.br
    'https://silvercrown.com.br/categoria-aneis/',
    max_products=20
)

# Realizar scraping completo
data = scraper.scrape_all(max_products_per_category=15)

# Salvar em diferentes formatos
scraper.save_to_json(data, 'produtos.json')
scraper.save_to_csv(data, 'produtos.csv')
```

## 📊 Dados Coletados

O scraper coleta as seguintes informações:

### Por Produto:
- Título/Nome do produto
- Preço atual
- Preço original (se houver desconto)
- Percentual de desconto
- URL do produto
- URL da imagem principal
- Descrição
- Especificações técnicas

### Por Categoria:
- Nome da categoria
- URL da categoria
- Lista de produtos

## 📁 Arquivos de Saída

### JSON (`silvercrown_produtos.json`)
Estrutura hierárquica completa com todas as informações.

```json
{
  "site": "Silver Crown",
  "url": "https://silvercrown.com.br",
  "data_coleta": "2026-01-20 10:30:00",
  "categorias": [
    {
      "nome": "Anéis",
      "url": "...",
      "produtos": [...]
    }
  ]
}
```

### CSV (`silvercrown_produtos.csv`)
Formato tabular simples para análise em Excel/Google Sheets.

| categoria | titulo | preco | desconto | url | imagem |
|-----------|--------|-------|----------|-----|--------|
| Anéis | Anel... | R$ 50,00 | 50% OFF | ... | ... |

## ⚙️ Configurações

Você pode ajustar os seguintes parâmetros:

```python
# Número máximo de produtos por categoria
max_products_per_category = 10

# Delay entre requisições (segundos)
time.sleep(0.5)  # Entre produtos
time.sleep(1)    # Entre categorias
```

## ⚠️ Avisos Importantes

1. **Respeite os Termos de Uso**: Verifique os termos de serviço do site antes de usar
2. **Use com moderação**: Não faça muitas requisições em pouco tempo
3. **Dados Públicos**: Este scraper coleta apenas dados públicos disponíveis no site
4. **Uso Educacional**: Este projeto é para fins educacionais

## 🛠️ Solução de Problemas

### Erro de timeout
```python
# Aumentar o timeout na função get_page_content
response = self.session.get(url, timeout=30)
```

### Site bloqueando requisições
- Adicione delays maiores entre requisições
- Varie o User-Agent
- Use proxies se necessário

## 📝 Licença

Este projeto é livre para uso educacional e pessoal.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir novas funcionalidades
- Melhorar a documentação

## 📧 Contato

Para dúvidas ou sugestões sobre este scraper, abra uma issue no repositório.

---

**Nota**: Este scraper foi desenvolvido para fins educacionais. Use responsavelmente e respeite as políticas do site.
#   g r i f f e d a p r a t a 
 
 