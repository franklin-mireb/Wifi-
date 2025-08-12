# 🌐 Guide de Déploiement sur LWS

## 📋 **Prérequis pour LWS**

### 🎯 **Types d'Hébergement LWS Compatibles :**

1. **LWS Hébergement Web Pro** (Recommandé)
   - Support Python/Flask
   - Accès SSH
   - Base de données MySQL/PostgreSQL
   - SSL gratuit

2. **LWS VPS/Cloud**
   - Contrôle total du serveur
   - Installation personnalisée
   - Idéal pour applications complexes

3. **LWS Hébergement Mutualisé** (Limité)
   - Support Python basique
   - Limitations sur les ports et services

## 🚀 **Méthode 1 : Déploiement sur Hébergement Web Pro**

### Étape 1 : Préparation des Fichiers

```bash
# 1. Cloner le repository
git clone https://github.com/franklin-mireb/Wifi-.git
cd Wifi-

# 2. Créer un archive pour l'upload
tar -czf wifi-manager.tar.gz \
    app.py \
    config.py \
    security.py \
    run.py \
    templates/ \
    static/ \
    requirements.txt \
    README.md
```

### Étape 2 : Configuration pour LWS

Créer un fichier `.htaccess` pour Apache :

```apache
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^(.*)$ /app.py/$1 [QSA,L]

# Redirection HTTPS (optionnel)
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
```

Créer un fichier `passenger_wsgi.py` (requis par LWS) :

```python
#!/usr/bin/env python3
import sys
import os

# Ajouter le répertoire de l'application au path
sys.path.insert(0, os.path.dirname(__file__))

from app import app as application

if __name__ == "__main__":
    application.run()
```

### Étape 3 : Upload via FTP/SFTP

```bash
# Connexion SFTP
sftp votre-login@votre-domaine.com
put wifi-manager.tar.gz
quit

# Ou via FileZilla/WinSCP avec les identifiants LWS
```

### Étape 4 : Installation sur le Serveur

```bash
# Connexion SSH
ssh votre-login@votre-domaine.com

# Extraction
tar -xzf wifi-manager.tar.gz

# Installation des dépendances
pip3 install --user -r requirements.txt

# Configuration des permissions
chmod 755 app.py
chmod 755 passenger_wsgi.py
```

## 🔧 **Méthode 2 : Déploiement sur VPS LWS**

### Étape 1 : Configuration du VPS

```bash
# Connexion au VPS
ssh root@votre-vps-ip

# Mise à jour du système
apt update && apt upgrade -y

# Installation de Python et dépendances
apt install python3 python3-pip python3-venv nginx git -y

# Création de l'utilisateur application
adduser wifimanager
usermod -aG sudo wifimanager
```

### Étape 2 : Déploiement de l'Application

```bash
# Basculer vers l'utilisateur application
su - wifimanager

# Cloner le repository
git clone https://github.com/franklin-mireb/Wifi-.git
cd Wifi-

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Installer Gunicorn pour la production
pip install gunicorn
```

### Étape 3 : Configuration Gunicorn

Créer `/home/wifimanager/Wifi-/gunicorn.conf.py` :

```python
# Configuration Gunicorn pour production
bind = "127.0.0.1:5000"
workers = 2
worker_class = "sync"
timeout = 30
keepalive = 30
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

### Étape 4 : Service Systemd

Créer `/etc/systemd/system/wifi-manager.service` :

```ini
[Unit]
Description=WiFi Manager Flask App
After=network.target

[Service]
User=wifimanager
Group=wifimanager
WorkingDirectory=/home/wifimanager/Wifi-
Environment="PATH=/home/wifimanager/Wifi-/venv/bin"
ExecStart=/home/wifimanager/Wifi-/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### Étape 5 : Configuration Nginx

Créer `/etc/nginx/sites-available/wifi-manager` :

