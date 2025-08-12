# Configuration Gunicorn pour production LWS
import multiprocessing

# Liaison réseau
bind = "127.0.0.1:5000"

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

# Logging
accesslog = "/home/wifimanager/logs/access.log"
errorlog = "/home/wifimanager/logs/error.log"
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
