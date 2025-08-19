import logging
import os
import sys
from logging.handlers import RotatingFileHandler

try:
    from flask import current_app, has_request_context, request
except ImportError:
    current_app = None
    def has_request_context(): return False
    request = None


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = getattr(request, "url", None)
            record.remote_addr = getattr(request, "remote_addr", None)
            record.method = getattr(request, "method", None)
        else:
            record.url = None
            record.remote_addr = None
            record.method = None
        return super().format(record)


LOG_FORMAT = (
    "[%(asctime)s] %(levelname)s in %(module)s [%(process)d]: %(message)s"
    " | url=%(url)s remote_addr=%(remote_addr)s method=%(method)s"
)


def get_logger(name="app", config=None):
    logger = logging.getLogger(name)

    # Bersihkan handler sebelumnya jika ada
    if logger.hasHandlers():
        logger.handlers.clear()

    # Ambil konfigurasi dari Flask config atau fallback ke environment variable
    if config is None:
        try:
            config = current_app.config
        except Exception:
            config = {}

    LOG_LEVEL = str(config.get("LOG_LEVEL", os.getenv("LOG_LEVEL", "INFO"))).upper()
    LOG_DIR = config.get("LOG_DIR", os.getenv("LOG_DIR", "logs"))
    LOG_FILE = config.get("LOG_FILE", os.getenv("LOG_FILE", "app.log"))
    LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)
    LOG_MAX_BYTES = int(config.get("LOG_MAX_BYTES", os.getenv("LOG_MAX_BYTES", 10 * 1024 * 1024)))
    LOG_BACKUP_COUNT = int(config.get("LOG_BACKUP_COUNT", os.getenv("LOG_BACKUP_COUNT", 5)))

    os.makedirs(LOG_DIR, exist_ok=True)

    formatter = RequestFormatter(LOG_FORMAT)

    # File log handler (jika bisa)
    try:
        file_handler = RotatingFileHandler(
            LOG_PATH, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding="utf-8"
        )
        file_handler.setLevel(LOG_LEVEL)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"[LOGGER INIT] Could not add file handler: {e}")

    # Console stream handler yang aman
    try:
        console_handler = logging.StreamHandler(sys.__stdout__)  # lebih aman daripada sys.stdout.buffer
        console_handler.setLevel(LOG_LEVEL)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    except Exception as e:
        print(f"[LOGGER INIT] Could not add console handler: {e}")

    logger.setLevel(LOG_LEVEL)
    logger.propagate = False

    return logger
