# gunicorn.conf.py
# -------------------------------------------------
# Gunicorn configuration for Flask backend
# -------------------------------------------------

# Number of worker processes to handle requests concurrently
workers = 4

# Bind Gunicorn to all network interfaces on port 5000
bind = "0.0.0.0:5000"

# Log all access (requests) to stdout
accesslog = "-"

# Log all errors to stdout
errorlog = "-"

# Timeout in seconds before a worker is restarted
timeout = 120

# Optional: preload the app code before forking workers
preload_app = True

# Optional: use 'sync' workers (default); you can use 'gevent' for async workloads
worker_class = "sync"

# Optional: limit request line size (for security)
limit_request_line = 4094

# Optional: display worker startup messages
print_config = True
