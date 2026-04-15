#!/usr/bin/env python3
"""
vault404 Eval Harness - Controlled benchmark for recall testing.

Runs predefined error scenarios through the system and measures recall.

Usage:
    python scripts/eval_harness.py                    # Run all scenarios
    python scripts/eval_harness.py --group auth      # Run auth scenarios only
    python scripts/eval_harness.py --report          # Generate report only
    python scripts/eval_harness.py --export metrics.json  # Export metrics

Environment:
    VAULT404_MODEL          - Model identifier (default: eval-harness)
    VAULT404_CONTEXT_VERSION - Context version for A/B testing (default: v1)
"""

import argparse
import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from vault404.tools.querying import find_solution
from vault404.tools.maintenance import verify_solution
from vault404.recall.tracker import get_tracker, RecallTracker
from vault404.recall.analytics import compute_metrics, weekly_report, export_metrics_json
from vault404.recall.schemas import Outcome


@dataclass
class EvalScenario:
    """A test scenario for recall evaluation."""
    id: str
    group: str
    error_message: str
    expected_fix_pattern: str  # Keywords or pattern ID to match
    context: dict
    is_known: bool = True  # Should vault404 know this fix?


# =============================================================================
# TEST SCENARIOS
# =============================================================================

EVAL_SCENARIOS = [
    # Auth scenarios
    EvalScenario(
        id="auth-jwt-expired-01",
        group="auth",
        error_message="JWTExpired: jwt expired",
        expected_fix_pattern="refresh token",
        context={"language": "typescript", "category": "auth"},
    ),
    EvalScenario(
        id="auth-cors-01",
        group="auth",
        error_message="Access to fetch blocked by CORS policy: No 'Access-Control-Allow-Origin'",
        expected_fix_pattern="cors",
        context={"language": "typescript", "framework": "express"},
    ),
    EvalScenario(
        id="auth-nextauth-secret-01",
        group="auth",
        error_message="NextAuth: NEXTAUTH_SECRET is missing",
        expected_fix_pattern="NEXTAUTH_SECRET",
        context={"language": "typescript", "framework": "nextjs"},
    ),

    # Database scenarios
    EvalScenario(
        id="db-conn-refused-01",
        group="database",
        error_message="ECONNREFUSED 127.0.0.1:5432",
        expected_fix_pattern="postgresql|container|localhost",
        context={"database": "postgresql"},
    ),
    EvalScenario(
        id="db-unique-violation-01",
        group="database",
        error_message="ERROR: duplicate key value violates unique constraint",
        expected_fix_pattern="ON CONFLICT|upsert",
        context={"database": "postgresql"},
    ),
    EvalScenario(
        id="db-migration-drift-01",
        group="database",
        error_message="Prisma: Migration failed - database schema drift detected",
        expected_fix_pattern="prisma db pull|migrate reset",
        context={"database": "postgresql", "framework": "prisma"},
    ),

    # TypeScript scenarios
    EvalScenario(
        id="ts-undefined-01",
        group="types",
        error_message="Object is possibly 'undefined'. TS2532",
        expected_fix_pattern="optional chaining|nullish",
        context={"language": "typescript"},
    ),
    EvalScenario(
        id="ts-module-not-found-01",
        group="types",
        error_message="Cannot find module 'react' or its corresponding type declarations",
        expected_fix_pattern="npm install|@types",
        context={"language": "typescript", "framework": "react"},
    ),

    # React/Next.js scenarios
    EvalScenario(
        id="react-hydration-01",
        group="frontend",
        error_message="Hydration failed because the initial UI does not match what was rendered on the server",
        expected_fix_pattern="useEffect|dynamic|ssr: false",
        context={"language": "typescript", "framework": "nextjs"},
    ),
    EvalScenario(
        id="react-hook-deps-01",
        group="frontend",
        error_message="React Hook useEffect has a missing dependency",
        expected_fix_pattern="dependency array|useCallback",
        context={"language": "typescript", "framework": "react"},
    ),
    EvalScenario(
        id="nextjs-use-client-01",
        group="frontend",
        error_message="Error: You're importing a component that needs useState but none of its parents are client components",
        expected_fix_pattern="use client",
        context={"language": "typescript", "framework": "nextjs"},
    ),

    # DevOps scenarios
    EvalScenario(
        id="docker-port-conflict-01",
        group="devops",
        error_message="Error: Cannot start service: driver failed programming external connectivity",
        expected_fix_pattern="port|netstat",
        context={"platform": "docker"},
    ),
    EvalScenario(
        id="git-merge-conflict-01",
        group="git",
        error_message="CONFLICT (content): Merge conflict in file.txt",
        expected_fix_pattern="resolve|<<<<<<",
        context={"platform": "git"},
    ),
    EvalScenario(
        id="k8s-crashloop-01",
        group="devops",
        error_message="Error: CrashLoopBackOff",
        expected_fix_pattern="logs|env vars|resources",
        context={"platform": "kubernetes"},
    ),

    # Python scenarios
    EvalScenario(
        id="py-module-not-found-01",
        group="modules",
        error_message="ModuleNotFoundError: No module named 'requests'",
        expected_fix_pattern="pip install",
        context={"language": "python"},
    ),
    EvalScenario(
        id="py-none-attribute-01",
        group="types",
        error_message="AttributeError: 'NoneType' object has no attribute 'get'",
        expected_fix_pattern="None check|if obj",
        context={"language": "python"},
    ),
]


