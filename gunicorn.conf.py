"""Gunicorn configuration.

See: https://docs.gunicorn.org/en/stable/settings.html
"""

import multiprocessing
import os

# Server Socket
bind = f"0.0.0.0:{os.getenv('APP_INTERNAL_PORT', '8000')}"

reload = os.getenv("ENVIRONMENT", "development") == "development"

# Worker Processes
workers = int(os.getenv("WORKERS_COUNT", min(multiprocessing.cpu_count() * 2 + 1, 8)))
threads = int(os.getenv("THREADS_PER_WORKER", "1"))
worker_class = "uvicorn.workers.UvicornWorker"
timeout = int(os.getenv("WORKER_TIMEOUT", "600"))
graceful_timeout = int(os.getenv("GRACEFUL_TIMEOUT", "60"))

# Logging
loglevel = os.getenv("LOG_LEVEL", "info").lower()
accesslog = "-"