```nginx
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Servir les fichiers statiques directement
    location /static {
        alias /home/wifimanager/Wifi-/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Étape 6 : Activation et Démarrage

```bash
# Activer le site Nginx
ln -s /etc/nginx/sites-available/wifi-manager /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Démarrer le service
systemctl enable wifi-manager
systemctl start wifi-manager
systemctl status wifi-manager
```

## 🔒 **Configuration SSL avec Let's Encrypt**

```bash
# Installation Certbot
apt install certbot python3-certbot-nginx -y

# Génération du certificat
certbot --nginx -d votre-domaine.com -d www.votre-domaine.com

# Test du renouvellement automatique
certbot renew --dry-run
```

## 📊 **Méthode 3 : Déploiement Docker sur LWS**

### Étape 1 : Préparation

```bash
# Installation Docker sur VPS LWS
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Installation Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### Étape 2 : Configuration Docker

Créer `docker-compose.prod.yml` :

```yaml
version: '3.8'

services:
  wifi-manager:
    build: .
    container_name: wifi-manager-prod
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./logs:/app/logs
    networks:
      - wifi-network

  nginx:
    image: nginx:alpine
    container_name: wifi-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - wifi-manager
    restart: unless-stopped
    networks:
      - wifi-network

networks:
  wifi-network:
    driver: bridge
```

### Étape 3 : Déploiement

```bash
# Cloner et déployer
git clone https://github.com/franklin-mireb/Wifi-.git
cd Wifi-

# Configurer les variables d'environnement
echo "SECRET_KEY=votre-clé-secrète-très-longue" > .env

# Démarrer en production
docker-compose -f docker-compose.prod.yml up -d

# Vérifier les logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 🎯 **Configuration Spécifique LWS**

### Variables d'Environnement

```bash
# .env pour LWS
SECRET_KEY=votre-clé-ultra-sécurisée-pour-production
FLASK_ENV=production
DATABASE_URL=mysql://user:password@localhost/wifi_manager
LWS_MODE=true
DEBUG=false
```

### Adaptation du Code pour LWS

Modifier `config.py` :

```python
import os

class LWSConfig(Config):
    """Configuration spécifique pour LWS"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Configuration base de données LWS
    if os.environ.get('LWS_MODE'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Adaptations pour l'hébergement mutualisé
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))
```

## 📋 **Checklist de Déploiement LWS**

### Avant le Déploiement :

- [ ] ✅ Compte LWS activé avec support Python
- [ ] ✅ Nom de domaine configuré
- [ ] ✅ Accès SSH/FTP configuré
- [ ] ✅ Variables d'environnement définies
- [ ] ✅ SSL configuré

### Configuration :

- [ ] ✅ `passenger_wsgi.py` créé
- [ ] ✅ `.htaccess` configuré (hébergement web)
- [ ] ✅ Dépendances installées
- [ ] ✅ Permissions correctes

### Post-Déploiement :

- [ ] ✅ Application accessible
- [ ] ✅ SSL fonctionnel
- [ ] ✅ Logs vérifiés
- [ ] ✅ Performance testée

## 🛠️ **Dépannage LWS**

### Problèmes Courants :

1. **Erreur 500** : Vérifier les logs LWS
2. **Import Error** : Installer les dépendances avec `--user`
3. **Permission Denied** : Ajuster les permissions fichiers
4. **Port déjà utilisé** : Changer le port dans la configuration

### Commandes de Debug :

```bash
# Vérifier les logs LWS
tail -f ~/logs/error.log

# Tester l'application localement
python3 app.py

# Vérifier les dépendances
pip3 list --user
```

## 💰 **Coûts Estimés LWS**

- **Hébergement Web Pro :** ~10€/mois
- **VPS Starter :** ~15€/mois
- **VPS Performance :** ~30€/mois
- **SSL :** Gratuit avec Let's Encrypt

## 📞 **Support LWS**

- **Documentation :** https://aide.lws.fr/
- **Support :** Via espace client LWS
- **Forum :** Communauté LWS

---

**🎯 Votre application sera accessible sur :** `https://votre-domaine.com`
