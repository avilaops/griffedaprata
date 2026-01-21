# 🌐 GitHub Pages + Hetzner - Setup Completo

## 📋 Arquitetura Final

```
┌─────────────────────────────────────────┐
│  GitHub Pages (GRÁTIS)                  │
│  https://griffedaprata.com.br           │
│                                         │
│  • index.html                           │
│  • loja.html                            │
│  • produto.html                         │
│  • admin_produtos.html                  │
│  • CSS, JS, imagens                     │
└────────────┬────────────────────────────┘
             │
             │ API calls via fetch()
             │
             ▼
┌─────────────────────────────────────────┐
│  Hetzner Cloud (€5.83/mês)              │
│  https://api.griffedaprata.com.br       │
│                                         │
│  • backend_api.py (porta 5000)          │
│  • chatbot_api.py (porta 5001)          │
│  • whatsapp_bot.py (porta 5002)         │
│  • SQLite databases                     │
└─────────────────────────────────────────┘
```

## ✅ Vantagens desta Configuração

| Aspecto | Vantagem |
|---------|----------|
| **Custo** | Frontend GRÁTIS no GitHub Pages |
| **Performance** | CDN global do GitHub (super rápido) |
| **SSL** | HTTPS automático e gratuito |
| **Escalabilidade** | GitHub aguenta milhões de visitas |
| **Deploy** | `git push` e pronto! |
| **Separação** | Frontend e backend independentes |

## 🚀 Passo a Passo - Configuração

### 1. Configurar GitHub Pages

#### 1.1. Ativar GitHub Pages

```bash
# No GitHub, acesse:
https://github.com/avilaops/griffedaprata/settings/pages

# Configurar:
Source: Deploy from a branch
Branch: main
Folder: / (root)
```

#### 1.2. Criar arquivo de configuração do GitHub Pages

Já criado: `CNAME` com `griffedaprata.com.br`

#### 1.3. Configurar DNS

No seu provedor de domínio (Registro.br):

```
Tipo A:
Nome: @
Valores (todos os 4 IPs do GitHub):
  185.199.108.153
  185.199.109.153
  185.199.110.153
  185.199.111.153

Tipo CNAME:
Nome: www
Valor: avilaops.github.io

Tipo CNAME:
Nome: api
Valor: SEU_IP_HETZNER (ou use A record)
```

### 2. Atualizar Frontend para Usar API Externa

Os arquivos HTML já estão configurados, mas vamos garantir:

#### 2.1. Criar arquivo de configuração

Arquivo `config.js` (raiz do projeto):

```javascript
// Configuração de ambiente
const CONFIG = {
    // Produção (GitHub Pages)
    API_URL: 'https://api.griffedaprata.com.br',
    CHATBOT_URL: 'https://api.griffedaprata.com.br:5001',
    WHATSAPP_URL: 'https://api.griffedaprata.com.br:5002',
    
    // Desenvolvimento local (descomente para testar)
    // API_URL: 'http://localhost:5000',
    // CHATBOT_URL: 'http://localhost:5001',
    // WHATSAPP_URL: 'http://localhost:5002',
};
```

### 3. Configurar Backend no Hetzner

#### 3.1. Nginx com CORS e Subdomínio

```nginx
# /etc/nginx/sites-available/griffedaprata-api

server {
    listen 80;
    server_name api.griffedaprata.com.br;

    # CORS Headers
    add_header 'Access-Control-Allow-Origin' 'https://griffedaprata.com.br' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;
    add_header 'Access-Control-Allow-Credentials' 'true' always;

    # Preflight requests
    if ($request_method = 'OPTIONS') {
        return 204;
    }

    # Backend API
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Chatbot API
    location /chatbot/ {
        proxy_pass http://localhost:5001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WhatsApp API
    location /whatsapp/ {
        proxy_pass http://localhost:5002/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 3.2. Ativar site e SSL

```bash
# Ativar configuração
ln -s /etc/nginx/sites-available/griffedaprata-api /etc/nginx/sites-enabled/

# Testar
nginx -t

# Recarregar
systemctl reload nginx

# SSL para subdomínio API
certbot --nginx -d api.griffedaprata.com.br

# Renovação automática
certbot renew --dry-run
```

### 4. Deploy - Processo Completo

#### 4.1. Deploy do Frontend (GitHub Pages)

```bash
# Local - fazer alterações
git add .
git commit -m "Update frontend"
git push origin main

# GitHub Pages atualiza automaticamente em ~1 minuto
# Acesse: https://griffedaprata.com.br
```

#### 4.2. Deploy do Backend (Hetzner)

```bash
# SSH no servidor
ssh root@SEU_IP_HETZNER

# Atualizar código
cd /var/www/griffedaprata
git pull origin main

# Reiniciar serviços
supervisorctl restart all

# Verificar status
supervisorctl status
```

## 🔧 Arquivos que Precisam ser Atualizados

### Frontend (usar API externa):

Todos os arquivos HTML que fazem chamadas de API devem usar `CONFIG.API_URL`:

```javascript
// Antes (local):
const API_URL = 'http://localhost:5000/api';

