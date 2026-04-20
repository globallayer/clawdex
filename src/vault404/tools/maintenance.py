"""Maintenance tools for vault404 - verify, update, stats, purge, export"""

import json
import os
from pathlib import Path
from typing import Optional
from datetime import datetime
from ..storage import get_storage, reset_storage
from ..sync.anonymizer import anonymize_record
from ..sync.contribution import ContributionManager
from ..sync.community import get_community_brain
from ..recall.tracker import get_tracker

# Enable recall tracking via environment variable
RECALL_TRACKING = os.environ.get("VAULT404_RECALL_TRACKING", "true").lower() in ("true", "1", "yes")


# Global contribution manager instance
_contrib: Optional[ContributionManager] = None


def get_contribution_manager() -> ContributionManager:
    global _contrib
    if _contrib is None:
        _contrib = ContributionManager()
    return _contrib


async def verify_solution(
    record_id: str,
    success: bool,
    re_teach_needed: bool = False,
    run_id: Optional[str] = None,
) -> dict:
    """
    Verify whether a solution worked or not.

    IMPORTANT: Verified solutions are AUTOMATICALLY contributed to the
    community brain. This is how AI agents collectively get smarter.

    Args:
        record_id: The ID of the error_fix record
        success: True if the solution worked, False if it didn't
        re_teach_needed: True if human had to re-explain the fix (for recall tracking)
        run_id: Optional run_id from find_solution for correlation

    Returns:
        dict with confirmation and contribution status
    """
    storage = get_storage()
    contrib = get_contribution_manager()

    await storage.verify_solution(record_id, success)

    status = "successful" if success else "unsuccessful"
    response = {
        "_summary": f"[ok] verified as {status}",
        "success": True,
        "message": f"Marked solution {record_id} as {status}",
        "record_id": record_id,
        "verified_as": status,
    }

    # Track recall verification
    if RECALL_TRACKING:
        try:
            tracker = get_tracker()
            tracked_run_id = tracker.on_verify(
                record_id=record_id,
                success=success,
                re_teach_needed=re_teach_needed,
                run_id=run_id,
            )
            if tracked_run_id:
                # Finalize the recall event
                outcome = "pass" if success else "fail"
                tracker.finalize(tracked_run_id, outcome=outcome)
                response["_recall_tracked"] = True
        except Exception:
            pass  # Don't fail verification if tracking fails

    # AUTO-CONTRIBUTE: If solution worked, share it with the community
    if success:
        filepath = storage.errors_dir / f"{record_id}.json"
        if filepath.exists():
            record = json.loads(filepath.read_text(encoding="utf-8"))
            anon = anonymize_record(record)
            contrib_result = await contrib.confirm_contribution(record_id, anon)

            if contrib_result.get("success"):
                response["contributed"] = True
                response["message"] += " → Auto-contributed to community brain."
            else:
                response["contributed"] = False
                response["contribution_note"] = contrib_result.get("reason", "Already contributed")

    return response


async def get_stats() -> dict:
    """
    Get statistics about the vault404 knowledge base.

    Returns both local and community brain stats.

    Returns:
        dict with stats about records stored locally and in community brain
    """
    storage = get_storage()
    community = get_community_brain()

    # Get local stats
    local_stats = await storage.get_stats()
    local_total = local_stats.get("total_records", 0)
    local_fixes = local_stats.get("errors", 0)
    local_decisions = local_stats.get("decisions", 0)
    local_patterns = local_stats.get("patterns", 0)

    # Get community brain stats
    community_stats = await community.get_stats()
    community_total = community_stats.get("total", 0)
    community_fixes = community_stats.get("fixes", 0)
    community_decisions = community_stats.get("decisions", 0)
    community_patterns = community_stats.get("patterns", 0)

    # Combined totals
    combined_total = local_total + community_total

    # Build summary
    summary_parts = [f"vault404: {combined_total} total records"]
    summary_parts.append(
        f"Local: {local_total} ({local_fixes} fixes, {local_decisions} decisions, {local_patterns} patterns)"
    )
    summary_parts.append(
        f"Community Brain: {community_total} ({community_fixes} fixes, {community_decisions} decisions, {community_patterns} patterns)"
    )

    return {
        "_summary": " | ".join(summary_parts),
        "success": True,
        "stats": {
            "combined_total": combined_total,
            "local": {
                "total": local_total,
                "fixes": local_fixes,
                "decisions": local_decisions,
                "patterns": local_patterns,
                "data_directory": local_stats.get("data_dir", ""),
            },
            "community": {
                "total": community_total,
                "fixes": community_fixes,
                "decisions": community_decisions,
                "patterns": community_patterns,
                "categories": community_stats.get("categories", {}),
                "online": community_stats.get("success", False),
            },
        },
        "message": "vault404 statistics retrieved (local + community)",
    }


async def purge_all(confirm: bool = False) -> dict:
    """
    Delete ALL vault404 data. This is IRREVERSIBLE.

    YOUR RIGHT TO DELETE: This implements GDPR Article 17.
    All your data will be permanently removed.

    Args:
        confirm: Must be True to actually delete. Safety check.

    Returns:
        dict with result
    """
    if not confirm:
        return {
            "success": False,
            "message": "SAFETY CHECK: Set confirm=True to delete all data. This is IRREVERSIBLE.",
            "warning": "All error fixes, decisions, and patterns will be permanently deleted.",
        }

    data_dir = Path.home() / ".vault404"

    if data_dir.exists():
        import shutil

        shutil.rmtree(data_dir)

    # Reset the centralized storage singleton
    reset_storage()

    return {
        "success": True,
        "message": "All vault404 data has been permanently deleted.",
        "deleted_path": str(data_dir),
    }


async def export_all(output_path: Optional[str] = None) -> dict:
    """
    Export ALL your vault404 data to a JSON file.

    YOUR RIGHT TO DATA PORTABILITY: This implements GDPR Article 20.
    You can export all your data at any time.

    Args:
        output_path: Where to save the export. Defaults to ~/vault404-export-{date}.json

    Returns:
        dict with export location
    """
    storage = get_storage()

    # Get all stats
    stats = await storage.get_stats()

    # Get all records
    all_records = await storage.get_all_records()

    # Prepare export data
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "version": "0.1.0",
        "stats": stats,
        "data": {
            "error_fixes": all_records.get("errors", []),
            "decisions": all_records.get("decisions", []),
            "patterns": all_records.get("patterns", []),
        },
        "metadata": {
            "format": "vault404-export-v1",
            "description": "Complete export of vault404 knowledge base",
        },
    }

    # Determine output path
    if output_path is None:
        date_str = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = str(Path.home() / f"vault404-export-{date_str}.json")

    # Write export
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    return {
        "success": True,
        "message": f"Exported all vault404 data to {output_path}",
        "export_path": output_path,
        "records_exported": {
            "error_fixes": len(all_records.get("errors", [])),
            "decisions": len(all_records.get("decisions", [])),
            "patterns": len(all_records.get("patterns", [])),
        },
    }
