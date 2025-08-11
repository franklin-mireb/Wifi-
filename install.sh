#!/bin/bash

echo "🚀 Installation du Gestionnaire WiFi..."

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Créer un environnement virtuel
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances
echo "📚 Installation des dépendances..."
pip install -r requirements.txt

echo "✅ Installation terminée !"
echo ""
echo "Pour lancer l'application :"
echo "1. Activez l'environnement virtuel : source venv/bin/activate"
echo "2. Lancez l'application : python app.py"
echo "3. Ouvrez votre navigateur sur : http://localhost:5000"
echo ""
echo "🌐 L'application sera accessible depuis votre réseau local sur : http://[votre-ip]:5000"
