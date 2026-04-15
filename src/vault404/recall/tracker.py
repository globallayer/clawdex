"""
Recall Tracker - Auto-instruments find_solution → verify_solution flows.

Usage:
    tracker = get_tracker()

    # On find_solution call
    tracker.on_search(run_id, error_message, results, latency_ms)

    # On verify_solution call
    tracker.on_verify(run_id, record_id, success, re_teach_needed)

    # Finalize and write to CSV
    tracker.finalize(run_id, outcome, notes)
"""

import csv
import hashlib
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from threading import Lock

from .schemas import RecallEvent, Outcome, ensure_csv_exists, get_recall_csv_path


class RecallTracker:
    """
    Tracks recall events across find_solution → verify_solution flows.

    Thread-safe singleton that correlates searches with verifications.
    """

    def __init__(self):
        self._events: dict[str, RecallEvent] = {}  # run_id -> event
        self._pending_searches: dict[str, dict] = {}  # Searches waiting for verification
        self._lock = Lock()
        self._model = os.environ.get("VAULT404_MODEL", "unknown")
        self._context_version = os.environ.get("VAULT404_CONTEXT_VERSION", "v1")

    def _generate_run_id(self) -> str:
        """Generate unique run ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"r{timestamp[:12]}"

    def _generate_scenario_id(self, error_message: str) -> str:
        """Generate stable scenario ID from error message."""
        # Normalize error message for stable hashing
        normalized = error_message.lower().strip()[:200]
        hash_val = hashlib.md5(normalized.encode()).hexdigest()[:8]
        return f"scenario-{hash_val}"

    def _classify_scenario_group(self, error_message: str, context: Optional[dict] = None) -> str:
        """Classify error into scenario group."""
        msg_lower = error_message.lower()

        # Check context first
        if context:
            if context.get("category"):
                return context["category"]

        # Classify by error content
        if any(k in msg_lower for k in ["auth", "jwt", "token", "session", "login", "password"]):
            return "auth"
        if any(k in msg_lower for k in ["database", "sql", "postgres", "mysql", "mongo", "query"]):
            return "database"
        if any(k in msg_lower for k in ["cors", "api", "fetch", "request", "response", "http"]):
            return "api"
        if any(k in msg_lower for k in ["type", "typescript", "ts2", "cannot find"]):
            return "types"
        if any(k in msg_lower for k in ["react", "component", "hook", "render", "hydration"]):
            return "frontend"
        if any(k in msg_lower for k in ["docker", "container", "k8s", "kubernetes", "deploy"]):
            return "devops"
        if any(k in msg_lower for k in ["git", "merge", "commit", "push", "branch"]):
            return "git"
        if any(k in msg_lower for k in ["import", "module", "require", "package"]):
            return "modules"
        if any(k in msg_lower for k in ["build", "compile", "webpack", "vite", "esbuild"]):
            return "build"

        return "general"

    def on_search(
        self,
        error_message: str,
        results: list[dict],
        latency_ms: int,
        context: Optional[dict] = None,
        run_id: Optional[str] = None,
    ) -> str:
        """
        Called when find_solution is invoked.

        Returns run_id for correlation with verify_solution.
        """
        with self._lock:
            if run_id is None:
                run_id = self._generate_run_id()

            scenario_id = self._generate_scenario_id(error_message)
            scenario_group = self._classify_scenario_group(error_message, context)

            # Check if this is a repeat scenario
            is_repeat = self._check_is_repeat(scenario_id)

            # Determine if we found a prior fix
            applied_prior_fix = False
            fix_pattern_id = ""
            search_rank = 0

            if results:
                # Check if top result is a verified solution
                top_result = results[0]
                if top_result.get("verified") or top_result.get("confidence", 0) > 0.7:
                    applied_prior_fix = True
                    fix_pattern_id = top_result.get("id", "")
                    search_rank = 1
                else:
                    # Find first verified result
                    for i, r in enumerate(results):
                        if r.get("verified"):
                            search_rank = i + 1
                            fix_pattern_id = r.get("id", "")
                            break

            event = RecallEvent(
                run_id=run_id,
                scenario_id=scenario_id,
                scenario_group=scenario_group,
                is_repeat=is_repeat,
                model=self._model,
                context_version=self._context_version,
                fix_pattern_id=fix_pattern_id,
                applied_prior_fix=applied_prior_fix,
                search_rank=search_rank,
                latency_first_attempt_ms=latency_ms,
                error_message=error_message[:500],
                search_timestamp=datetime.now().isoformat(),
            )

            self._events[run_id] = event
            self._pending_searches[run_id] = {
                "error_message": error_message,
                "results": results,
                "timestamp": time.time(),
            }

            return run_id

    def on_verify(
        self,
        record_id: str,
        success: bool,
        re_teach_needed: bool = False,
        run_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Called when verify_solution is invoked.

        Correlates with the most recent search for this record_id.
        """
        with self._lock:
            # Find matching run_id if not provided
            if run_id is None:
                run_id = self._find_run_for_record(record_id)

            if run_id is None or run_id not in self._events:
                return None

            event = self._events[run_id]
            event.verify_timestamp = datetime.now().isoformat()
            event.re_teach_needed = re_teach_needed

            if success:
                event.outcome = Outcome.PASS.value
            else:
                event.outcome = Outcome.FAIL.value
                # If they tried a suggested fix and it failed, might be false positive
                if event.applied_prior_fix:
                    event.false_positive = True

            # Calculate time to fix
            if event.search_timestamp:
                search_time = datetime.fromisoformat(event.search_timestamp)
                verify_time = datetime.fromisoformat(event.verify_timestamp)
                delta = (verify_time - search_time).total_seconds() / 60
                event.time_to_fix_min = round(delta, 2)

            return run_id

    def finalize(
        self,
        run_id: str,
        outcome: Optional[str] = None,
        notes: str = "",
        tokens_in: int = 0,
        tokens_out: int = 0,
    ) -> bool:
        """
        Finalize an event and write to CSV.

        Call this after the fix flow is complete.
        """
        with self._lock:
            if run_id not in self._events:
                return False

            event = self._events[run_id]

            if outcome:
                event.outcome = outcome
            if notes:
                event.notes = notes
            if tokens_in:
                event.tokens_in = tokens_in
            if tokens_out:
                event.tokens_out = tokens_out

            # Write to CSV
            csv_path = ensure_csv_exists()
            with open(csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=RecallEvent.csv_headers())
                writer.writerow(event.to_csv_row())

            # Mark scenario as seen
            self._mark_scenario_seen(event.scenario_id)

            # Cleanup
            del self._events[run_id]
            if run_id in self._pending_searches:
                del self._pending_searches[run_id]

            return True

    def _check_is_repeat(self, scenario_id: str) -> bool:
        """Check if scenario was seen before."""
        seen_file = self._get_seen_scenarios_path()
        if not seen_file.exists():
            return False

        with open(seen_file, "r", encoding="utf-8") as f:
            seen = set(line.strip() for line in f)

        return scenario_id in seen

    def _mark_scenario_seen(self, scenario_id: str) -> None:
        """Mark scenario as seen."""
        seen_file = self._get_seen_scenarios_path()
        with open(seen_file, "a", encoding="utf-8") as f:
            f.write(f"{scenario_id}\n")

    def _get_seen_scenarios_path(self) -> Path:
        """Get path to seen scenarios file."""
        data_dir = Path(os.environ.get("VAULT404_DATA_DIR", Path.home() / ".vault404"))
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir / "seen_scenarios.txt"

    def _find_run_for_record(self, record_id: str) -> Optional[str]:
        """Find run_id that references this record."""
        for run_id, event in self._events.items():
            if event.fix_pattern_id == record_id:
                return run_id
        return None

    def get_pending_count(self) -> int:
        """Get count of pending (unfinalized) events."""
        with self._lock:
            return len(self._events)

    def cleanup_stale(self, max_age_seconds: int = 3600) -> int:
        """Remove stale pending events older than max_age_seconds."""
        with self._lock:
            now = time.time()
            stale = []

            for run_id, search_data in self._pending_searches.items():
                if now - search_data["timestamp"] > max_age_seconds:
                    stale.append(run_id)

            for run_id in stale:
                if run_id in self._events:
                    # Write as incomplete
                    event = self._events[run_id]
                    event.outcome = Outcome.PENDING.value
                    event.notes = "stale_cleanup"

                    csv_path = ensure_csv_exists()
                    with open(csv_path, "a", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=RecallEvent.csv_headers())
                        writer.writerow(event.to_csv_row())

                    del self._events[run_id]

                if run_id in self._pending_searches:
                    del self._pending_searches[run_id]

            return len(stale)


# Singleton instance
_tracker: Optional[RecallTracker] = None


def get_tracker() -> RecallTracker:
    """Get the global RecallTracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = RecallTracker()
    return _tracker
