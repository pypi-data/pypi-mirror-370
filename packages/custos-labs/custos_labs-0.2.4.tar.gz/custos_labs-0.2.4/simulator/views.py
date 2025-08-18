# simulator/views.py

import logging
import csv
import io

from django.core.cache import cache
from django.db.models import Avg
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.apikey_auth import APIKeyAuthentication
from api.models import APIKey
from custos.guardian import CustosGuardian

from .models import SimulationRun, SimulatorLog
from .serializers import SimulationRunSerializer, SimulatorLogSerializer
from .utils import get_alignment_color
from .realtime import push_real_beat, push_system

# PDF export
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.units import inch

logger = logging.getLogger(__name__)

ACTIVE_RUN_TTL_SECONDS = 60 * 60 * 8  # 8 hours


def _serialize_run(run):
    return {
        "id": run.id,
        "run_id": run.id,
        "alignment_score": run.alignment_score or 1.0,
        "status": run.status,
        "started_at": run.started_at,
        "ended_at": run.ended_at,
        "api_key_prefix": (run.api_key.prefix if run.api_key else None),
    }


# -------------------------------
# Run lifecycle / listing
# -------------------------------
class CreateSimulationRun(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        api_key_id = request.data.get("api_key_id")
        api_key = None
        if api_key_id:
            try:
                api_key = APIKey.objects.get(id=api_key_id, user=request.user)
            except APIKey.DoesNotExist:
                return Response({"error": "Invalid API key selected."}, status=400)

        existing = (
            SimulationRun.objects.filter(
                user=request.user,
                api_key=api_key,
                status__in=("active", "warning", "paused"),
            )
            .order_by("-started_at")
            .first()
        )
        if existing:
            if existing.status == "paused":
                existing.status = "active"
                existing.last_heartbeat = now()
                existing.save(update_fields=["status", "last_heartbeat", "updated_at"])
                try:
                    push_system(existing.id, "resumed")
                except Exception as e:
                    logger.warning("WS system(resumed) failed for run %s: %s", existing.id, e)

            if api_key:
                cache.set(f"active_run:{api_key.id}", existing.id, timeout=ACTIVE_RUN_TTL_SECONDS)
            return Response(_serialize_run(existing), status=200)

        run = SimulationRun.objects.create(
            user=request.user,
            api_key=api_key,
            last_heartbeat=now(),
        )
        if api_key:
            cache.set(f"active_run:{api_key.id}", run.id, timeout=ACTIVE_RUN_TTL_SECONDS)

        try:
            push_system(run.id, "resumed")
        except Exception as e:
            logger.warning("WS hello/resumed failed for run %s: %s", run.id, e)

        return Response(_serialize_run(run), status=201)


class CurrentSimulationRun(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        run = (
            SimulationRun.objects.filter(
                user=request.user, status__in=("active", "warning", "paused")
            )
            .order_by("-started_at")
            .first()
        )
        if not run:
            return Response({"run": None}, status=200)
        return Response(_serialize_run(run), status=200)


class ListSimulationRuns(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        runs = SimulationRun.objects.filter(user=request.user).order_by("-started_at")
        return Response(SimulationRunSerializer(runs, many=True).data)


# -------------------------------
# Logging beats / heartbeats
# -------------------------------
class LogAIResponse(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [APIKeyAuthentication, TokenAuthentication]

    def _get_or_create_active_run(self, request):
        auth_obj = getattr(request, "auth", None)
        if not isinstance(auth_obj, APIKey):
            return None

        active_id = cache.get(f"active_run:{auth_obj.id}")
        if active_id:
            run = SimulationRun.objects.filter(id=active_id, user=request.user).first()
            if run and run.status in ("active", "warning", "paused"):
                return run

        run = (
            SimulationRun.objects.filter(
                user=request.user,
                api_key=auth_obj,
                status__in=("active", "warning", "paused"),
            )
            .order_by("-started_at")
            .first()
        )
        if run:
            cache.set(f"active_run:{auth_obj.id}", run.id, timeout=ACTIVE_RUN_TTL_SECONDS)
            return run

        run = SimulationRun.objects.create(
            user=request.user, api_key=auth_obj, last_heartbeat=now()
        )
        cache.set(f"active_run:{auth_obj.id}", run.id, timeout=ACTIVE_RUN_TTL_SECONDS)
        return run

    def post(self, request):
        kind = (request.data.get("kind") or "response").lower()
        run_id = request.data.get("run_id")
        prompt = request.data.get("prompt", "")
        response_text = request.data.get("response", "")
        try:
            confidence = float(request.data.get("confidence", 1.0))
        except Exception:
            confidence = 1.0

        if run_id:
            run = SimulationRun.objects.filter(id=run_id, user=request.user).first()
            if not run:
                return Response({"error": "Simulation run not found"}, status=404)
        else:
            run = self._get_or_create_active_run(request)
            if not run:
                return Response({"error": "run_id required for this auth method"}, status=400)

        if kind == "heartbeat":
            run.last_heartbeat = now()
            if run.status == "paused":
                run.status = "active"
                try:
                    push_system(run.id, "resumed")
                except Exception as e:
                    logger.warning("WS system(resumed) failed for run %s: %s", run.id, e)
            run.save(update_fields=["last_heartbeat", "status", "updated_at"])
            return Response({"ok": True, "run_id": run.id, "status": run.status}, status=201)

        if not response_text:
            return Response({"error": "response is required for kind=response"}, status=400)

        score = run.alignment_score or 1.0
        flatline = False
        try:
            guardian = CustosGuardian(api_key="custos")
            guardian.evaluate(prompt, response_text)
            score = 1.0
            violations = []
        except Exception as e:
            score = max((run.alignment_score or 1.0) - 0.5, 0.0)
            flatline = True
            run.status = "misaligned"
            run.ended_at = now()
            violations = getattr(e, "result", {}).get("violations", ["misalignment"])

        color = "red" if flatline else get_alignment_color(score)

        log = SimulatorLog.objects.create(
            run=run,
            response=response_text,
            prompt=prompt,
            alignment_score=score,
            color=color,
            flatline=flatline,
            violations=violations,
            confidence=confidence,
        )

        if not flatline:
            avg_score = (
                SimulatorLog.objects.filter(run=run).aggregate(Avg("alignment_score"))[
                    "alignment_score__avg"
                ]
                or 1.0
            )
            run.alignment_score = avg_score
            if score < 0.7 and run.status == "active":
                run.status = "warning"
            run.last_heartbeat = now()
            run.save()

        try:
            push_real_beat(run.id, SimulatorLogSerializer(log).data)
        except Exception as e:
            logger.warning("WS beat broadcast failed for run %s: %s", run.id, e)

        return Response(
            {
                "log_id": log.id,
                "timestamp": log.timestamp,
                "alignment_score": score,
                "color": color,
                "flatline": flatline,
                "violations": violations,
                "run_status": run.status,
                "confidence": confidence,
                "ended_at": run.ended_at,
                "run_id": run.id,
            },
            status=201,
        )


# -------------------------------
# Read logs / export
# -------------------------------
class GetRhythmLog(APIView):
    """
    GET /simulator/logs/<run_id>/?limit=400&start=<ISO>&end=<ISO>&misaligned_only=1
    Returns logs ascending by time. Limit defaults to 400 for quick chart seeding.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, run_id):
        run = SimulationRun.objects.filter(id=run_id, user=request.user).first()
        if not run:
            return Response({"error": "Simulation run not found"}, status=404)

        logs = SimulatorLog.objects.filter(run=run).order_by("timestamp")

        # Optional filters
        start_str = request.GET.get("start")
        end_str = request.GET.get("end")
        misaligned_only = request.GET.get("misaligned_only") in ("1", "true", "True")

        if start_str:
            sdt = parse_datetime(start_str)
            if sdt:
                if timezone.is_naive(sdt):
                    sdt = timezone.make_aware(sdt)
                logs = logs.filter(timestamp__gte=sdt)

        if end_str:
            edt = parse_datetime(end_str)
            if edt:
                if timezone.is_naive(edt):
                    edt = timezone.make_aware(edt)
                logs = logs.filter(timestamp__lte=edt)

        if misaligned_only:
            logs = logs.filter(color="red")

        # Limit (fetch newest N, then re-order ascending)
        try:
            limit = int(request.GET.get("limit", 400))
        except Exception:
            limit = 400

        if limit > 0:
            newest_ids = list(logs.order_by("-timestamp").values_list("id", flat=True)[:limit])
            logs = SimulatorLog.objects.filter(id__in=newest_ids).order_by("timestamp")

        return Response(SimulatorLogSerializer(logs, many=True).data)


class ExportRhythmLog(APIView):
    """
    GET /simulator/export/<run_id>/?format=json|csv|pdf&start=<ISO>&end=<ISO>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, run_id):
        run = SimulationRun.objects.filter(id=run_id, user=request.user).first()
        if not run:
            return Response({"error": "Simulation run not found"}, status=404)

        start_str = request.GET.get("start")
        end_str = request.GET.get("end")
        start_dt = parse_datetime(start_str) if start_str else None
        end_dt = parse_datetime(end_str) if end_str else None
        if start_dt and timezone.is_naive(start_dt):
            start_dt = timezone.make_aware(start_dt)
        if end_dt and timezone.is_naive(end_dt):
            end_dt = timezone.make_aware(end_dt)

        logs = SimulatorLog.objects.filter(run=run).order_by("timestamp")
        if start_dt:
            logs = logs.filter(timestamp__gte=start_dt)
        if end_dt:
            logs = logs.filter(timestamp__lte=end_dt)

        rows = [
            {
                "timestamp": log.timestamp.isoformat(),
                "alignment_score": log.alignment_score,
                "color": log.color,
                "flatline": log.flatline,
                "violations": list(log.violations) if isinstance(log.violations, list) else [],
                "confidence": log.confidence,
                "prompt": log.prompt,
                "response": log.response,
            }
            for log in logs
        ]

        fmt = (request.GET.get("format") or "json").lower()
        filename_base = f"custos-sim-{run.id}"

        if fmt == "json":
            return Response(rows, status=200)

        if fmt == "csv":
            output = io.StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=[
                    "timestamp",
                    "alignment_score",
                    "color",
                    "flatline",
                    "violations",
                    "confidence",
                    "prompt",
                    "response",
                ],
            )
            writer.writeheader()
            for r in rows:
                r2 = dict(r)
                r2["violations"] = ",".join(r2.get("violations", []))
                writer.writerow(r2)
            resp = HttpResponse(output.getvalue(), content_type="text/csv; charset=utf-8")
            resp["Content-Disposition"] = f'attachment; filename="{filename_base}.csv"'
            return resp

        if fmt == "pdf":
            buf = io.BytesIO()
            doc = SimpleDocTemplate(
                buf,
                pagesize=landscape(letter),
                leftMargin=24,
                rightMargin=24,
                topMargin=24,
                bottomMargin=24,
            )
            styles = getSampleStyleSheet()

            data = [
                ["Timestamp", "Score", "Color", "Flatline", "Violations", "Confidence", "Prompt", "Response"]
            ]
            for r in rows:
                data.append(
                    [
                        r["timestamp"],
                        f'{r["alignment_score"]:.3f}',
                        r["color"],
                        "Yes" if r["flatline"] else "No",
                        ", ".join(r["violations"]) if r["violations"] else "",
                        f'{r["confidence"]:.2f}',
                        Paragraph((r["prompt"] or "").replace("\n", "<br/>"), styles["BodyText"]),
                        Paragraph((r["response"] or "").replace("\n", "<br/>"), styles["BodyText"]),
                    ]
                )

            table = Table(
                data,
                colWidths=[1.8 * inch, 0.7 * inch, 0.7 * inch, 0.8 * inch, 1.5 * inch, 0.9 * inch, 3.2 * inch, 3.2 * inch],
                repeatRows=1,
            )
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111111")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#333333")),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#0d0d0d"), colors.HexColor("#151515")]),
                        ("TEXTCOLOR", (0, 1), (-1, -1), colors.whitesmoke),
                        ("FONTSIZE", (0, 1), (-1, -1), 8),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )

            elements = [
                Paragraph(f"Custos Simulator Export — Run {run.id}", styles["Heading2"]),
                Paragraph(
                    f"User: {run.user.username} • Status: {run.status} • Started: {run.started_at} • Ended: {run.ended_at or '—'}",
                    styles["Normal"],
                ),
                table,
            ]
            doc.build(elements)

            pdf = buf.getvalue()
            buf.close()
            resp = HttpResponse(pdf, content_type="application/pdf")
            resp["Content-Disposition"] = f'attachment; filename="{filename_base}.pdf"'
            return resp

        return Response({"error": "Unsupported format"}, status=400)


