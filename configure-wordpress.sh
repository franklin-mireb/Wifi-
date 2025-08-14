#!/bin/bash

# 🚀 Script de configuration WordPress automatique

echo "🌐 Configuration automatique de WordPress..."

# Attendre que WordPress soit prêt
sleep 20

# Configuration automatique via WP-CLI
docker exec -it wordpress-site bash -c "
    # Installer WP-CLI
    curl -O https://raw.githubusercontent.com/wp-cli/wp-cli/main/utils/wp-completion.bash
    curl -L https://github.com/wp-cli/wp-cli/releases/latest/download/wp-cli.phar -o wp-cli.phar
    chmod +x wp-cli.phar
    mv wp-cli.phar /usr/local/bin/wp
    
    # Configuration WordPress
    cd /var/www/html
    
    # Installation automatique
    wp core install \
        --url='http://localhost:8080' \
        --title='WiFi Hotspot Manager' \
        --admin_user='admin' \
        --admin_password='WifiAdmin2025!' \
        --admin_email='admin@wifimanager.local' \
        --allow-root
    
    # Activer le plugin WiFi Manager
    wp plugin activate wifi-manager --allow-root
    
    # Créer une page pour le système WiFi
    wp post create \
        --post_type=page \
        --post_title='Gestion WiFi' \
        --post_content='[wifi_manager]' \
        --post_status=publish \
        --allow-root
    
    # Créer une page pour les vouchers
    wp post create \
        --post_type=page \
        --post_title='Acheter Accès WiFi' \
        --post_content='[wifi_vouchers]' \
        --post_status=publish \
        --allow-root
    
    echo '✅ WordPress configuré automatiquement!'
"

echo "🎉 Configuration terminée!"
echo "🌐 WordPress: http://localhost:8080"
echo "👤 Admin: admin / WifiAdmin2025!"
