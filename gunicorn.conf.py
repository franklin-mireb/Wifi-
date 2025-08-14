# Configuration Gunicorn pour production Cloud (Render/Heroku)
import multiprocessing
import os

# Liaison réseau (Render utilise $PORT)
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"

# Workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000

# Timeouts
timeout = 30
keepalive = 30
graceful_timeout = 30

# Performance
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Logging (logs vers stdout/stderr pour Render)
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "wifi-manager"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# SSL (si utilisé directement)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
