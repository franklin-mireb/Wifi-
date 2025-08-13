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
    echo "⚠️  Redémarrez votre session pour que les modifications prennent effet"
fi

# Vérifier Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "Installation de Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Configuration des variables d'environnement
if [ ! -f .env ]; then
    echo "Création du fichier .env..."
    echo "SECRET_KEY=$(openssl rand -base64 32)" > .env
    echo "FLASK_ENV=production" >> .env
    echo "PORT=5000" >> .env
    echo "HOST=0.0.0.0" >> .env
fi

# Créer les répertoires nécessaires
mkdir -p logs ssl

# Arrêter les conteneurs existants
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# Construction et démarrage
echo "🔨 Construction des images..."
docker-compose -f docker-compose.prod.yml build

echo "🚀 Démarrage des services..."
docker-compose -f docker-compose.prod.yml up -d

echo "✅ Déploiement Docker terminé !"
echo "🌐 Application accessible sur http://localhost:5000"
echo "📊 Logs des conteneurs : docker-compose -f docker-compose.prod.yml logs -f"
echo "🛑 Arrêter les services : docker-compose -f docker-compose.prod.yml down"
