#!/bin/bash

# 🚀 Script de déploiement automatique pour LWS
# Usage: ./deploy-lws.sh [web|vps|docker]

set -e

echo "🌐 Déploiement WiFi Manager sur LWS"
echo "=================================="

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'affichage
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifications préliminaires
check_requirements() {
    print_status "Vérification des prérequis..."
    
    if [ ! -f "app.py" ]; then
        print_error "Fichier app.py non trouvé. Êtes-vous dans le bon répertoire ?"
        exit 1
    fi
    
    if [ ! -f "requirements.txt" ]; then
        print_error "Fichier requirements.txt non trouvé."
        exit 1
    fi
    
    print_success "Prérequis vérifiés"
}

# Déploiement sur hébergement web LWS
deploy_web() {
    print_status "Préparation pour hébergement web LWS..."
    
    # Créer le répertoire de déploiement
    mkdir -p deploy-web
    
    # Copier les fichiers nécessaires
    cp -r app.py config.py security.py templates/ requirements.txt deploy-web/
    cp passenger_wsgi.py .htaccess deploy-web/
    
    # Créer l'archive
    cd deploy-web
    tar -czf ../wifi-manager-web.tar.gz *
    cd ..
    
    print_success "Archive créée : wifi-manager-web.tar.gz"
    print_warning "Étapes suivantes :"
    echo "1. Uploadez wifi-manager-web.tar.gz via FTP/SFTP"
    echo "2. Connectez-vous en SSH et extrayez : tar -xzf wifi-manager-web.tar.gz"
    echo "3. Installez les dépendances : pip3 install --user -r requirements.txt"
    echo "4. Configurez vos variables d'environnement"
}

# Déploiement sur VPS LWS
deploy_vps() {
    print_status "Préparation pour VPS LWS..."
    
    # Vérifier la présence de Git
    if ! command -v git &> /dev/null; then
        print_error "Git n'est pas installé"
        exit 1
    fi
    
    print_status "Création du script d'installation VPS..."
    
    cat > install-vps.sh << 'EOF'
#!/bin/bash
# Script d'installation automatique pour VPS LWS

set -e

echo "🔧 Installation sur VPS LWS..."

# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des dépendances
sudo apt install python3 python3-pip python3-venv nginx git certbot python3-certbot-nginx -y

# Création de l'utilisateur application
sudo adduser --system --group --home /home/wifimanager wifimanager

# Clone du repository
sudo -u wifimanager git clone https://github.com/franklin-mireb/Wifi-.git /home/wifimanager/Wifi-

# Configuration de l'environnement virtuel
cd /home/wifimanager/Wifi-
sudo -u wifimanager python3 -m venv venv
sudo -u wifimanager venv/bin/pip install -r requirements.txt
sudo -u wifimanager venv/bin/pip install gunicorn

# Création des répertoires de logs
sudo -u wifimanager mkdir -p /home/wifimanager/logs

# Installation du service systemd
sudo cp wifi-manager.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable wifi-manager

# Configuration Nginx
sudo cp nginx.lws.conf /etc/nginx/sites-available/wifi-manager
sudo ln -sf /etc/nginx/sites-available/wifi-manager /etc/nginx/sites-enabled/
sudo nginx -t

# Configuration SSL Let's Encrypt
read -p "Nom de domaine (ex: monsite.com): " DOMAIN
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN

# Démarrage des services
sudo systemctl start wifi-manager
sudo systemctl reload nginx

echo "✅ Installation terminée !"
echo "🌐 Votre application est disponible sur : https://$DOMAIN"
EOF

    chmod +x install-vps.sh
    
    print_success "Script d'installation VPS créé : install-vps.sh"
    print_warning "Étapes suivantes :"
    echo "1. Copiez install-vps.sh sur votre VPS"
    echo "2. Exécutez : chmod +x install-vps.sh && ./install-vps.sh"
    echo "3. Suivez les instructions pour configurer le domaine"
}

# Déploiement Docker
deploy_docker() {
    print_status "Préparation pour déploiement Docker..."
    
    # Créer docker-compose pour production
    cat > docker-compose.lws.yml << 'EOF'
version: '3.8'

services:
  wifi-manager:
    build: .
    container_name: wifi-manager-lws
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY:-change-this-secret-key}
    volumes:
      - ./logs:/app/logs
    networks:
      - wifi-network

  nginx:
    image: nginx:alpine
    container_name: wifi-nginx-lws
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.lws.conf:/etc/nginx/conf.d/default.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - wifi-manager
    restart: unless-stopped
    networks:
      - wifi-network

networks:
  wifi-network:
    driver: bridge

volumes:
  logs:
EOF

    # Créer le script de déploiement Docker
    cat > deploy-docker.sh << 'EOF'
#!/bin/bash
# Déploiement Docker sur LWS

set -e

echo "🐳 Déploiement Docker WiFi Manager..."

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    echo "Installation de Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

# Vérifier Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "Installation de Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Configuration des variables d'environnement
if [ ! -f .env ]; then
    echo "SECRET_KEY=$(openssl rand -base64 32)" > .env
    echo "FLASK_ENV=production" >> .env
fi

# Construction et démarrage
docker-compose -f docker-compose.lws.yml up -d --build

echo "✅ Déploiement Docker terminé !"
echo "🌐 Application accessible sur http://localhost"
EOF

    chmod +x deploy-docker.sh
    
    print_success "Configuration Docker créée"
    print_warning "Étapes suivantes :"
    echo "1. Copiez tous les fichiers sur votre serveur LWS"
    echo "2. Exécutez : ./deploy-docker.sh"
    echo "3. Configurez votre reverse proxy/domaine"
}

# Menu principal
main() {
    check_requirements
    
    if [ $# -eq 0 ]; then
        echo ""
        echo "Choisissez le type de déploiement LWS :"
        echo "1) Hébergement Web (mutualisé/pro)"
        echo "2) VPS LWS"
        echo "3) Docker (VPS/Cloud)"
        echo ""
        read -p "Votre choix (1-3): " choice
        
        case $choice in
            1) deploy_web ;;
            2) deploy_vps ;;
            3) deploy_docker ;;
            *) print_error "Choix invalide" && exit 1 ;;
        esac
    else
        case $1 in
            web) deploy_web ;;
            vps) deploy_vps ;;
            docker) deploy_docker ;;
            *) 
                echo "Usage: $0 [web|vps|docker]"
                exit 1
                ;;
        esac
    fi
    
    echo ""
    print_success "Préparation terminée !"
    echo ""
    echo "📚 Documentation complète : DEPLOYMENT_LWS.md"
    echo "🌐 Support LWS : https://aide.lws.fr/"
    echo ""
}

# Exécution du script
main "$@"
