# 🚀 Guia de Deploy - Hetzner Cloud

## 📋 Visão Geral

Este guia mostra como hospedar a plataforma Griffe da Prata no **Hetzner Cloud**, mantendo todos os serviços online 24/7.

## 🎯 Por que Hetzner?

- ✅ **Mais barato** que AWS/Azure
- ✅ **Servidores na Europa** (baixa latência)
- ✅ **IPv4 gratuito**
- ✅ **Fácil configuração**
- ✅ **99.9% uptime**

## 💰 Planos Recomendados

### Opção 1: Pequeno Negócio (Recomendado)
- **CX21**: €5.83/mês
- 2 vCPU, 4 GB RAM, 40 GB SSD
- ✅ Ideal para 211 produtos + chatbot

### Opção 2: Crescimento
- **CX31**: €11.66/mês
- 2 vCPU, 8 GB RAM, 80 GB SSD
- ✅ Suporta mais tráfego e produtos

### Opção 3: Profissional
- **CX41**: €23.33/mês
- 4 vCPU, 16 GB RAM, 160 GB SSD
- ✅ Alta performance, muitos acessos

## 🔧 Passo a Passo - Deploy Completo

### 1. Criar Servidor no Hetzner

```bash
# 1. Acesse: https://console.hetzner.cloud/
# 2. Crie um novo projeto: "Griffe da Prata"
# 3. Adicione um servidor:
#    - Localização: Nuremberg (Alemanha) ou Ashburn (EUA)
#    - Imagem: Ubuntu 22.04
#    - Tipo: CX21 (ou superior)
#    - SSH Key: Adicione sua chave pública
#    - Nome: griffe-producao
```

### 2. Conectar ao Servidor

```bash
# Pegar IP do servidor (ex: 65.108.123.45)
ssh root@SEU_IP_AQUI

# Primeira vez: aceitar fingerprint (yes)
```

### 3. Configurar Servidor

```bash
# Atualizar sistema
apt update && apt upgrade -y

# Instalar Python 3.10
apt install -y python3.10 python3-pip python3-venv

# Instalar Nginx (servidor web)
apt install -y nginx

# Instalar Supervisor (manter processos rodando)
apt install -y supervisor

# Instalar Git
apt install -y git

# Instalar certbot (SSL grátis)
apt install -y certbot python3-certbot-nginx
```

### 4. Clonar Projeto

```bash
# Criar diretório
mkdir -p /var/www
cd /var/www

# Clonar repositório
git clone https://github.com/avilaops/griffedaprata.git
cd griffedaprata

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 5. Configurar Variáveis de Ambiente

```bash
# Criar arquivo .env
nano .env
```

Cole este conteúdo:

```env
# APIs (Opcional - Sistema funciona sem)
OPENAI_API_KEY=sua_chave_aqui
GROK_API_KEY=sua_chave_aqui
HF_TOKEN=seu_token_aqui

# WhatsApp/Twilio
TWILIO_ACCOUNT_SID=seu_sid_aqui
TWILIO_AUTH_TOKEN=seu_token_aqui
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Domínio
DOMAIN=griffedaprata.com.br
```

Salvar: `Ctrl+X`, `Y`, `Enter`

### 6. Configurar Supervisor (Manter Serviços Online)

```bash
# Criar arquivo de configuração
nano /etc/supervisor/conf.d/griffedaprata.conf
```

Cole este conteúdo:

```ini
[program:griffe_backend]
directory=/var/www/griffedaprata
command=/var/www/griffedaprata/venv/bin/python backend_api.py
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/griffe_backend.err.log
stdout_logfile=/var/log/griffe_backend.out.log

[program:griffe_chatbot]
directory=/var/www/griffedaprata
command=/var/www/griffedaprata/venv/bin/python chatbot_api.py
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/griffe_chatbot.err.log
stdout_logfile=/var/log/griffe_chatbot.out.log

