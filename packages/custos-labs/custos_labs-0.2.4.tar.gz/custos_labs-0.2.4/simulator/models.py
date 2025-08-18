# simulator/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q 

User = get_user_model()


class SimulationRun(models.Model):
    """
    A single live/continuous simulation session for a user (and optionally tied to a specific API key).

    Status lifecycle:
      active  -> normal streaming
      warning -> streaming but below threshold
      paused  -> user/tab inactivity or manual pause
      misaligned -> hard stop due to violation
      ended   -> completed/terminated
    """
    STATUS_CHOICES = [
        ("active", "Active"),
        ("warning", "Warning"),
        ("misaligned", "Misaligned"),
        ("paused", "Paused"),
        ("ended", "Ended"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="simulation_runs")
    api_key = models.ForeignKey(
        "api.APIKey",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="simulation_runs",
    )

    alignment_score = models.FloatField(null=True, blank=True, default=1.0)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="active", db_index=True)

    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    last_heartbeat = models.DateTimeField(null=True, blank=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Most queries look up “current run” and recent runs:
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["user", "status", "started_at"]),
            models.Index(fields=["api_key", "status", "started_at"]),
            models.Index(fields=["last_heartbeat"]),
            models.Index(fields=["updated_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "api_key"],
                condition=Q(status__in=["active", "warning", "paused"]),
                name="unique_open_run_per_user_key",
            )
        ]

    @property
    def is_open(self) -> bool:
        """Convenience flag: True if the run is not ended/misaligned."""
        return self.status in {"active", "warning", "paused"}

    def __str__(self) -> str:
        return f"Run {self.id} ({self.status})"


class SimulatorLog(models.Model):
    """
    A single 'beat' of telemetry for a SimulationRun.
    """
    run = models.ForeignKey(SimulationRun, on_delete=models.CASCADE, related_name="logs")
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    response = models.TextField(blank=True, default="")
    prompt = models.TextField(blank=True, default="")

    alignment_score = models.FloatField()
    color = models.CharField(max_length=8)          # "green" | "yellow" | "red"
    flatline = models.BooleanField(default=False)   # True if violation / hard stop
    violations = models.JSONField(default=list)     # e.g., ["misalignment"] or policy slugs
    confidence = models.FloatField(default=1.0)

    class Meta:
        ordering = ["timestamp"]
        indexes = [
            models.Index(fields=["run", "timestamp"]),
        ]

    def __str__(self) -> str:
        return f"Log {self.id} [{self.color}] for Run {self.run_id}"
