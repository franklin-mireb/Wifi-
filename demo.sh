#!/bin/bash

# 🎮 DÉMO INSTANTANÉE - Gestionnaire WiFi
# Lance l'application immédiatement pour test

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                 🎮 DÉMO INSTANTANÉE                        ║"
echo "║                Gestionnaire WiFi                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Vérifier si l'environnement virtuel existe
if [ ! -d ".venv" ]; then
    echo "🔄 Création de l'environnement virtuel..."
    python3 -m venv .venv
fi

# Activer l'environnement virtuel
source .venv/bin/activate

# Installer les dépendances si nécessaire
if [ ! -f ".venv/installed" ]; then
    echo "🔄 Installation des dépendances..."
    pip install -r requirements.txt > /dev/null 2>&1
    touch .venv/installed
    echo "✅ Dépendances installées"
fi

# Créer la configuration si elle n'existe pas
if [ ! -f ".env" ]; then
    echo "🔄 Configuration automatique..."
    cat > .env << EOF
SECRET_KEY=$(openssl rand -base64 32)
FLASK_ENV=development
PORT=5000
HOST=0.0.0.0
DEBUG=true
EOF
    echo "✅ Configuration créée"
fi

# Trouver un port libre
PORT=5000
while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; do
    PORT=$((PORT + 1))
done

echo ""
echo "🚀 LANCEMENT DE LA DÉMO"
echo "========================"
echo ""
echo "🌐 Application disponible sur : http://localhost:$PORT"
echo ""
echo "🎮 POUR TESTER EN MODE DÉMO :"
echo "   📍 IP du routeur : 192.168.1.100"
echo "   👤 Utilisateur   : demo"
echo "   🔑 Mot de passe  : demo"
echo ""
echo "🛑 Appuyez sur Ctrl+C pour arrêter"
echo ""
echo "▶️  Démarrage en cours..."

# Démarrer l'application
python run.py --env development --port $PORT
