#!/usr/bin/env python3
"""
Configuration WSGI pour Render avec Gunicorn
"""
import os
from app import app

# Configuration pour Render
if __name__ != "__main__":
    # Mode WSGI (gunicorn)
    application = app
else:
    # Mode direct (python wsgi.py)
    port = int(os.environ.get('PORT', 10000))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=False)
