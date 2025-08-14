#!/bin/bash
# Script de monitoring Render
echo "🔍 Vérification du déploiement Render..."

# Attendre un peu pour que Render redéploie
sleep 30

# URL de test (remplace par ton URL Render réelle)
RENDER_URL="https://wifi-[your-service-name].onrender.com"

echo "📡 Test de connectivité vers $RENDER_URL"

# Test de base
response=$(curl -s -o /dev/null -w "%{http_code}" "$RENDER_URL" || echo "000")

if [ "$response" = "200" ]; then
    echo "✅ Application Render accessible (HTTP 200)"
    echo "🎯 Test du système de vouchers..."
    
    # Test API voucher
    voucher_response=$(curl -s "$RENDER_URL/api/vouchers" | head -5)
    echo "📋 Réponse API vouchers:"
    echo "$voucher_response"
    
    echo ""
    echo "🚀 Déploiement Render RÉUSSI !"
    echo "🌐 Accès: $RENDER_URL"
    
elif [ "$response" = "000" ]; then
    echo "❌ Erreur de connectivité - Service non accessible"
else
    echo "⚠️  Response HTTP: $response"
    echo "🔧 Le service redémarre peut-être encore..."
fi

echo ""
echo "💡 Conseils de débogage Render:"
echo "1. Vérifier les logs dans le dashboard Render"
echo "2. S'assurer que le service utilise le bon Procfile"
echo "3. Vérifier les variables d'environnement"
echo "4. Confirmer que Python 3.12 est supporté"
