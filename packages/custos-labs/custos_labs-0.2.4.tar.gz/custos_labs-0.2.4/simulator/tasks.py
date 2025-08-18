# simulator/tasks.py
from __future__ import annotations

import logging
import random
from typing import Dict, Any

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from .models import SimulationRun
from .realtime import push_real_beat, push_system

logger = logging.getLogger(__name__)


def _demo_payload() -> Dict[str, Any]:
    """
    Generate a synthetic beat for demo/preview purposes.
    Alignment ≈ N(0.82, 0.08) clamped to [0, 1].
    """
    val = max(0.0, min(1.0, random.gauss(0.82, 0.08)))
    return {
        "timestamp": timezone.now().isoformat(),
        "alignment_score": round(val, 3),
        "color": "green" if val >= 0.85 else ("yellow" if val >= 0.70 else "red"),
        "flatline": val < 0.40,
        "violations": [] if val >= 0.40 else ["low_alignment"],
        "confidence": round(random.uniform(0.60, 0.98), 3),
    }


@shared_task
def monitor_alignment(sim_id: int) -> None:
    """
    Placeholder for future automated monitoring per run.
    """
    try:
        sim = SimulationRun.objects.get(id=sim_id)
    except SimulationRun.DoesNotExist:
        logger.warning("monitor_alignment: SimulationRun %s not found", sim_id)
        return
    logger.info("Monitor running for Simulation %s: status=%s", sim_id, sim.status)


@shared_task
def send_demo_beat(run_id: int) -> None:
    """
    Push a synthetic beat to all WS clients for a run.
    Useful for manual testing or demo scenarios.
    """
    payload = _demo_payload()
    try:
        push_real_beat(run_id, payload)
    except Exception as e:
        logger.warning("send_demo_beat: push failed for run %s: %s", run_id, e)


@shared_task
def watchdog_sweep() -> None:
    """
    Periodic watchdog:
      - Pause runs with no heartbeat for PAUSE_AFTER seconds
      - End  runs with no heartbeat for END_AFTER   seconds

    Tunables (Django settings / env):
      SIM_WATCHDOG_PAUSE_AFTER_SEC  (default 180)
      SIM_WATCHDOG_END_AFTER_SEC    (default 7200)
    """
    now = timezone.now()
    pause_after = int(getattr(settings, "SIM_WATCHDOG_PAUSE_AFTER_SEC", 180))
    end_after = int(getattr(settings, "SIM_WATCHDOG_END_AFTER_SEC", 7200))

    qs = SimulationRun.objects.filter(status__in=["active", "warning", "paused"]).only(
        "id", "status", "started_at", "last_heartbeat"
    )

    for run in qs.iterator():
        last = run.last_heartbeat or run.started_at
        delta = (now - last).total_seconds()

        try:
            if delta >= end_after and run.status != "ended":
                run.status = "ended"
                run.ended_at = now
                run.save(update_fields=["status", "ended_at", "updated_at"])
                try:
                    push_system(run.id, "ended")
                except Exception as e:
                    logger.warning("watchdog_sweep: push_system(ended) failed run %s: %s", run.id, e)

            elif delta >= pause_after and run.status not in ("paused", "ended"):
                run.status = "paused"
                run.save(update_fields=["status", "updated_at"])
                try:
                    push_system(run.id, "paused")
                except Exception as e:
                    logger.warning("watchdog_sweep: push_system(paused) failed run %s: %s", run.id, e)

        except Exception as e:
            logger.exception("watchdog_sweep: error processing run %s: %s", run.id, e)
