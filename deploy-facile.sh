#!/bin/bash

# 🚀 DÉPLOIEMENT ULTRA-FACILE - Gestionnaire WiFi
# Ce script fait TOUT automatiquement !

set -e

clear
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                  🌐 GESTIONNAIRE WIFI                         ║"
echo "║                Déploiement Automatique                       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Variables de couleur
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}🔄 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# ÉTAPE 1: Choix du type de déploiement
echo "Choisissez votre type de déploiement :"
echo ""
echo "1) 🖥️  Local (pour tester sur cet ordinateur)"
echo "2) 🐳 Docker (recommandé pour serveurs)"
echo "3) 🌐 Hébergement Web LWS (mutualisé)"
echo "4) 🖥️  VPS LWS (serveur dédié)"
echo ""
read -p "Votre choix (1-4) : " DEPLOY_TYPE

case $DEPLOY_TYPE in
    1)
        echo ""
        print_step "Déploiement LOCAL choisi"
        
        # Installation des dépendances
        print_step "Installation des dépendances Python..."
        if [ ! -d ".venv" ]; then
            python3 -m venv .venv
        fi
        
        source .venv/bin/activate
        pip install -r requirements.txt > /dev/null 2>&1
        print_success "Dépendances installées"
        
        # Configuration
        print_step "Configuration de l'environnement..."
        if [ ! -f ".env" ]; then
            cat > .env << EOF
SECRET_KEY=$(openssl rand -base64 32)
FLASK_ENV=development
PORT=5000
HOST=0.0.0.0
DEBUG=true
EOF
        fi
        print_success "Configuration créée"
        
        # Test de l'application
        print_step "Test de l'application..."
        python -c "from app import app; print('✅ Import réussi')" 2>/dev/null
        print_success "Application validée"
        
        echo ""
        echo "🎉 DÉPLOIEMENT LOCAL TERMINÉ !"
        echo ""
        echo "🚀 Pour démarrer votre application :"
        echo "   cd $(pwd)"
        echo "   source .venv/bin/activate"
        echo "   python run.py"
        echo ""
        echo "🌐 Ensuite ouvrez : http://localhost:5000"
        echo "🎮 Mode démo : IP 192.168.1.100, user: demo, pass: demo"
        echo ""
        
        read -p "Voulez-vous démarrer maintenant ? (o/n) : " START_NOW
        if [ "$START_NOW" = "o" ] || [ "$START_NOW" = "O" ]; then
            echo ""
            print_step "Démarrage de l'application..."
            echo "🌐 Application disponible sur : http://localhost:5000"
            echo "🛑 Appuyez sur Ctrl+C pour arrêter"
            echo ""
            python run.py
        fi
        ;;
        
    2)
        echo ""
        print_step "Déploiement DOCKER choisi"
        
        # Vérifier Docker
        if ! command -v docker &> /dev/null; then
            print_warning "Docker n'est pas installé. Installation..."
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            sudo usermod -aG docker $USER
            print_success "Docker installé (redémarrez votre session)"
        fi
        
        # Créer le fichier .env
        print_step "Configuration Docker..."
        cat > .env << EOF
SECRET_KEY=$(openssl rand -base64 32)
FLASK_ENV=production
PORT=5000
HOST=0.0.0.0
EOF
        
        # Créer les répertoires
        mkdir -p logs ssl
        
        # Construction et démarrage
        print_step "Construction de l'image Docker..."
        docker build -t wifi-manager . > /dev/null 2>&1
        print_success "Image Docker créée"
        
        print_step "Démarrage du conteneur..."
        docker run -d \
            --name wifi-manager \
            --restart unless-stopped \
            -p 5000:5000 \
            -v $(pwd)/logs:/app/logs \
            -v $(pwd)/.env:/app/.env \
            wifi-manager > /dev/null 2>&1
        print_success "Conteneur démarré"
        
        echo ""
        echo "🎉 DÉPLOIEMENT DOCKER TERMINÉ !"
        echo ""
        echo "🌐 Application disponible sur : http://localhost:5000"
        echo "🎮 Mode démo : IP 192.168.1.100, user: demo, pass: demo"
        echo ""
        echo "🔧 Commandes utiles :"
        echo "   docker logs wifi-manager    (voir les logs)"
        echo "   docker stop wifi-manager    (arrêter)"
        echo "   docker start wifi-manager   (redémarrer)"
        echo ""
        ;;
        
    3)
        echo ""
        print_step "Déploiement HÉBERGEMENT WEB LWS choisi"
        
        # Créer le package de déploiement
        print_step "Création du package de déploiement..."
        mkdir -p deploy-web
        
        # Copier les fichiers essentiels
        cp app.py config.py security.py requirements.txt deploy-web/
        cp -r templates deploy-web/
        
        # Créer le fichier WSGI pour LWS
        cat > deploy-web/passenger_wsgi.py << 'EOF'
import sys
import os

# Ajouter le répertoire de l'application au path
sys.path.insert(0, os.path.dirname(__file__))

