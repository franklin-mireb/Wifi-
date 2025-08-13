# 🚀 GUIDE DÉPLOIEMENT PRODUCTION

## 📋 **CHOIX D'HÉBERGEMENT**

### 🏆 **RECOMMANDÉ - VPS/Cloud**
- **Control total** du serveur
- **Docker** supporté
- **SSL** gratuit
- **Performance** optimale

### 💡 **ALTERNATIF - Hébergement Web**
- **Plus simple** à configurer
- **Moins cher** (~10€/mois)
- **Limitations** sur certaines fonctionnalités

## 🎯 **DÉPLOIEMENT RAPIDE VPS**

### 1. **PRÉPARER LE VPS**

```bash
# Connexion au serveur
ssh root@votre-serveur-ip

# Mise à jour système
apt update && apt upgrade -y

# Installation Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Installation Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### 2. **CLONER L'APPLICATION**

```bash
# Cloner votre repository
git clone https://github.com/franklin-mireb/Wifi-.git
cd Wifi-

# Configuration production
cp docker-compose.prod.yml docker-compose.yml
```

### 3. **CONFIGURATION SSL + DOMAINE**

```bash
# Installation Nginx et SSL
apt install nginx certbot python3-certbot-nginx -y

# Configuration domaine (remplacez par votre domaine)
nano /etc/nginx/sites-available/wifi-manager
```

Contenu du fichier :
```nginx
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. **ACTIVATION**

```bash
# Activer le site
ln -s /etc/nginx/sites-available/wifi-manager /etc/nginx/sites-enabled/
systemctl reload nginx

# Générer certificat SSL
certbot --nginx -d votre-domaine.com

# Démarrer l'application
docker-compose up -d
```

## 🔧 **CONFIGURATION PRODUCTION**

### **Variables d'Environnement**

```bash
# Créer le fichier .env
nano .env
```

Contenu :
```env
SECRET_KEY=votre-clé-super-secrète-de-32-caractères-minimum
FLASK_ENV=production
DEBUG=false
HOST=0.0.0.0
PORT=5000
```

### **Configuration Routeur WiFi RÉEL**

Modifier `config.py` :
```python
class ProductionConfig(Config):
    DEBUG = False
    
    # VOS VRAIES DONNÉES ROUTEUR
    ROUTER_CONFIG = {
        'ip': '192.168.1.1',      # IP réelle de votre routeur
        'username': 'admin',       # Vraie username
        'password': 'votre-pass',  # Vrai mot de passe
        'interface': 'wlan0'       # Interface WiFi réelle
    }
    
    # SÉCURITÉ RENFORCÉE
    RATE_LIMIT = {
        'enabled': True,
        'attempts': 3,           # 3 tentatives max
        'window': 900           # 15 minutes
    }
```

## 💳 **SYSTÈME DE PAIEMENT RÉEL**

### **Intégration Stripe** (Recommandé)

```python
# Dans voucher_system.py - remplacer PaymentSimulator
import stripe

class StripePaymentProcessor:
    def __init__(self, api_key):
        stripe.api_key = api_key
    
    def create_payment_intent(self, amount, currency='usd'):
        """Créer intention de paiement Stripe"""
        return stripe.PaymentIntent.create(
            amount=int(amount * 100),  # En centimes
            currency=currency,
            automatic_payment_methods={'enabled': True}
        )
    
    def confirm_payment(self, payment_intent_id):
        """Confirmer le paiement"""
        return stripe.PaymentIntent.retrieve(payment_intent_id)
```

### **Configuration Stripe**

```bash
# Variables d'environnement Stripe
echo "STRIPE_PUBLIC_KEY=pk_live_votre_clé_publique" >> .env
echo "STRIPE_SECRET_KEY=sk_live_votre_clé_secrète" >> .env
```

## 📊 **MONITORING & LOGS**

### **Logs Centralisés**

```bash
# Voir les logs en temps réel
docker-compose logs -f

# Logs spécifiques
docker logs wifi-manager -f
```

### **Monitoring Système**

```bash
# Installation htop pour monitoring
apt install htop

# Vérifier l'utilisation
htop
docker stats
```

## 🔒 **SÉCURITÉ PRODUCTION**

### **Firewall UFW**

```bash
# Installer et configurer firewall
ufw enable
ufw allow ssh
ufw allow 80
ufw allow 443
ufw status
```

### **Sauvegarde Automatique**

```bash
# Script de sauvegarde (sauvegarder.sh)
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /backup/wifi-manager-$DATE.tar.gz /root/Wifi-
find /backup -name "wifi-manager-*.tar.gz" -mtime +7 -delete
```

## 🎯 **TESTS PRODUCTION**

### **Checklist de Vérification**

```bash
# Test connectivité
curl -I https://votre-domaine.com

# Test API vouchers
curl -X POST https://votre-domaine.com/api/voucher/purchase \
  -H "Content-Type: application/json" \
  -d '{"plan":"monthly","amount":7}'

# Test interface admin
curl https://votre-domaine.com/admin
```

## 📈 **OPTIMISATION PERFORMANCE**

### **Configuration Redis** (Cache)

```bash
# Installation Redis
apt install redis-server

# Configuration dans app.py
pip install redis flask-caching
```

### **Configuration Base de Données**

```bash
# Installation PostgreSQL
apt install postgresql postgresql-contrib
sudo -u postgres createdb wifi_manager
```

## 💰 **COÛTS ESTIMÉS**

| Service | Prix/mois | Description |
|---------|-----------|-------------|
| **VPS 2GB** | 15-25€ | Serveur principal |
| **Domaine** | 1-2€ | Nom de domaine |
| **SSL** | Gratuit | Let's Encrypt |
| **Stripe** | 2.9% + 0.25€ | Frais paiement |
| **TOTAL** | ~20€/mois | Hors revenus vouchers |

## 🚀 **SCRIPT DE DÉPLOIEMENT AUTOMATIQUE**

Créons un script qui fait tout automatiquement :