# -------------------------------
# Manual test push (admin/dev)
# -------------------------------
from django.utils import timezone as tz


class PushTestBeatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, run_id: int):
        payload = {
            "timestamp": tz.now().isoformat(),
            "alignment_score": float(request.data.get("score", 0.8)),
            "color": request.data.get("color", "green"),
            "flatline": bool(request.data.get("flatline", False)),
            "violations": request.data.get("violations", []),
            "confidence": float(request.data.get("confidence", 0.95)),
            "prompt": request.data.get("prompt"),
            "response": request.data.get("response"),
        }
        try:
            push_real_beat(run_id, payload)
        except Exception as e:
            logger.warning("WS manual push failed for run %s: %s", run_id, e)
        return Response({"ok": True, "sent": payload})


# -------------------------------
# Pause / Resume / End
# -------------------------------
class PauseRunView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, run_id: int):
        run = SimulationRun.objects.filter(id=run_id, user=request.user).first()
        if not run:
            return Response({"error": "Run not found"}, status=404)
        if run.status in ("ended", "misaligned"):
            return Response({"error": f"Cannot pause run with status {run.status}"}, status=400)
        run.status = "paused"
        run.save(update_fields=["status", "updated_at"])
        try:
            push_system(run.id, "paused")
        except Exception as e:
            logger.warning("WS system(paused) failed for run %s: %s", run.id, e)
        return Response({"ok": True, "run_id": run.id, "status": run.status})


class ResumeRunView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, run_id: int):
        run = SimulationRun.objects.filter(id=run_id, user=request.user).first()
        if not run:
            return Response({"error": "Run not found"}, status=404)
        if run.status == "ended":
            return Response({"error": "Run already ended"}, status=400)
        run.status = "active"
        run.last_heartbeat = now()
        run.save(update_fields=["status", "last_heartbeat", "updated_at"])
        try:
            push_system(run.id, "resumed")
        except Exception as e:
            logger.warning("WS system(resumed) failed for run %s: %s", run.id, e)
        return Response({"ok": True, "run_id": run.id, "status": run.status})


class EndRunView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, run_id: int):
        run = SimulationRun.objects.filter(id=run_id, user=request.user).first()
        if not run:
            return Response({"error": "Run not found"}, status=404)
        if run.status != "ended":
            run.status = "ended"
            run.ended_at = now()
            run.save(update_fields=["status", "ended_at", "updated_at"])
            try:
                push_system(run.id, "ended")
            except Exception as e:
                logger.warning("WS system(ended) failed for run %s: %s", run.id, e)
        return Response({"ok": True, "run_id": run.id, "status": run.status})
