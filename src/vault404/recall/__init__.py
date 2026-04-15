"""
vault404 Recall Tracking

Measures how well the AI remembers and applies previously learned fixes.
Two modes:
1. Auto-instrumented: Logs every find_solution → verify_solution flow
2. Eval harness: Controlled benchmark scenarios
"""

from .tracker import RecallTracker, get_tracker
from .schemas import RecallEvent, RecallMetrics
from .analytics import compute_metrics, weekly_report

__all__ = [
    "RecallTracker",
    "get_tracker",
    "RecallEvent",
    "RecallMetrics",
    "compute_metrics",
    "weekly_report",
]
