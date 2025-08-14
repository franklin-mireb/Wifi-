# Configuration pour différents environnements

import os

class Config:
    """Configuration de base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = 5000
    
    # Configuration routeur KUWFI
    ROUTER_IP = os.environ.get('ROUTER_IP', '192.168.1.254')  # Passerelle détectée
    ROUTER_USER = os.environ.get('ROUTER_USER', 'admin')
    ROUTER_PASS = os.environ.get('ROUTER_PASS', 'admin')
    WIFI_SSID = os.environ.get('WIFI_SSID', 'mireb wifi')
    WIFI_PASSWORD = os.environ.get('WIFI_PASSWORD', '0816448961')
    
    # Réseau détecté
    NETWORK_SUBNET = '192.168.1.0/24'
    GATEWAY = '192.168.1.254'
    DNS_SERVER = '192.168.1.254'

class DevelopmentConfig(Config):
    """Configuration pour le développement"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Configuration pour la production"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'production-secret-key-must-be-set'
    
class TestingConfig(Config):
    """Configuration pour les tests"""
    TESTING = True
    DEBUG = True

# Dictionnaire des configurations
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
