#!/usr/bin/env python3
"""
Point d'entrée optimisé pour Render
"""
import os
import sys

# Ajouter le répertoire actuel au path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuration pour Render
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('HOST', '0.0.0.0')
os.environ.setdefault('PORT', '10000')

try:
    # Importer l'application
    from app import app
    
    if __name__ == "__main__":
        port = int(os.environ.get('PORT', 10000))
        host = os.environ.get('HOST', '0.0.0.0')
        debug = os.environ.get('FLASK_ENV') != 'production'
        
        print(f"🚀 Starting WiFi Manager on {host}:{port}")
        print(f"🔧 Environment: {os.environ.get('FLASK_ENV', 'development')}")
        print(f"🐍 Python version: {sys.version}")
        print(f"📁 Working directory: {os.getcwd()}")
        print(f"📋 Python path: {sys.path}")
        
        app.run(
            host=host,
            port=port,
            debug=debug
        )
        
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"📋 Files available: {os.listdir('.')}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting application: {e}")
    sys.exit(1)
