#!/bin/bash

# Script de déploiement rapide du Gestionnaire WiFi
# Usage: ./deploy.sh

set -e

echo "🚀 Déploiement du Gestionnaire WiFi"
echo "===================================="

# Vérifications préliminaires
echo "📋 Vérifications..."

if [ ! -f "app.py" ]; then
    echo "❌ Fichier app.py non trouvé"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ Fichier requirements.txt non trouvé"
    exit 1
fi

# Configuration de l'environnement virtuel
echo "🐍 Configuration de l'environnement Python..."

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt

# Vérification de la syntaxe
echo "🔍 Vérification de la syntaxe..."
python -m py_compile app.py
python -m py_compile config.py
python -m py_compile security.py

# Tests
echo "🧪 Exécution des tests..."
python test_app.py

# Configuration de l'environnement
echo "⚙️  Configuration de l'environnement..."

if [ ! -f ".env" ]; then
    echo "Création du fichier .env..."
    cat > .env << EOF
SECRET_KEY=$(openssl rand -base64 32)
FLASK_ENV=production
PORT=5000
HOST=0.0.0.0
DEBUG=false
EOF
fi

# Création des répertoires nécessaires
mkdir -p logs
mkdir -p ssl

# Test de l'application
echo "🔬 Test de l'application..."
timeout 10s python run.py --env production --port 9001 > /dev/null 2>&1 &
APP_PID=$!
sleep 3

if kill -0 $APP_PID 2>/dev/null; then
    echo "✅ Application démarrée avec succès"
    kill $APP_PID
else
    echo "❌ Erreur lors du démarrage de l'application"
    exit 1
fi

echo ""
echo "✅ Déploiement terminé avec succès !"
echo ""
echo "📁 Fichiers prêts pour le déploiement :"
echo "   - app.py (application principale)"
echo "   - requirements.txt (dépendances)"
echo "   - .env (configuration)"
echo "   - templates/ (interface web)"
echo ""
echo "🚀 Pour démarrer l'application :"
echo "   ./run.py --env production"
echo ""
echo "🐳 Pour déploiement Docker :"
echo "   ./deploy-docker.sh"
echo ""
echo "📚 Consultez DEPLOYMENT_LWS.md pour plus d'informations"