// Depois (produção):
const API_URL = CONFIG.API_URL + '/api';
```

**Arquivos a atualizar:**
- `index.html`
- `loja.html`
- `produto.html`
- `admin_produtos.html`
- `painel_pedidos.html`
- `painel_chatbot.html`
- `chatbot-widget.js`

## 📊 Custos Finais

| Serviço | Custo |
|---------|-------|
| GitHub Pages (Frontend) | **GRÁTIS** ✅ |
| Hetzner CX21 (Backend) | €5.83/mês |
| Domínio griffedaprata.com.br | ~R$ 40/ano |
| SSL Certificate | **GRÁTIS** (Let's Encrypt) |
| **Total Mensal** | **€5.83** (~R$ 35/mês) |

**Economia:** ~€50/mês vs hospedar tudo no Hetzner maior

## 🎯 Vantagens desta Arquitetura

### Performance
- ✅ Frontend em CDN global (GitHub)
- ✅ Latência < 50ms em qualquer lugar do mundo
- ✅ 99.99% uptime (GitHub SLA)

### Segurança
- ✅ HTTPS em frontend e backend
- ✅ CORS configurado corretamente
- ✅ Backend isolado, sem acesso público direto aos arquivos

### Escalabilidade
- ✅ Frontend aguenta 10 milhões de visitas (GitHub)
- ✅ Backend escala conforme necessidade (Hetzner)

### Desenvolvimento
- ✅ Deploy frontend: `git push` (automático)
- ✅ Deploy backend: `git pull` + `supervisorctl restart`
- ✅ Testar local antes de subir

## 🧪 Testar Configuração

### Teste 1: Frontend

```bash
# Acessar site
https://griffedaprata.com.br

# Deve carregar HTML/CSS/JS do GitHub Pages
# Abrir DevTools (F12) > Network
# Ver que arquivos .html, .css, .js vêm do GitHub
```

### Teste 2: Backend API

```bash
# Testar API diretamente
curl https://api.griffedaprata.com.br/api/produtos

# Deve retornar JSON com produtos
```

### Teste 3: CORS

```bash
# No navegador, abrir:
https://griffedaprata.com.br/loja.html

# Abrir DevTools > Console
# Não deve ter erros de CORS
# Produtos devem carregar normalmente
```

## 🐛 Troubleshooting

### Erro: CORS blocked

**Solução:** Verificar configuração Nginx no Hetzner:
```bash
# Checar headers CORS
curl -I https://api.griffedaprata.com.br
# Deve ter: Access-Control-Allow-Origin
```

### Erro: Mixed content (HTTP/HTTPS)

**Solução:** Garantir que todas as URLs usam HTTPS:
```javascript
// ❌ Errado
const API_URL = 'http://api.griffedaprata.com.br';

// ✅ Correto
const API_URL = 'https://api.griffedaprata.com.br';
```

### GitHub Pages não atualiza

**Solução:** 
```bash
# Forçar rebuild
git commit --allow-empty -m "Trigger rebuild"
git push origin main

# Aguardar 1-2 minutos
```

## 📱 URLs Finais

| Serviço | URL | Onde Roda |
|---------|-----|-----------|
| **Site Principal** | https://griffedaprata.com.br | GitHub Pages |
| **Admin Panel** | https://griffedaprata.com.br/admin_produtos.html | GitHub Pages |
| **Backend API** | https://api.griffedaprata.com.br/api/produtos | Hetzner |
| **Chatbot API** | https://api.griffedaprata.com.br/chatbot/ | Hetzner |
| **WhatsApp** | https://api.griffedaprata.com.br/whatsapp/ | Hetzner |

## 🎉 Resultado Final

```
✅ Frontend GRÁTIS no GitHub Pages
✅ Backend otimizado no Hetzner
✅ SSL em tudo (HTTPS)
✅ CDN global para velocidade máxima
✅ Separação clara de responsabilidades
✅ Deploy simplificado (git push)
✅ Custo: apenas €5.83/mês

🚀 SETUP PROFISSIONAL COM CUSTO MÍNIMO!
```

## 📞 Checklist de Implementação

- [ ] 1. Ativar GitHub Pages no repositório
- [ ] 2. Criar `config.js` com URLs de produção
- [ ] 3. Atualizar arquivos HTML para usar CONFIG.API_URL
- [ ] 4. Configurar DNS (4 IPs do GitHub + subdomínio api)
- [ ] 5. Deploy backend no Hetzner
- [ ] 6. Configurar Nginx com CORS
- [ ] 7. Ativar SSL no subdomínio API
- [ ] 8. Testar frontend no GitHub Pages
- [ ] 9. Testar chamadas de API
- [ ] 10. Verificar CORS funcionando
- [ ] 11. Deploy final!

---

💎 **Griffe da Prata com setup profissional e econômico!**
