#!/usr/bin/env python3
"""
Fichier WSGI pour le déploiement sur LWS
Ce fichier est requis par l'hébergement LWS pour les applications Python
"""

import sys
import os

# Ajouter le répertoire de l'application au path Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configuration pour l'environnement LWS
os.environ.setdefault('FLASK_ENV', 'production')

# Import de l'application Flask
from app import app as application

# Configuration spécifique pour LWS
application.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'lws-production-key-change-this'),
    DEBUG=False,
    HOST='0.0.0.0',
    PORT=int(os.environ.get('PORT', 5000))
)

if __name__ == "__main__":
    application.run(
        host=application.config.get('HOST', '0.0.0.0'),
        port=application.config.get('PORT', 5000),
        debug=application.config.get('DEBUG', False)
    )
