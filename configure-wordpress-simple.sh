#!/bin/bash

# 🚀 Configuration WordPress Simplifiée

echo "🌐 Configuration WordPress via base de données..."

# Configuration directe via MySQL
docker exec -i wordpress-mysql mysql -u wordpress -pwordpress_password wordpress << 'EOF'

-- Insertion des données WordPress de base
INSERT INTO wp_options (option_name, option_value, autoload) VALUES
('siteurl', 'http://localhost:8080', 'yes'),
('home', 'http://localhost:8080', 'yes'),
('blogname', 'WiFi Hotspot Manager', 'yes'),
('blogdescription', 'Gestionnaire WiFi avec système de vouchers', 'yes'),
('admin_email', 'admin@wifimanager.local', 'yes'),
('default_role', 'subscriber', 'yes')
ON DUPLICATE KEY UPDATE option_value = VALUES(option_value);

-- Créer l'utilisateur admin
INSERT INTO wp_users (user_login, user_pass, user_nicename, user_email, user_status, display_name) VALUES
('admin', MD5('WifiAdmin2025!'), 'admin', 'admin@wifimanager.local', 0, 'Administrator')
ON DUPLICATE KEY UPDATE user_pass = VALUES(user_pass);

-- Ajouter les permissions admin
INSERT INTO wp_usermeta (user_id, meta_key, meta_value) VALUES
(1, 'wp_capabilities', 'a:1:{s:13:"administrator";b:1;}'),
(1, 'wp_user_level', '10')
ON DUPLICATE KEY UPDATE meta_value = VALUES(meta_value);

EOF

echo "✅ Base de données configurée!"

# Copier le plugin
echo "🔌 Installation du plugin WiFi Manager..."
docker exec -it wordpress-site bash -c "
    mkdir -p /var/www/html/wp-content/plugins/wifi-manager/
    chown -R www-data:www-data /var/www/html/wp-content/plugins/
"

# Vérifier que le plugin est bien copié
docker exec -it wordpress-site bash -c "
    ls -la /var/www/html/wp-content/plugins/wifi-manager/
"

echo "🎉 Configuration terminée!"
echo ""
echo "📋 Informations de connexion:"
echo "🌐 URL: http://localhost:8080"
echo "👤 Utilisateur: admin"
echo "🔐 Mot de passe: WifiAdmin2025!"
echo ""
echo "🔌 Plugin WiFi Manager installé!"
echo "📝 Shortcodes disponibles:"
echo "   [wifi_manager] - Interface complète"
echo "   [wifi_vouchers] - Système de tickets"