from app import app as application

if __name__ == "__main__":
    application.run()
EOF
        
        # Créer .htaccess
        cat > deploy-web/.htaccess << 'EOF'
PassengerAppRoot /home/votre-compte/votre-domaine.com/
PassengerPython /home/votre-compte/.local/bin/python3
PassengerAppType wsgi
PassengerStartupFile passenger_wsgi.py
EOF
        
        # Créer le fichier de configuration
        cat > deploy-web/.env << EOF
SECRET_KEY=$(openssl rand -base64 32)
FLASK_ENV=production
PORT=80
HOST=0.0.0.0
EOF
        
        # Créer l'archive
        cd deploy-web
        tar -czf ../wifi-manager-web.tar.gz *
        cd ..
        
        print_success "Package créé : wifi-manager-web.tar.gz"
        
        echo ""
        echo "🎉 PACKAGE HÉBERGEMENT WEB CRÉÉ !"
        echo ""
        echo "📦 Fichier à uploader : wifi-manager-web.tar.gz"
        echo ""
        echo "🚀 ÉTAPES SUIVANTES :"
        echo "1. Connectez-vous à votre espace client LWS"
        echo "2. Allez dans l'onglet FTP/SFTP"
        echo "3. Uploadez wifi-manager-web.tar.gz dans votre dossier web"
        echo "4. Connectez-vous en SSH et tapez :"
        echo "   cd ~/votre-domaine.com"
        echo "   tar -xzf wifi-manager-web.tar.gz"
        echo "   pip3 install --user -r requirements.txt"
        echo ""
        echo "🌐 Votre site sera disponible sur : https://votre-domaine.com"
        ;;
        
    4)
        echo ""
        print_step "Déploiement VPS LWS choisi"
        
        # Créer le script d'installation VPS
        cat > install-vps-lws.sh << 'EOF'
#!/bin/bash
# Installation automatique sur VPS LWS

set -e

echo "🔧 Installation sur VPS LWS..."

# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des dépendances
sudo apt install python3 python3-pip python3-venv nginx git certbot python3-certbot-nginx -y

# Création de l'utilisateur
sudo adduser --system --group --home /home/wifimanager wifimanager

# Clone du projet
sudo -u wifimanager git clone https://github.com/franklin-mireb/Wifi-.git /home/wifimanager/app

# Configuration Python
cd /home/wifimanager/app
sudo -u wifimanager python3 -m venv venv
sudo -u wifimanager venv/bin/pip install -r requirements.txt
sudo -u wifimanager venv/bin/pip install gunicorn

# Configuration
sudo -u wifimanager mkdir -p /home/wifimanager/logs
cat > /home/wifimanager/app/.env << EOFENV
SECRET_KEY=$(openssl rand -base64 32)
FLASK_ENV=production
PORT=5000
HOST=127.0.0.1
EOFENV

# Service systemd
sudo tee /etc/systemd/system/wifi-manager.service > /dev/null <<EOFSERVICE
[Unit]
Description=WiFi Manager
After=network.target

[Service]
User=wifimanager
Group=wifimanager
WorkingDirectory=/home/wifimanager/app
Environment=PATH=/home/wifimanager/app/venv/bin
ExecStart=/home/wifimanager/app/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOFSERVICE

# Configuration Nginx
sudo tee /etc/nginx/sites-available/wifi-manager > /dev/null <<EOFNGINX
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOFNGINX

sudo ln -sf /etc/nginx/sites-available/wifi-manager /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Démarrage des services
sudo systemctl daemon-reload
sudo systemctl enable wifi-manager
sudo systemctl start wifi-manager
sudo nginx -t && sudo systemctl reload nginx

echo "✅ Installation terminée !"
echo "🌐 Votre application est disponible sur l'IP de votre VPS"
EOF
        
        chmod +x install-vps-lws.sh
        print_success "Script d'installation VPS créé"
        
        echo ""
        echo "🎉 SCRIPT VPS LWS CRÉÉ !"
        echo ""
        echo "📁 Fichier créé : install-vps-lws.sh"
        echo ""
        echo "🚀 ÉTAPES SUIVANTES :"
        echo "1. Copiez install-vps-lws.sh sur votre VPS LWS"
        echo "2. Connectez-vous en SSH à votre VPS"
        echo "3. Rendez le script exécutable : chmod +x install-vps-lws.sh"
        echo "4. Lancez l'installation : ./install-vps-lws.sh"
        echo ""
        echo "🌐 L'application sera disponible sur l'IP de votre VPS"
        ;;
        
    *)
        print_error "Choix invalide"
        exit 1
        ;;
esac

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    🎉 DÉPLOIEMENT TERMINÉ                    ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "🎮 POUR TESTER EN MODE DÉMO :"
echo "   IP du routeur : 192.168.1.100"
echo "   Utilisateur   : demo"
echo "   Mot de passe  : demo"
echo ""
echo "📞 Support LWS : https://aide.lws.fr/"
echo "📚 Documentation : README.md"
echo ""