def check_solution_matches(solution: str, expected_pattern: str) -> bool:
    """Check if solution contains expected pattern keywords."""
    import re
    solution_lower = solution.lower()
    patterns = expected_pattern.lower().split("|")
    return any(re.search(p.strip(), solution_lower) for p in patterns)


async def run_scenario(
    scenario: EvalScenario,
    tracker: RecallTracker,
    verbose: bool = False,
) -> dict:
    """Run a single evaluation scenario."""
    start = time.time()

    # Search for solution
    result = await find_solution(
        error_message=scenario.error_message,
        language=scenario.context.get("language"),
        framework=scenario.context.get("framework"),
        database=scenario.context.get("database"),
        platform=scenario.context.get("platform"),
        category=scenario.context.get("category"),
    )

    latency_ms = int((time.time() - start) * 1000)

    # Analyze results
    found = result.get("found", False)
    solutions = result.get("solutions", [])

    # Check if correct solution was found
    correct_found = False
    correct_rank = 0
    matched_solution = ""

    for i, sol in enumerate(solutions):
        if check_solution_matches(sol.get("solution", ""), scenario.expected_fix_pattern):
            correct_found = True
            correct_rank = i + 1
            matched_solution = sol.get("solution", "")[:100]
            break

    # Determine outcome
    if correct_found and correct_rank == 1:
        outcome = Outcome.PASS.value
        re_teach_needed = False
    elif correct_found:
        outcome = Outcome.PARTIAL.value
        re_teach_needed = False  # Found it, just not top result
    else:
        outcome = Outcome.FAIL.value
        re_teach_needed = True

    # Track the event
    run_id = result.get("_run_id")
    if run_id:
        tracker.on_verify(
            record_id=solutions[0]["id"] if solutions else "",
            success=outcome == Outcome.PASS.value,
            re_teach_needed=re_teach_needed,
            run_id=run_id,
        )
        tracker.finalize(
            run_id,
            outcome=outcome,
            notes=f"eval_harness|{scenario.id}",
        )

    eval_result = {
        "scenario_id": scenario.id,
        "group": scenario.group,
        "outcome": outcome,
        "found": found,
        "correct_found": correct_found,
        "correct_rank": correct_rank,
        "solutions_returned": len(solutions),
        "latency_ms": latency_ms,
        "re_teach_needed": re_teach_needed,
    }

    if verbose:
        status = "✓" if outcome == Outcome.PASS.value else ("◐" if outcome == Outcome.PARTIAL.value else "✗")
        print(f"  {status} {scenario.id}: {outcome} (rank={correct_rank}, {latency_ms}ms)")
        if correct_found and verbose:
            print(f"      Matched: {matched_solution}...")

    return eval_result


