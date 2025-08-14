#!/bin/bash
# 🚀 Script de déploiement automatique Render
# ID Serveur: srv-d2enims9c44c73960iag

echo "🎯 Déploiement automatique WiFi Manager sur Render..."
echo "� Serveur ID: srv-d2enims9c44c73960iag"
echo "⏰ $(date)"

# Vérifications pré-déploiement
echo "🔍 Vérification des fichiers critiques..."

if [ ! -f "Procfile" ]; then
    echo "❌ Procfile manquant!"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt manquant!"
    exit 1
fi

if [ ! -f "wsgi.py" ]; then
    echo "❌ wsgi.py manquant!"
    exit 1
fi

echo "✅ Tous les fichiers critiques présents"

# Test de l'application WSGI
echo "🧪 Test du module WSGI..."
python -c "from wsgi import application; print('✅ WSGI OK')" || {
    echo "❌ Erreur WSGI!"
    exit 1
}

# Vérification des dépendances
echo "📦 Vérification des dépendances..."
pip install -q -r requirements.txt || {
    echo "❌ Erreur installation dépendances!"
    exit 1
}

echo "✅ Dépendances installées"

# Push final vers GitHub (requis pour Render)
echo "📤 Push final vers GitHub..."
git add -A
git commit -m "🚀 Auto-deploy to Render srv-d2enims9c44c73960iag - $(date)"
git push origin main

echo ""
echo "🎉 DÉPLOIEMENT PRÊT!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "� Serveur Render: srv-d2enims9c44c73960iag"
echo "� GitHub: https://github.com/franklin-mireb/Wifi-"
echo "⚙️  Configuration: render.yaml + Procfile"
echo "🎯 Status: Prêt pour déploiement automatique"
echo ""
echo "🚀 PROCHAINES ÉTAPES:"
echo "1. Connectez votre repo GitHub à Render"
echo "2. Render détectera automatiquement render.yaml"
echo "3. Le déploiement démarrera avec Procfile corrigé"
echo ""
echo "� Ou utilisez l'API Render directement:"
echo "   curl -X POST https://api.render.com/v1/services/srv-d2enims9c44c73960iag/deploys"
echo ""
echo "😴 Reposez-vous, le déploiement est configuré!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
