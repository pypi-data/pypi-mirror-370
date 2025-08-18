## custos/app.py

from __future__ import annotations
from django.apps import AppConfig
from .bootstrap import custos_bootstrap

class CustosConfigDjango(AppConfig):
    name = "custos"
    verbose_name = "Custos Labs (Alignment & HRV)"

    def ready(self):
        # Start HRV at Django startup; never block the app on errors
        try:
            custos_bootstrap()
        except Exception:
            pass
