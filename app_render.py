#!/usr/bin/env python3
"""
Point d'entrée simple et robuste pour Render
"""
import os

# Configuration Render
port = int(os.environ.get('PORT', 10000))
host = os.environ.get('HOST', '0.0.0.0')

# Import et démarrage
from app import app

if __name__ == "__main__":
    print(f"🚀 WiFi Manager starting on {host}:{port}")
    app.run(host=host, port=port, debug=False)
