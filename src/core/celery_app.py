import os
import sys
from celery import Celery

# -------------------------------------------------
# PATH FIX (CRITICAL)
# -------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.append(SRC_ROOT)

# -------------------------------------------------
# CONFIG IMPORT (FIXED)
# -------------------------------------------------
from core.config import settings  # ✅ NOW THIS WORKS

# -------------------------------------------------
# CELERY APP
# -------------------------------------------------
celery_app = Celery(
    "pyautomate",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
