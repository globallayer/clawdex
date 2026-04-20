"""
Recall Analytics - Compute metrics from tracking data.

Core metrics:
1. Fix Recall Rate = count(is_repeat AND applied_prior_fix AND !re_teach_needed) / count(is_repeat)
2. No-Reteach Success Rate = count(is_repeat AND outcome='pass' AND !re_teach_needed) / count(is_repeat)
3. Recall Drift = week-over-week change in Fix Recall Rate per context_version
"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

from .schemas import RecallMetrics, get_recall_csv_path


def load_events(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    context_version: Optional[str] = None,
) -> list[dict]:
    """Load recall events from CSV with optional filters."""
    csv_path = get_recall_csv_path()
    if not csv_path.exists():
        return []

    events = []
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Apply filters
            if start_date and row["date"] < start_date:
                continue
            if end_date and row["date"] > end_date:
                continue
            if context_version and row["context_version"] != context_version:
                continue

            # Parse booleans
            row["is_repeat"] = row["is_repeat"].lower() == "true"
            row["applied_prior_fix"] = row["applied_prior_fix"].lower() == "true"
            row["re_teach_needed"] = row["re_teach_needed"].lower() == "true"
            row["false_positive"] = row["false_positive"].lower() == "true"

            # Parse numbers
            row["search_rank"] = int(row["search_rank"] or 0)
            row["time_to_fix_min"] = float(row["time_to_fix_min"] or 0)
            row["latency_first_attempt_ms"] = int(row["latency_first_attempt_ms"] or 0)
            row["tokens_in"] = int(row["tokens_in"] or 0)
            row["tokens_out"] = int(row["tokens_out"] or 0)

            events.append(row)

    return events


def compute_metrics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    context_version: Optional[str] = None,
) -> RecallMetrics:
    """
    Compute recall metrics for a time period.

    Args:
        start_date: Start date (YYYY-MM-DD), defaults to 7 days ago
        end_date: End date (YYYY-MM-DD), defaults to today
        context_version: Filter by context version

    Returns:
        RecallMetrics with computed values
    """
    # Default to last 7 days
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if start_date is None:
        start = datetime.now() - timedelta(days=7)
        start_date = start.strftime("%Y-%m-%d")

    events = load_events(start_date, end_date, context_version)

    metrics = RecallMetrics(
        period_start=start_date,
        period_end=end_date,
        context_version=context_version or "all",
    )

    if not events:
        return metrics

    # Total scenarios
    metrics.total_scenarios = len(events)

    # Filter to repeat scenarios for recall metrics
    repeat_events = [e for e in events if e["is_repeat"]]
    metrics.repeat_scenarios = len(repeat_events)

    if metrics.repeat_scenarios > 0:
        # Fix Recall Rate
        # count(is_repeat AND applied_prior_fix AND !re_teach_needed) / count(is_repeat)
        fix_recall_count = sum(
            1 for e in repeat_events if e["applied_prior_fix"] and not e["re_teach_needed"]
        )
        metrics.fix_recall_rate = round(fix_recall_count / metrics.repeat_scenarios, 4)

        # No-Reteach Success Rate
        # count(is_repeat AND outcome='pass' AND !re_teach_needed) / count(is_repeat)
        no_reteach_success = sum(
            1 for e in repeat_events if e["outcome"] == "pass" and not e["re_teach_needed"]
        )
        metrics.no_reteach_success_rate = round(no_reteach_success / metrics.repeat_scenarios, 4)

        # False positive rate among repeats
        false_positives = sum(1 for e in repeat_events if e["false_positive"])
        metrics.false_positive_rate = round(false_positives / metrics.repeat_scenarios, 4)

    # Metrics across all events
    if events:
        # Average search rank (lower is better, 0 means no result)
        ranks = [e["search_rank"] for e in events if e["search_rank"] > 0]
        if ranks:
            metrics.avg_search_rank = round(sum(ranks) / len(ranks), 2)

        # Average time to fix
        times = [e["time_to_fix_min"] for e in events if e["time_to_fix_min"] > 0]
        if times:
            metrics.avg_time_to_fix_min = round(sum(times) / len(times), 2)

        # Average latency
        latencies = [
            e["latency_first_attempt_ms"] for e in events if e["latency_first_attempt_ms"] > 0
        ]
        if latencies:
            metrics.avg_latency_ms = int(sum(latencies) / len(latencies))

    # Group breakdown
    group_data = defaultdict(list)
    for e in events:
        group_data[e["scenario_group"]].append(e)

    for group, group_events in group_data.items():
        group_repeats = [e for e in group_events if e["is_repeat"]]
        if group_repeats:
            recall = sum(
                1 for e in group_repeats if e["applied_prior_fix"] and not e["re_teach_needed"]
            )
            metrics.group_metrics[group] = {
                "total": len(group_events),
                "repeats": len(group_repeats),
                "fix_recall_rate": round(recall / len(group_repeats), 4),
            }

    return metrics


def compute_recall_drift(
    weeks: int = 4,
    context_version: Optional[str] = None,
) -> list[dict]:
    """
    Compute week-over-week recall drift.

    Returns list of weekly metrics to track degradation.
    """
    results = []
    today = datetime.now()

    for i in range(weeks):
        week_end = today - timedelta(days=i * 7)
        week_start = week_end - timedelta(days=7)

        metrics = compute_metrics(
            start_date=week_start.strftime("%Y-%m-%d"),
            end_date=week_end.strftime("%Y-%m-%d"),
            context_version=context_version,
        )

        results.append(
            {
                "week": i + 1,
                "period": f"{week_start.strftime('%m/%d')} - {week_end.strftime('%m/%d')}",
                "fix_recall_rate": metrics.fix_recall_rate,
                "no_reteach_success_rate": metrics.no_reteach_success_rate,
                "repeat_scenarios": metrics.repeat_scenarios,
                "total_scenarios": metrics.total_scenarios,
            }
        )

    # Calculate drift (change from previous week)
    for i in range(len(results) - 1):
        current = results[i]["fix_recall_rate"]
        previous = results[i + 1]["fix_recall_rate"]
        if previous > 0:
            drift = round((current - previous) / previous * 100, 2)
            results[i]["drift_pct"] = drift
        else:
            results[i]["drift_pct"] = 0.0

    if results:
        results[-1]["drift_pct"] = 0.0  # No previous week for oldest

    return results


def weekly_report(context_version: Optional[str] = None) -> str:
    """Generate a human-readable weekly recall report."""
    metrics = compute_metrics(context_version=context_version)
    drift = compute_recall_drift(weeks=4, context_version=context_version)

    lines = [
        "=" * 60,
        "vault404 RECALL REPORT",
        f"Period: {metrics.period_start} to {metrics.period_end}",
        f"Context Version: {metrics.context_version}",
        "=" * 60,
        "",
        "CORE METRICS",
        "-" * 40,
        f"Total Scenarios:        {metrics.total_scenarios}",
        f"Repeat Scenarios:       {metrics.repeat_scenarios}",
        f"Fix Recall Rate:        {metrics.fix_recall_rate * 100:.1f}%",
        f"No-Reteach Success:     {metrics.no_reteach_success_rate * 100:.1f}%",
        f"False Positive Rate:    {metrics.false_positive_rate * 100:.1f}%",
        "",
        "PERFORMANCE",
        "-" * 40,
        f"Avg Search Rank:        {metrics.avg_search_rank:.1f}",
        f"Avg Time to Fix:        {metrics.avg_time_to_fix_min:.1f} min",
        f"Avg Search Latency:     {metrics.avg_latency_ms} ms",
        "",
    ]

    if metrics.group_metrics:
        lines.append("BY SCENARIO GROUP")
        lines.append("-" * 40)
        for group, data in sorted(metrics.group_metrics.items()):
            lines.append(
                f"  {group:15} recall={data['fix_recall_rate'] * 100:.0f}% "
                f"({data['repeats']}/{data['total']})"
            )
        lines.append("")

    if drift:
        lines.append("RECALL DRIFT (4 weeks)")
        lines.append("-" * 40)
        for week in drift:
            drift_str = f"{week['drift_pct']:+.1f}%" if week["drift_pct"] != 0 else "baseline"
            lines.append(
                f"  {week['period']:15} recall={week['fix_recall_rate'] * 100:.0f}% ({drift_str})"
            )

    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)


def export_metrics_json(
    output_path: Optional[str] = None,
    weeks: int = 4,
) -> str:
    """Export metrics to JSON for dashboards/APIs."""
    import json
    from datetime import datetime

    metrics = compute_metrics()
    drift = compute_recall_drift(weeks=weeks)

    data = {
        "generated_at": datetime.now().isoformat(),
        "current_period": metrics.to_dict(),
        "weekly_drift": drift,
    }

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return output_path

    return json.dumps(data, indent=2)
