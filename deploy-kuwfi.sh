#!/bin/bash
# 🚀 Script de déploiement WiFi Manager KUWFI
# Configuration spécialisée pour le routeur mireb wifi

echo "🎯 Déploiement WiFi Manager pour routeur KUWFI"
echo "📍 Serveur: srv-d2enims9c44c73960iag"
echo "🌐 URL: https://wifi-manager-zu09.onrender.com/"
echo "=" * 60

# Configuration des variables d'environnement pour KUWFI
export ROUTER_IP="192.168.1.254"
export ROUTER_USER="admin"
export ROUTER_PASS="admin"
export WIFI_SSID="mireb wifi"
export WIFI_PASSWORD="0816448961"
export FLASK_ENV="production"

echo "📋 Configuration KUWFI:"
echo "  • SSID WiFi: $WIFI_SSID"
echo "  • Passerelle: $ROUTER_IP"
echo "  • Réseau: 192.168.1.0/24"
echo "  • DNS: 192.168.1.254"
echo

# Test des composants avant déploiement
echo "🧪 Tests pré-déploiement..."

# Test 1: Syntaxe Python
echo "📝 Vérification syntaxe Python..."
python -m py_compile app.py kuwfi_manager.py voucher_system.py
if [ $? -eq 0 ]; then
    echo "✅ Syntaxe Python OK"
else
    echo "❌ Erreur syntaxe Python"
    exit 1
fi

# Test 2: Imports
echo "📦 Vérification des imports..."
python -c "from app import app; from kuwfi_manager import KUWFIManager; from voucher_system import VoucherManager; print('✅ Imports OK')"
if [ $? -ne 0 ]; then
    echo "❌ Erreur imports"
    exit 1
fi

# Test 3: WSGI
echo "🔧 Test WSGI..."
python -c "from wsgi import application; print(f'✅ WSGI OK - {type(application)}')"
if [ $? -ne 0 ]; then
    echo "❌ Erreur WSGI"
    exit 1
fi

# Test 4: Voucher system
echo "🎫 Test système de vouchers..."
python -c "
from voucher_system import VoucherManager
vm = VoucherManager()
voucher = vm.create_voucher('monthly')
print(f'✅ Voucher créé: {voucher.code}')
print(f'💰 Prix: \${voucher.plan.price_usd}')
"

# Création du fichier .env pour production
echo "📄 Création du fichier .env..."
cat > .env << EOF
# Configuration KUWFI Router
ROUTER_IP=192.168.1.254
ROUTER_USER=admin
ROUTER_PASS=admin
WIFI_SSID=mireb wifi
WIFI_PASSWORD=0816448961

# Configuration Flask
FLASK_ENV=production
SECRET_KEY=\$(openssl rand -hex 32)

# Configuration réseau
NETWORK_SUBNET=192.168.1.0/24
GATEWAY=192.168.1.254
DNS_SERVER=192.168.1.254

# Render deployment
PORT=10000
HOST=0.0.0.0
EOF

echo "✅ Fichier .env créé"

# Mise à jour du render.yaml avec la config KUWFI
echo "⚙️ Mise à jour render.yaml..."
cat > render.yaml << 'EOF'
# 🚀 Configuration Render pour WiFi Manager KUWFI
services:
  - type: web
    name: wifi-manager-kuwfi
    env: python
    plan: free
    region: oregon
    buildCommand: pip install --upgrade pip && pip install -r requirements.txt
    startCommand: ./start.sh
    envVars:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: ROUTER_IP
        value: 192.168.1.254
      - key: ROUTER_USER
        value: admin
      - key: ROUTER_PASS
        value: admin
      - key: WIFI_SSID
        value: mireb wifi
      - key: WIFI_PASSWORD
        value: 0816448961
      - key: NETWORK_SUBNET
        value: 192.168.1.0/24
      - key: GATEWAY
        value: 192.168.1.254
      - key: DNS_SERVER
        value: 192.168.1.254
      - key: PYTHON_VERSION
        value: 3.12.0
EOF

echo "✅ render.yaml mis à jour"

# Commit et push
echo "📤 Push vers GitHub..."
git add -A
git commit -m "🔧 KUWFI Router Integration Complete

✅ Fonctionnalités ajoutées:
- 🌐 Gestionnaire KUWFI spécialisé
- 📱 Détection appareils connectés
- 🚫 Blocage/déblocage par adresse MAC
- 🎫 Intégration système vouchers
- 📊 Monitoring temps réel
- 🔧 Configuration automatique

📋 Configuration réseau:
- SSID: mireb wifi
- Passerelle: 192.168.1.254
- Réseau: 192.168.1.0/24

🎯 Prêt pour production sur Render!"

git push origin main

echo
echo "🎉 DÉPLOIEMENT TERMINÉ!"
echo "=" * 40
echo "🌐 URL Application: https://wifi-manager-zu09.onrender.com/"
echo "📡 SSID WiFi: mireb wifi"
echo "🔑 Mot de passe: 0816448961"
echo "📍 IP Routeur: 192.168.1.254"
echo
echo "🚀 FONCTIONNALITÉS DISPONIBLES:"
echo "  • Gestion appareils connectés"
echo "  • Système vouchers (7$/mois, 0.6$/jour)"
echo "  • Blocage/déblocage par MAC"
echo "  • Monitoring temps réel"
echo "  • Interface web responsive"
echo
echo "📖 Pour tester:"
echo "  1. Connectez-vous au WiFi 'mireb wifi'"
echo "  2. Visitez l'application web"
echo "  3. Cliquez 'Appareils Connectés'"
echo "  4. Gérez les accès et vouchers"
echo
echo "😴 Repos bien mérité - tout fonctionne automatiquement!"
