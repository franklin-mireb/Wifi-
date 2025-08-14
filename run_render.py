#!/usr/bin/env python3
"""
Point d'entrée simple pour Render
"""
import os
from app import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