[program:griffe_whatsapp]
directory=/var/www/griffedaprata
command=/var/www/griffedaprata/venv/bin/python whatsapp_bot.py
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/griffe_whatsapp.err.log
stdout_logfile=/var/log/griffe_whatsapp.out.log
```

### 7. Configurar Nginx (Servidor Web)

```bash
# Criar arquivo de configuração
nano /etc/nginx/sites-available/griffedaprata
```

Cole este conteúdo:

```nginx
server {
    listen 80;
    server_name griffedaprata.com.br www.griffedaprata.com.br;

    # Frontend
    root /var/www/griffedaprata;
    index index.html;

    # Arquivos estáticos
    location / {
        try_files $uri $uri/ =404;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Chatbot API
    location /chatbot/ {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WhatsApp Webhook
    location /whatsapp/ {
        proxy_pass http://localhost:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 8. Ativar Site e Iniciar Serviços

```bash
# Criar link simbólico
ln -s /etc/nginx/sites-available/griffedaprata /etc/nginx/sites-enabled/

# Remover site padrão
rm /etc/nginx/sites-enabled/default

# Testar configuração
nginx -t

# Recarregar Nginx
systemctl reload nginx

# Atualizar Supervisor
supervisorctl reread
supervisorctl update

# Iniciar serviços
supervisorctl start griffe_backend
supervisorctl start griffe_chatbot
supervisorctl start griffe_whatsapp

# Verificar status
supervisorctl status
```

### 9. Configurar DNS (Domínio)

No seu provedor de domínio (Registro.br, etc):

```
Tipo A:
Nome: @
Valor: SEU_IP_HETZNER
TTL: 3600

Tipo A:
Nome: www
Valor: SEU_IP_HETZNER
TTL: 3600
```

### 10. Configurar SSL (HTTPS Grátis)

```bash
# Aguardar DNS propagar (5-30 minutos)

# Obter certificado SSL
certbot --nginx -d griffedaprata.com.br -d www.griffedaprata.com.br

# Email: seu@email.com
# Aceitar termos: Y
# Compartilhar email: N
# Redirect HTTP -> HTTPS: 2 (Yes)

# Renovação automática já está configurada!
```

## 🎯 Comandos Úteis

### Ver Logs

```bash
# Backend
tail -f /var/log/griffe_backend.out.log

# Chatbot
tail -f /var/log/griffe_chatbot.out.log

# WhatsApp
tail -f /var/log/griffe_whatsapp.out.log

# Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Gerenciar Serviços

```bash
# Status de todos
supervisorctl status

# Reiniciar um serviço
supervisorctl restart griffe_backend

# Parar um serviço
supervisorctl stop griffe_backend

# Iniciar um serviço
supervisorctl start griffe_backend

# Reiniciar todos
supervisorctl restart all
```

### Atualizar Código

```bash
cd /var/www/griffedaprata

# Baixar atualizações
git pull origin main

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar dependências (se necessário)
pip install -r requirements.txt

# Reiniciar serviços
supervisorctl restart all
```

## 🔒 Segurança

### Configurar Firewall

```bash
# Instalar UFW
apt install -y ufw

# Permitir SSH
ufw allow 22/tcp

# Permitir HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Ativar firewall
ufw enable

# Verificar status
ufw status
```

### Criar Usuário não-root

```bash
# Criar usuário
adduser griffe

# Adicionar ao grupo sudo
usermod -aG sudo griffe

# Copiar chave SSH
rsync --archive --chown=griffe:griffe ~/.ssh /home/griffe

# Testar login (nova janela)
ssh griffe@SEU_IP

# Desabilitar login root (após testar)
nano /etc/ssh/sshd_config
# Mudar: PermitRootLogin no
systemctl restart sshd
```

## 💾 Backup Automático

```bash
# Criar script de backup
nano /usr/local/bin/backup-griffe.sh
```

Cole:

```bash
#!/bin/bash
DATA=$(date +%Y%m%d_%H%M%S)
mkdir -p /backups
cd /var/www/griffedaprata
tar -czf /backups/griffe_$DATA.tar.gz .
find /backups -mtime +7 -delete  # Remove backups > 7 dias
```

```bash
# Dar permissão
chmod +x /usr/local/bin/backup-griffe.sh

# Agendar (diariamente às 3AM)
crontab -e
# Adicionar: 0 3 * * * /usr/local/bin/backup-griffe.sh
```

## 📊 Monitoramento

### Instalar Netdata (Dashboard de Monitoramento)

```bash
bash <(curl -Ss https://get.netdata.cloud/kickstart.sh)

# Acessar: http://SEU_IP:19999
```

## 🚀 Otimizações de Performance

### Habilitar Gzip no Nginx

```bash
nano /etc/nginx/nginx.conf
```

Adicionar dentro de `http {}`:

```nginx
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml text/javascript 
           application/json application/javascript application/xml+rss;
```

### Aumentar Limites do Sistema

```bash
nano /etc/security/limits.conf
```

Adicionar:

```
* soft nofile 65535
* hard nofile 65535
```

## 🎉 Pronto!

Seu site está online em:
- 🌐 **https://griffedaprata.com.br**
- 🔒 **SSL ativo** (cadeado verde)
- 🤖 **Chatbot funcionando**
- 📱 **WhatsApp integrado**
- ⚡ **Performance otimizada**

## 📞 Suporte Hetzner

- 📧 Email: support@hetzner.com
- 💬 Chat: https://console.hetzner.cloud/
- 📚 Docs: https://docs.hetzner.com/

## 💡 Dicas Importantes

1. **NÃO use Postman para produção** - é apenas para testes
2. **Supervisor mantém tudo rodando** - se cair, reinicia automaticamente
3. **SSL renova automaticamente** - certbot faz sozinho
4. **Backups diários** - em /backups/
5. **Logs em tempo real** - use `tail -f`

---

💎 **Griffe da Prata agora está 24/7 online no Hetzner!**
