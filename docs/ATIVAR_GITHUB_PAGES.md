# 🚀 Ativar GitHub Pages - 5 Minutos

## ✅ Passo 1: Ativar GitHub Pages

1. Acesse: https://github.com/avilaops/griffedaprata/settings/pages

2. Configure:
   ```
   Source: Deploy from a branch
   Branch: main
   Folder: / (root)
   ```

3. Clique em **Save**

4. Aguarde 1-2 minutos

5. Seu site estará em: **https://avilaops.github.io/griffedaprata/**

## ✅ Passo 2: Configurar Domínio Personalizado

### No GitHub:

1. Na mesma página (Settings > Pages)
2. Em **Custom domain**, digite: `griffedaprata.com.br`
3. Clique em **Save**
4. Marque: ☑️ **Enforce HTTPS**

### No Registro.br (ou seu provedor):

Configure estes registros DNS:

```dns
# Frontend (GitHub Pages)
Tipo: A
Nome: @
Valor: 185.199.108.153
TTL: 3600

Tipo: A  
Nome: @
Valor: 185.199.109.153
TTL: 3600

Tipo: A
Nome: @
Valor: 185.199.110.153
TTL: 3600

Tipo: A
Nome: @
Valor: 185.199.111.153
TTL: 3600

# WWW
Tipo: CNAME
Nome: www
Valor: avilaops.github.io
TTL: 3600

# Backend API (Hetzner)
Tipo: A
Nome: api
Valor: SEU_IP_HETZNER (ex: 65.108.123.45)
TTL: 3600
```

## ⏱️ Aguardar Propagação DNS

- Tempo: 5 minutos a 24 horas
- Normalmente: 30 minutos
- Testar: https://dnschecker.org/

## ✅ Passo 3: Testar

```bash
# Testar frontend
https://griffedaprata.com.br

# Testar backend (depois de configurar Hetzner)
https://api.griffedaprata.com.br/api/produtos
```

## 🎉 Pronto!

Seu site está no ar:
- 🌐 Frontend: GitHub Pages (GRÁTIS)
- ⚡ CDN global (super rápido)
- 🔒 HTTPS automático
- 🚀 Deploy: apenas `git push`

## 📝 Próximo: Deploy Backend no Hetzner

Veja: **DEPLOY_HETZNER.md** para configurar as APIs
