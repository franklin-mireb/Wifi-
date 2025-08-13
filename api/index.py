#!/usr/bin/env python3
"""
Point d'entrée pour Vercel
"""
import os
import sys

# Ajouter le répertoire racine au path Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importer l'application Flask
from app import app

# Pour Vercel, l'application doit être accessible via la variable 'app'
if __name__ == "__main__":
    app.run(debug=False)
