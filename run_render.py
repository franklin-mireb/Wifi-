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
