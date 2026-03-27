import logging
import os
import sys

from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        auto_start = bool(getattr(settings, "ENGAGEMENT_MONITOR_AUTOSTART", True))
        if not auto_start:
            return

        command = sys.argv[1] if len(sys.argv) > 1 else ""
        if command != "runserver":
            return

        # Django autoreload starts two processes; run monitor only in the serving process.
        if os.environ.get("RUN_MAIN") != "true" and "--noreload" not in sys.argv:
            return

        try:
            from api.services.engagement_monitor_service import start_engagement_monitor_background
        except Exception:
            logger.exception("[ENGAGEMENT_MONITOR] Failed to import monitor service")
            return

        started = start_engagement_monitor_background()
        if started:
            logger.info("[ENGAGEMENT_MONITOR] Background monitor thread started")