async def run_eval(
    scenarios: list[EvalScenario],
    verbose: bool = False,
) -> dict:
    """Run full evaluation suite."""
    print("=" * 60)
    print("vault404 EVAL HARNESS")
    print(f"Scenarios: {len(scenarios)}")
    print(f"Context Version: {os.environ.get('VAULT404_CONTEXT_VERSION', 'v1')}")
    print("=" * 60)
    print()

    tracker = get_tracker()
    results = []
    start_time = time.time()

    # Group scenarios
    groups = {}
    for s in scenarios:
        groups.setdefault(s.group, []).append(s)

    for group, group_scenarios in sorted(groups.items()):
        print(f"[{group}] - {len(group_scenarios)} scenarios")
        print("-" * 40)

        for scenario in group_scenarios:
            result = await run_scenario(scenario, tracker, verbose)
            results.append(result)

        print()

    # Summary
    elapsed = time.time() - start_time
    passed = sum(1 for r in results if r["outcome"] == Outcome.PASS.value)
    partial = sum(1 for r in results if r["outcome"] == Outcome.PARTIAL.value)
    failed = sum(1 for r in results if r["outcome"] == Outcome.FAIL.value)

    print("=" * 60)
    print("SUMMARY")
    print("-" * 40)
    print(f"Total:    {len(results)}")
    print(f"Passed:   {passed} ({passed/len(results)*100:.1f}%)")
    print(f"Partial:  {partial} ({partial/len(results)*100:.1f}%)")
    print(f"Failed:   {failed} ({failed/len(results)*100:.1f}%)")
    print(f"Time:     {elapsed:.1f}s")
    print()

    # Avg latency
    avg_latency = sum(r["latency_ms"] for r in results) / len(results)
    print(f"Avg Latency: {avg_latency:.0f}ms")

    # Avg rank for correct solutions
    correct_ranks = [r["correct_rank"] for r in results if r["correct_found"]]
    if correct_ranks:
        print(f"Avg Correct Rank: {sum(correct_ranks)/len(correct_ranks):.1f}")

    print("=" * 60)

    return {
        "timestamp": datetime.now().isoformat(),
        "total": len(results),
        "passed": passed,
        "partial": partial,
        "failed": failed,
        "pass_rate": passed / len(results) if results else 0,
        "elapsed_seconds": elapsed,
        "avg_latency_ms": avg_latency,
        "results": results,
    }


def filter_scenarios(scenarios: list[EvalScenario], group: Optional[str] = None) -> list[EvalScenario]:
    """Filter scenarios by group."""
    if group:
        return [s for s in scenarios if s.group == group]
    return scenarios


async def main():
    parser = argparse.ArgumentParser(description="vault404 Eval Harness")
    parser.add_argument("--group", "-g", help="Filter by scenario group")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--report", "-r", action="store_true", help="Show recall report only")
    parser.add_argument("--export", "-e", help="Export metrics to JSON file")
    parser.add_argument("--list", "-l", action="store_true", help="List available scenarios")
    args = parser.parse_args()

    # List scenarios
    if args.list:
        groups = {}
        for s in EVAL_SCENARIOS:
            groups.setdefault(s.group, []).append(s)

        print("Available scenarios:")
        for group, scenarios in sorted(groups.items()):
            print(f"\n[{group}]")
            for s in scenarios:
                print(f"  - {s.id}")
        return 0

    # Report only
    if args.report:
        print(weekly_report())
        return 0

    # Export metrics
    if args.export:
        path = export_metrics_json(args.export)
        print(f"Metrics exported to: {path}")
        return 0

    # Run evaluation
    scenarios = filter_scenarios(EVAL_SCENARIOS, args.group)
    if not scenarios:
        print(f"No scenarios found for group: {args.group}")
        return 1

    result = await run_eval(scenarios, verbose=args.verbose)

    # Save results
    results_dir = Path.home() / ".vault404" / "eval_results"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"\nResults saved: {results_file}")
    return 0 if result["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
