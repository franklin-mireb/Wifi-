#!/bin/bash

# 🚀 Script de déploiement Render automatique

echo "🌐 Préparation du déploiement Render..."

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "app.py" ]; then
    echo "❌ Erreur: app.py non trouvé. Assurez-vous d'être dans le répertoire Wifi-"
    exit 1
fi

# Créer/mettre à jour requirements.txt
echo "📦 Mise à jour des dépendances..."
pip freeze > requirements.txt

# Vérifier les fichiers requis pour Render
echo "🔍 Vérification des fichiers Render..."

if [ ! -f "render.yaml" ]; then
    echo "❌ render.yaml manquant"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt manquant"
    exit 1
fi

# Ajouter un Procfile pour compatibilité
echo "📝 Création du Procfile..."
echo "web: python run.py --env production --host 0.0.0.0 --port \$PORT" > Procfile

# Mettre à jour run.py pour Render
echo "🔧 Optimisation pour Render..."
cat > run_render.py << 'EOF'
#!/usr/bin/env python3
"""
Point d'entrée optimisé pour Render
"""
import os
import sys

# Configuration pour Render
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('HOST', '0.0.0.0')
os.environ.setdefault('PORT', '10000')

# Importer l'application
from app import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"🚀 Starting WiFi Manager on {host}:{port}")
    print(f"🔧 Environment: {os.environ.get('FLASK_ENV', 'development')}")
    
    app.run(
        host=host,
        port=port,
        debug=debug
    )
EOF

# Commit et push vers GitHub
echo "📤 Push vers GitHub..."
git add .
git commit -m "🌐 Configuration Render - Déploiement automatique

✨ Ajouts pour Render:
- 📋 render.yaml - Configuration Render complète
- 📚 DEPLOYMENT_RENDER.md - Guide déploiement
- 📦 requirements.txt mis à jour
- 🚀 Procfile pour démarrage
- 🔧 run_render.py optimisé

🎯 Prêt pour déploiement 1-click sur Render!"

git push origin main

echo ""
echo "✅ Préparation terminée!"
echo ""
echo "🎯 PROCHAINES ÉTAPES:"
echo "1. 🌐 Aller sur: https://render.com/"
echo "2. 📦 Connecter GitHub et sélectionner: franklin-mireb/Wifi-"
echo "3. ⚙️ Render détectera automatiquement render.yaml"
echo "4. 🚀 Cliquer 'Create Web Service'"
echo ""
echo "📍 Ou utiliser le deploy button:"
echo "👉 https://render.com/deploy?repo=https://github.com/franklin-mireb/Wifi-"
echo ""
echo "🎉 Votre WiFi Manager sera en ligne en 2-3 minutes!"
