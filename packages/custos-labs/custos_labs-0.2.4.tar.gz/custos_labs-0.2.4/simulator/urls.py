# simulator/urls.py

from django.urls import path
from .views import (
    CreateSimulationRun,
    CurrentSimulationRun,
    ListSimulationRuns,
    LogAIResponse,
    GetRhythmLog,
    ExportRhythmLog,
    PushTestBeatView,
    PauseRunView,
    ResumeRunView,
    EndRunView,
)

urlpatterns = [
    # Runs
    path("runs/", CreateSimulationRun.as_view(), name="sim-create-run"),
    path("runs/current/", CurrentSimulationRun.as_view(), name="sim-runs-current"),
    path("runs/list/", ListSimulationRuns.as_view(), name="sim-list"),

    # Write/read logs
    path("logs/", LogAIResponse.as_view(), name="sim-logs"),
    path("logs/<int:run_id>/", GetRhythmLog.as_view(), name="sim-get-log"),  # supports ?limit=

    # Export (json|csv|pdf)
    path("export/<int:run_id>/", ExportRhythmLog.as_view(), name="sim-export"),

    # Controls
    path("runs/<int:run_id>/pause/", PauseRunView.as_view(), name="sim-pause"),
    path("runs/<int:run_id>/resume/", ResumeRunView.as_view(), name="sim-resume"),
    path("runs/<int:run_id>/end/", EndRunView.as_view(), name="sim-end"),

    # Dev
    path("push-test/<int:run_id>/", PushTestBeatView.as_view(), name="sim-push-test"),
]
