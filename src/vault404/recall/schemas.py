"""
Recall tracking data schemas.

CSV Schema v2:
run_id,date,scenario_id,scenario_group,is_repeat,model,context_version,
fix_pattern_id,applied_prior_fix,search_rank,re_teach_needed,false_positive,
outcome,time_to_fix_min,latency_first_attempt_ms,tokens_in,tokens_out,notes
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Literal
from enum import Enum
import csv
import os
from pathlib import Path


class Outcome(str, Enum):
    PASS = "pass"
    PARTIAL = "partial"
    FAIL = "fail"
    PENDING = "pending"


@dataclass
class RecallEvent:
    """A single recall measurement event."""

    # Identifiers
    run_id: str
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    scenario_id: str = ""  # Exact bug scenario (stable ID)
    scenario_group: str = ""  # Cluster: auth/db/ui/api/build etc.

    # Context
    is_repeat: bool = False  # True if scenario was seen before
    model: str = ""  # claude-3.7, gpt-4, etc.
    context_version: str = "v1"  # Memory/prompt version for A/B testing

    # Fix tracking
    fix_pattern_id: str = ""  # Canonical fix pattern used
    applied_prior_fix: bool = False  # Did it reuse known pattern?
    search_rank: int = 0  # Was correct fix #1 or #5?
    re_teach_needed: bool = False  # Did human need to re-explain?
    false_positive: bool = False  # Applied wrong fix confidently

    # Outcome
    outcome: str = Outcome.PENDING.value

    # Timing
    time_to_fix_min: float = 0.0
    latency_first_attempt_ms: int = 0

    # Token usage
    tokens_in: int = 0
    tokens_out: int = 0

    # Metadata
    notes: str = ""
    error_message: str = ""  # The error that triggered this
    solution_applied: str = ""  # What solution was used

    # Timestamps for correlation
    search_timestamp: Optional[str] = None
    verify_timestamp: Optional[str] = None

    def to_csv_row(self) -> dict:
        """Convert to CSV row dict."""
        return {
            "run_id": self.run_id,
            "date": self.date,
            "scenario_id": self.scenario_id,
            "scenario_group": self.scenario_group,
            "is_repeat": str(self.is_repeat).lower(),
            "model": self.model,
            "context_version": self.context_version,
            "fix_pattern_id": self.fix_pattern_id,
            "applied_prior_fix": str(self.applied_prior_fix).lower(),
            "search_rank": self.search_rank,
            "re_teach_needed": str(self.re_teach_needed).lower(),
            "false_positive": str(self.false_positive).lower(),
            "outcome": self.outcome,
            "time_to_fix_min": self.time_to_fix_min,
            "latency_first_attempt_ms": self.latency_first_attempt_ms,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "notes": self.notes,
        }

    @classmethod
    def csv_headers(cls) -> list[str]:
        """Get CSV headers."""
        return [
            "run_id",
            "date",
            "scenario_id",
            "scenario_group",
            "is_repeat",
            "model",
            "context_version",
            "fix_pattern_id",
            "applied_prior_fix",
            "search_rank",
            "re_teach_needed",
            "false_positive",
            "outcome",
            "time_to_fix_min",
            "latency_first_attempt_ms",
            "tokens_in",
            "tokens_out",
            "notes",
        ]


@dataclass
class RecallMetrics:
    """Computed recall metrics for a time period."""

    period_start: str
    period_end: str
    context_version: str

    # Core metrics
    total_scenarios: int = 0
    repeat_scenarios: int = 0

    # Fix Recall Rate
    # count(is_repeat=true AND applied_prior_fix=true AND re_teach_needed=false) / count(is_repeat=true)
    fix_recall_rate: float = 0.0

    # No-Reteach Success Rate
    # count(is_repeat=true AND outcome='pass' AND re_teach_needed=false) / count(is_repeat=true)
    no_reteach_success_rate: float = 0.0

    # Additional metrics
    avg_search_rank: float = 0.0  # Lower is better
    false_positive_rate: float = 0.0
    avg_time_to_fix_min: float = 0.0
    avg_latency_ms: int = 0

    # Breakdown by group
    group_metrics: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def get_recall_csv_path() -> Path:
    """Get path to recall tracking CSV."""
    data_dir = Path(os.environ.get("VAULT404_DATA_DIR", Path.home() / ".vault404"))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "recall_tracking.csv"


def ensure_csv_exists() -> Path:
    """Ensure CSV file exists with headers."""
    csv_path = get_recall_csv_path()
    if not csv_path.exists():
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=RecallEvent.csv_headers())
            writer.writeheader()
    return csv_path
