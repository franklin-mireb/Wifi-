#!/bin/bash

# 🚀 Script de Déploiement Production WiFi Manager
# Auteur: GitHub Copilot
# Date: $(date)

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'affichage
print_step() {
    echo -e "${BLUE}[ÉTAPE]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCÈS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[ATTENTION]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERREUR]${NC} $1"
}

# Banner
echo -e "${BLUE}"
echo "╔════════════════════════════════════════╗"
echo "║      🚀 DÉPLOIEMENT PRODUCTION         ║"
echo "║         WiFi Manager + Vouchers        ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# Vérification des prérequis
print_step "Vérification des prérequis..."

if ! command -v docker &> /dev/null; then
    print_error "Docker n'est pas installé!"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose n'est pas installé!"
    exit 1
fi

print_success "Prérequis OK"

# Configuration interactive
echo ""
print_step "Configuration de production"

read -p "📧 Votre email pour SSL (Let's Encrypt): " EMAIL
read -p "🌐 Votre nom de domaine (ex: monwifi.com): " DOMAIN
read -p "🔑 Clé secrète Flask (32+ caractères): " SECRET_KEY

# Validation
if [[ ${#SECRET_KEY} -lt 32 ]]; then
    print_error "La clé secrète doit faire au moins 32 caractères!"
    exit 1
fi

echo ""
print_step "Configuration du routeur WiFi"
read -p "📡 IP du routeur (ex: 192.168.1.1): " ROUTER_IP
read -p "👤 Username routeur: " ROUTER_USER
read -s -p "🔐 Mot de passe routeur: " ROUTER_PASS
echo ""

echo ""
print_step "Configuration paiements"
echo "1) Mode démo (paiements simulés)"
echo "2) Stripe (paiements réels)"
read -p "Choisissez (1-2): " PAYMENT_MODE

STRIPE_PUBLIC_KEY=""
STRIPE_SECRET_KEY=""

if [[ $PAYMENT_MODE == "2" ]]; then
    read -p "🔑 Clé publique Stripe (pk_live_...): " STRIPE_PUBLIC_KEY
    read -s -p "🔐 Clé secrète Stripe (sk_live_...): " STRIPE_SECRET_KEY
    echo ""
fi

# Création du fichier de configuration production
print_step "Création de la configuration production..."

cat > .env.prod << EOF
# Configuration Production WiFi Manager
SECRET_KEY=$SECRET_KEY
FLASK_ENV=production
DEBUG=false
HOST=0.0.0.0
PORT=5000

# Configuration Routeur
ROUTER_IP=$ROUTER_IP
ROUTER_USER=$ROUTER_USER
ROUTER_PASS=$ROUTER_PASS

# Configuration SSL
DOMAIN=$DOMAIN
EMAIL=$EMAIL

# Configuration Paiements
PAYMENT_MODE=$PAYMENT_MODE
STRIPE_PUBLIC_KEY=$STRIPE_PUBLIC_KEY
STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY
EOF

print_success "Configuration créée"

# Mise à jour du fichier config.py pour la production
print_step "Adaptation du code pour la production..."

cat > config_prod.py << 'EOF'
import os
from config import Config

class ProductionConfig(Config):
    """Configuration optimisée pour la production"""
    
    DEBUG = False
    TESTING = False
    
    # Sécurité renforcée
    SECRET_KEY = os.environ.get('SECRET_KEY')
    WTF_CSRF_ENABLED = True
    
    # Configuration routeur réel
    ROUTER_CONFIG = {
        'ip': os.environ.get('ROUTER_IP', '192.168.1.1'),
        'username': os.environ.get('ROUTER_USER', 'admin'),
        'password': os.environ.get('ROUTER_PASS', ''),
        'interface': 'wlan0',
        'timeout': 10
    }
    
    # Sécurité avancée
    SECURITY_CONFIG = {
        'rate_limit_enabled': True,
        'max_attempts': 3,
        'lockout_duration': 900,  # 15 minutes
        'require_https': True,
        'secure_cookies': True
    }
    
    # Configuration base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///production.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/app/logs/production.log'
EOF

# Configuration Nginx
print_step "Configuration du proxy Nginx..."

mkdir -p nginx

cat > nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream wifi_manager {
        server wifi-manager:5000;
    }
    
    # Redirection HTTP vers HTTPS
    server {
        listen 80;
        server_name $DOMAIN www.$DOMAIN;
        return 301 https://\$server_name\$request_uri;
    }
    
    # Configuration HTTPS
    server {
        listen 443 ssl http2;
        server_name $DOMAIN www.$DOMAIN;
        
        ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
        
        # Sécurité SSL
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        
        # Headers de sécurité
        add_header Strict-Transport-Security "max-age=63072000" always;
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        
        location / {
            proxy_pass http://wifi_manager;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
        
        # Fichiers statiques
        location /static {
            proxy_pass http://wifi_manager;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
EOF

# Docker Compose production
print_step "Configuration Docker production..."

cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  wifi-manager:
    build: .
    container_name: wifi-manager-prod
    restart: unless-stopped
    env_file:
      - .env.prod
    volumes:
      - ./logs:/app/logs
      - ./vouchers.json:/app/vouchers.json
      - ./config_prod.py:/app/config.py
    networks:
      - wifi-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: wifi-nginx-prod
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - wifi-manager
    networks:
      - wifi-network

  redis:
    image: redis:alpine
    container_name: wifi-redis
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - wifi-network

volumes:
  redis_data:

networks:
  wifi-network:
    driver: bridge
EOF

# Installation SSL
print_step "Installation du certificat SSL..."

# Arrêt temporaire de nginx si il tourne
sudo systemctl stop nginx 2>/dev/null || true

# Installation certbot
if ! command -v certbot &> /dev/null; then
    print_step "Installation de Certbot..."
    sudo apt update
    sudo apt install -y certbot
fi

# Génération du certificat
print_step "Génération du certificat SSL pour $DOMAIN..."
sudo certbot certonly --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

if [[ $? -eq 0 ]]; then
    print_success "Certificat SSL généré avec succès"
else
    print_error "Échec de la génération du certificat SSL"
    print_warning "Vérifiez que:"
    echo "  - Le domaine $DOMAIN pointe vers cette IP"
    echo "  - Les ports 80 et 443 sont ouverts"
    echo "  - Aucun autre service n'utilise ces ports"
    exit 1
fi

# Configuration du renouvellement automatique
print_step "Configuration du renouvellement automatique SSL..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

# Ajout du endpoint de santé
print_step "Ajout du monitoring de santé..."

cat >> app.py << 'EOF'

@app.route('/health')
def health_check():
    """Endpoint de vérification de santé"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }, 200
EOF

# Construction et démarrage
print_step "Construction de l'image Docker..."
docker build -t wifi-manager-prod .

print_step "Démarrage des services..."
docker-compose -f docker-compose.prod.yml up -d

# Attendre que les services démarrent
print_step "Attente du démarrage des services..."
sleep 30

# Vérification de la santé des services
print_step "Vérification des services..."

if docker ps | grep -q "wifi-manager-prod"; then
    print_success "WiFi Manager démarré"
else
    print_error "Échec du démarrage de WiFi Manager"
    docker-compose -f docker-compose.prod.yml logs wifi-manager
    exit 1
fi

if docker ps | grep -q "wifi-nginx-prod"; then
    print_success "Nginx démarré"
else
    print_error "Échec du démarrage de Nginx"
    docker-compose -f docker-compose.prod.yml logs nginx
    exit 1
fi

# Test de connectivité
print_step "Test de connectivité..."

if curl -k -s https://$DOMAIN/health > /dev/null; then
    print_success "Application accessible via HTTPS"
else
    print_warning "L'application pourrait ne pas être encore accessible"
    print_warning "Cela peut prendre quelques minutes..."
fi

# Affichage des informations finales
echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      🎉 DÉPLOIEMENT TERMINÉ!           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}🌐 Application disponible sur:${NC}"
echo -e "   https://$DOMAIN"
echo -e "   https://www.$DOMAIN"
echo ""

echo -e "${BLUE}🎫 Système de vouchers:${NC}"
echo -e "   https://$DOMAIN/vouchers"
echo ""

echo -e "${BLUE}🔧 Gestion des services:${NC}"
echo -e "   docker-compose -f docker-compose.prod.yml logs -f     # Voir les logs"
echo -e "   docker-compose -f docker-compose.prod.yml restart     # Redémarrer"
echo -e "   docker-compose -f docker-compose.prod.yml down        # Arrêter"
echo ""

echo -e "${BLUE}📊 Monitoring:${NC}"
echo -e "   https://$DOMAIN/health                                # Santé de l'app"
echo -e "   docker stats                                          # Statistiques"
echo ""

if [[ $PAYMENT_MODE == "1" ]]; then
    echo -e "${YELLOW}⚠️  Mode démo activé - Configurez Stripe pour les vrais paiements${NC}"
fi

echo -e "${GREEN}🚀 Votre WiFi Manager est en production!${NC}"

# Sauvegarde de la configuration
mkdir -p /backup
cp .env.prod /backup/
cp docker-compose.prod.yml /backup/
print_success "Configuration sauvegardée dans /backup/"

exit 0
