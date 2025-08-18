# simulator/admin.py

from django.contrib import admin
from .models import SimulationRun, SimulatorLog

@admin.register(SimulationRun)
class SimulationRunAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'alignment_score', 'started_at', 'ended_at']

@admin.register(SimulatorLog)
class SimulatorLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'run', 'timestamp', 'alignment_score', 'color', 'flatline']
