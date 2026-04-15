"""Querying tools for vault404 - find solutions, decisions, and patterns"""

import os
import time
from typing import Optional
from ..storage import get_storage, Context
from ..sync.community import federated_search
from ..recall.tracker import get_tracker

# Enable community search via environment variable
COMMUNITY_ENABLED = os.environ.get("VAULT404_COMMUNITY", "").lower() in ("true", "1", "yes")

# Enable recall tracking via environment variable
RECALL_TRACKING = os.environ.get("VAULT404_RECALL_TRACKING", "true").lower() in ("true", "1", "yes")


async def find_solution(
    error_message: str,
    project: Optional[str] = None,
    language: Optional[str] = None,
    framework: Optional[str] = None,
    database: Optional[str] = None,
    platform: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 3,
) -> dict:
    """
    Find solutions for an error from vault404.

    ALWAYS check this first when encountering an error.
    Returns past solutions ranked by relevance and context match.

    Args:
        error_message: The error message to find solutions for
        project: Current project (for context matching)
        language: Current language (for context matching)
        framework: Current framework (for context matching)
        database: Current database (for context matching)
        platform: Current platform (for context matching)
        category: Issue category (for context matching)
        limit: Maximum number of solutions to return

    Returns:
        dict with solutions ranked by relevance
    """
    start_time = time.time()
    storage = get_storage()

    context = None
    context_dict = None
    if any([project, language, framework, database, platform, category]):
        context = Context(
            project=project,
            language=language,
            framework=framework,
            database=database,
            platform=platform,
            category=category,
        )
        context_dict = {
            "language": language,
            "framework": framework,
            "database": database,
            "platform": platform,
            "category": category,
        }

    local_results = await storage.find_solutions(
        error_message=error_message,
        context=context,
        limit=limit,
    )

    # Optionally include community results
    all_results = local_results
    community_count = 0

    if COMMUNITY_ENABLED:
        try:
            all_results = await federated_search(
                error_message,
                local_results,
                context_dict,
                limit,
            )
            community_count = sum(1 for r in all_results if r.get("source") == "community")
        except Exception:
            pass  # Fall back to local only

    # Calculate latency
    latency_ms = int((time.time() - start_time) * 1000)

    # Track recall event
    run_id = None
    if RECALL_TRACKING:
        try:
            tracker = get_tracker()
            run_id = tracker.on_search(
                error_message=error_message,
                results=all_results,
                latency_ms=latency_ms,
                context=context_dict,
            )
        except Exception:
            pass  # Don't fail search if tracking fails

    if not all_results:
        return {
            "_summary": "No solutions found",
            "found": False,
            "message": "No matching solutions found in vault404",
            "solutions": [],
            "suggestion": "After fixing this error, use log_error_fix to save the solution.",
            "_run_id": run_id,  # For correlation with verify_solution
        }

    # Build compact summary
    count = len(all_results)
    top = all_results[0]
    top_solution = top.get("solution", "")[:60]
    summary = f"Found {count} solution(s). Top: {top_solution}..."

    return {
        "_summary": summary,
        "found": True,
        "message": f"Found {count} potential solution(s)"
        + (f" ({community_count} from community)" if community_count else ""),
        "solutions": [
            {
                "id": r.get("id", ""),
                "solution": r.get("solution", ""),
                "original_error": r.get("error", ""),
                "context": r.get("context", {}),
                "confidence": round(r.get("score", 0), 2),
                "verified": r.get("verified", False),
                "source": r.get("source", "local"),
            }
            for r in all_results
        ],
        "_run_id": run_id,  # For correlation with verify_solution
        "_latency_ms": latency_ms,
    }


async def find_decision(
    topic: str,
    project: Optional[str] = None,
    component: Optional[str] = None,
    limit: int = 3,
) -> dict:
    """
    Find past decisions on a topic from vault404.

    Check this before making architectural choices.

    Args:
        topic: Topic to search for (e.g., "database choice", "auth strategy")
        project: Filter by project
        component: Filter by component
        limit: Maximum number of decisions to return

    Returns:
        dict with relevant past decisions
    """
    storage = get_storage()

    context = None
    if project or component:
        context = Context(project=project, category=component)

    results = await storage.find_decisions(
        topic=topic,
        context=context,
        limit=limit,
    )

    if not results:
        return {
            "_summary": f"No decisions found for: {topic}",
            "found": False,
            "message": f"No past decisions found for: {topic}",
            "decisions": [],
            "suggestion": "After making a decision, use log_decision to save it.",
        }

    count = len(results)
    top = results[0]
    summary = (
        f"Found {count} decision(s). Top: {top.get('title', '')} → {top.get('choice', '')[:40]}"
    )

    return {
        "_summary": summary,
        "found": True,
        "message": f"Found {count} relevant decision(s)",
        "decisions": [
            {
                "id": r.get("id", ""),
                "title": r.get("title", ""),
                "choice": r.get("choice", ""),
                "relevance": round(r.get("similarity", 0), 2),
            }
            for r in results
        ],
    }


async def find_pattern(
    problem: str,
    category: Optional[str] = None,
    language: Optional[str] = None,
    framework: Optional[str] = None,
    limit: int = 3,
) -> dict:
    """
    Find reusable patterns for a problem from vault404.

    Check this before implementing solutions.

    Args:
        problem: The problem to find patterns for
        category: Category filter (database, auth, api, etc.)
        language: Language filter
        framework: Framework filter
        limit: Maximum number of patterns to return

    Returns:
        dict with relevant patterns
    """
    storage = get_storage()

    results = await storage.find_patterns(
        problem=problem,
        category=category,
        limit=limit,
    )

    if not results:
        return {
            "_summary": f"No patterns found for: {problem}",
            "found": False,
            "message": f"No patterns found for: {problem}",
            "patterns": [],
            "suggestion": "After solving this, use log_pattern to save the pattern.",
        }

    count = len(results)
    top = results[0]
    summary = f"Found {count} pattern(s). Top: {top.get('name', '')}"

    return {
        "_summary": summary,
        "found": True,
        "message": f"Found {count} relevant pattern(s)",
        "patterns": [
            {
                "id": r.get("id", ""),
                "name": r.get("name", ""),
                "category": r.get("category", ""),
                "problem": r.get("problem", ""),
                "solution": r.get("solution", ""),
                "relevance": round(r.get("similarity", 0), 2),
            }
            for r in results
        ],
    }
