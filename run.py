#!/usr/bin/env python3

"""
Script de démarrage pour le Gestionnaire WiFi
Permet de lancer l'application dans différents environnements
"""

import os
import sys
import argparse
from app import app
from config import config

def main():
    parser = argparse.ArgumentParser(description='Gestionnaire WiFi - Script de démarrage')
    parser.add_argument('--env', 
                       choices=['development', 'production', 'testing'],
                       default='development',
                       help='Environnement d\'exécution (default: development)')
    parser.add_argument('--host', 
                       default='0.0.0.0',
                       help='Adresse d\'écoute (default: 0.0.0.0)')
    parser.add_argument('--port', 
                       type=int,
                       default=5000,
                       help='Port d\'écoute (default: 5000)')
    parser.add_argument('--debug',
                       action='store_true',
                       help='Activer le mode debug')
    
    args = parser.parse_args()
    
    # Configuration de l'environnement
    config_class = config.get(args.env, config['default'])
    app.config.from_object(config_class)
    
    # Override des paramètres via les arguments
    if args.debug:
        app.config['DEBUG'] = True
    
    print(f"🚀 Démarrage du Gestionnaire WiFi")
    print(f"📍 Environnement: {args.env}")
    print(f"🌐 Adresse: http://{args.host}:{args.port}")
    print(f"🔧 Debug: {'Activé' if app.config.get('DEBUG', False) else 'Désactivé'}")
    print("━" * 50)
    
    if args.env == 'production':
        print("⚠️  ATTENTION: Mode production détecté")
        print("   Assurez-vous que SECRET_KEY est définie")
        print("   Utilisez un serveur WSGI en production")
        print("━" * 50)
    
    try:
        app.run(host=args.host, port=args.port, debug=app.config.get('DEBUG', False))
    except KeyboardInterrupt:
        print("\n👋 Arrêt du serveur...")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
