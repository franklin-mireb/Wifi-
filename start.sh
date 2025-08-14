#!/bin/bash
# Script de démarrage explicite pour Render
echo "🚀 Starting WiFi Manager on Render..."
echo "📍 PORT: $PORT"
echo "🔧 PYTHON_VERSION: $(python --version)"

# Démarrage avec gunicorn
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 wsgi:application
