"""
vault404 Command Line Interface

Usage:
    vault404 setup-claude    Configure Claude Code (MCP + permissions)
    vault404 stats           Show knowledge base statistics
    vault404 export [PATH]   Export all data to JSON
    vault404 purge           Delete all data (requires confirmation)
    vault404 search QUERY    Search for solutions
    vault404 encrypt         Enable encryption for data at rest
    vault404 serve           Start the REST API server
    vault404 serve-mcp       Start the MCP server
    vault404 recall          Show recall metrics (fix recall rate, drift)
"""

import argparse
import asyncio
import json
import sys

# Fix Windows console encoding for Unicode
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from .storage import get_storage, configure_storage, reset_storage
from .tools.maintenance import get_stats, export_all, purge_all
from .tools.querying import find_solution, find_decision, find_pattern
from .recall.analytics import compute_metrics, weekly_report, export_metrics_json


def print_json(data: dict) -> None:
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_stats(args: argparse.Namespace) -> int:
    """Show knowledge base statistics."""

    async def run():
        result = await get_stats()
        if args.json:
            print_json(result)
        else:
            stats = result.get("stats", {})
            print("\n📊 vault404 Statistics")
            print("=" * 40)
            print(f"  Error Fixes:  {stats.get('error_fixes', 0)}")
            print(f"  Decisions:    {stats.get('decisions', 0)}")
            print(f"  Patterns:     {stats.get('patterns', 0)}")
            print("  ─────────────────────────")
            print(f"  Total:        {stats.get('total_records', 0)}")
            print(f"\n  Data dir: {stats.get('data_directory', 'N/A')}")
        return 0

    return asyncio.run(run())


def cmd_export(args: argparse.Namespace) -> int:
    """Export all data to JSON file."""

    async def run():
        result = await export_all(args.output)
        if args.json:
            print_json(result)
        else:
            if result.get("success"):
                print(f"\n✅ {result.get('message')}")
                records = result.get("records_exported", {})
                print(f"   Error fixes: {records.get('error_fixes', 0)}")
                print(f"   Decisions:   {records.get('decisions', 0)}")
                print(f"   Patterns:    {records.get('patterns', 0)}")
            else:
                print(f"\n❌ Export failed: {result.get('message')}")
                return 1
        return 0

    return asyncio.run(run())


def cmd_purge(args: argparse.Namespace) -> int:
    """Delete all vault404 data."""
    if not args.confirm:
        print("\n⚠️  WARNING: This will permanently delete ALL vault404 data!")
        print("   This action cannot be undone.\n")
        confirm = input("   Type 'DELETE' to confirm: ")
        if confirm != "DELETE":
            print("\n   Aborted.")
            return 1

    async def run():
        result = await purge_all(confirm=True)
        if result.get("success"):
            print(f"\n✅ {result.get('message')}")
        else:
            print(f"\n❌ {result.get('message')}")
            return 1
        return 0

    return asyncio.run(run())


def cmd_search(args: argparse.Namespace) -> int:
    """Search for solutions, decisions, or patterns."""

    async def run():
        query = " ".join(args.query)

        if args.type == "solution" or args.type == "all":
            result = await find_solution(query, limit=args.limit)
            if args.json:
                print_json({"solutions": result})
            else:
                print("\n🔍 Solutions:")
                if result.get("found"):
                    for s in result.get("solutions", []):
                        print(
                            f"\n  [{s.get('confidence', 0):.0%}] {s.get('original_error', '')[:60]}"
                        )
                        print(f"       → {s.get('solution', '')[:80]}")
                        if s.get("verified"):
                            print("       ✓ Verified")
                else:
                    print("  No solutions found.")

        if args.type == "decision" or args.type == "all":
            result = await find_decision(query, limit=args.limit)
            if args.json:
                print_json({"decisions": result})
            else:
                print("\n📋 Decisions:")
                if result.get("found"):
                    for d in result.get("decisions", []):
                        print(f"\n  [{d.get('relevance', 0):.0%}] {d.get('title', '')}")
                        print(f"       → {d.get('choice', '')}")
                else:
                    print("  No decisions found.")

        if args.type == "pattern" or args.type == "all":
            result = await find_pattern(query, limit=args.limit)
            if args.json:
                print_json({"patterns": result})
            else:
                print("\n📐 Patterns:")
                if result.get("found"):
                    for p in result.get("patterns", []):
                        print(
                            f"\n  [{p.get('relevance', 0):.0%}] {p.get('name', '')} ({p.get('category', '')})"
                        )
                        print(f"       Problem: {p.get('problem', '')[:60]}")
                        print(f"       Solution: {p.get('solution', '')[:60]}")
                else:
                    print("  No patterns found.")

        print()
        return 0

    return asyncio.run(run())


def cmd_encrypt(args: argparse.Namespace) -> int:
    """Enable encryption for data at rest."""

    # Check if already encrypted
    storage = get_storage()
    if storage.encrypted:
        print("\n✅ Encryption is already enabled.")
        return 0

    print("\n🔐 Enabling encryption for vault404 data...")
    print("   This will encrypt all future data at rest using AES-256.")

    if args.password:
        password = args.password
    else:
        import getpass

        password = getpass.getpass(
            "   Enter encryption password (or press Enter for auto-generated): "
        )
        if not password:
            password = None
            print("   Using auto-generated encryption key.")

    # Reset and reconfigure with encryption
    reset_storage()
    configure_storage(encrypted=True, password=password)

    print("\n✅ Encryption enabled!")
    print("   Set VAULT404_ENCRYPTED=true to enable on future runs.")
    if password:
        print("   Set VAULT404_PASSWORD to your password to unlock data.")

    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    """Start the REST API server."""
    try:
        from .api.server import run_server
    except ImportError as e:
        print(f"\nError: Could not import API server: {e}")
        print("Make sure FastAPI and uvicorn are installed:")
        print("  pip install fastapi uvicorn")
        return 1

    print("\n🚀 Starting Vault404 REST API server...")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   Docs: http://{args.host}:{args.port}/docs")
    print()

    run_server(
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="debug" if args.verbose else "info",
    )
    return 0


def cmd_serve_mcp(args: argparse.Namespace) -> int:
    """Start the MCP server."""
    from .mcp_server import main

    main()
    return 0


def cmd_recall(args: argparse.Namespace) -> int:
    """Show recall metrics."""
    # Export to file
    if args.export:
        path = export_metrics_json(args.export, weeks=args.weeks)
        print(f"Metrics exported to: {path}")
        return 0

    # JSON output
    if args.json:
        metrics = compute_metrics(context_version=args.version)
        print_json(metrics.to_dict())
        return 0

    # Human-readable report
    print(weekly_report(context_version=args.version))
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    """Sync all verified local data to the community brain."""
    import httpx
    from pathlib import Path

    print("\n🌐 Syncing local vault404 data to Community Brain...")

    # Supabase config
    API_URL = "https://sbbhtxxegxkqjbfqcrwz.supabase.co/rest/v1"
    API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNiYmh0eHhlZ3hrcWpiZnFjcnd6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM3ODU4MjcsImV4cCI6MjA4OTM2MTgyN30.L4D9egjGWUbfpbGkZogVWPia4y6GBKjvJ0FhjB8fuIc"

    headers = {
        "Content-Type": "application/json",
        "Prefer": "return=representation",
        "apikey": API_KEY,
        "Authorization": f"Bearer {API_KEY}",
    }

    data_dir = Path.home() / ".vault404"
    if not data_dir.exists():
        print("  No local vault404 data found.")
        return 0

    synced = {"fixes": 0, "decisions": 0, "patterns": 0}
    errors = 0

    # Sync error fixes
    errors_dir = data_dir / "errors"
    if errors_dir.exists():
        for f in errors_dir.glob("*.json"):
            try:
                record = json.loads(f.read_text(encoding="utf-8"))
                if not record.get("verified", False):
                    continue  # Only sync verified

                import hashlib

                content = f"{record.get('error', {}).get('message', '')[:100]}|{record.get('solution', {}).get('description', '')[:100]}"
                content_hash = hashlib.md5(content.encode(), usedforsecurity=False).hexdigest()

                payload = {
                    "content_hash": content_hash,
                    "record_type": "error_fix",
                    "category": record.get("category"),
                    "language": record.get("context", {}).get("language"),
                    "framework": record.get("context", {}).get("framework"),
                    "database": record.get("context", {}).get("database"),
                    "platform": record.get("context", {}).get("platform"),
                    "error_data": record.get("error", {}),
                    "solution_data": record.get("solution", {}),
                    "verification_count": record.get("success_count", 1),
                    "contributor_hash": "local_sync",
                }

                with httpx.Client() as client:
                    resp = client.post(
                        f"{API_URL}/community_solutions",
                        headers=headers,
                        json=payload,
                        timeout=10.0,
                    )
                    if resp.status_code in (200, 201):
                        synced["fixes"] += 1
                    elif resp.status_code == 409:
                        pass  # Duplicate, skip
                    else:
                        errors += 1
            except Exception as e:
                if args.verbose:
                    print(f"  Error syncing {f.name}: {e}")
                errors += 1

    # Sync decisions
    decisions_dir = data_dir / "decisions"
    if decisions_dir.exists():
        for f in decisions_dir.glob("*.json"):
            try:
                record = json.loads(f.read_text(encoding="utf-8"))

                import hashlib

                content = f"{record.get('title', '')[:100]}|{record.get('choice', '')[:100]}"
                content_hash = hashlib.md5(content.encode(), usedforsecurity=False).hexdigest()

                payload = {
                    "content_hash": content_hash,
                    "record_type": "decision",
                    "category": record.get("component"),
                    "language": record.get("language"),
                    "framework": record.get("framework"),
                    "error_data": {"title": record.get("title")},
                    "solution_data": {
                        "choice": record.get("choice"),
                        "alternatives": record.get("alternatives", []),
                        "pros": record.get("pros", []),
                        "cons": record.get("cons", []),
                        "deciding_factor": record.get("deciding_factor"),
                    },
                    "verification_count": 1,
                    "contributor_hash": "local_sync",
                }

                with httpx.Client() as client:
                    resp = client.post(
                        f"{API_URL}/community_solutions",
                        headers=headers,
                        json=payload,
                        timeout=10.0,
                    )
                    if resp.status_code in (200, 201):
                        synced["decisions"] += 1
            except Exception:
                errors += 1

    # Sync patterns
    patterns_dir = data_dir / "patterns"
    if patterns_dir.exists():
        for f in patterns_dir.glob("*.json"):
            try:
                record = json.loads(f.read_text(encoding="utf-8"))

                import hashlib

                content = f"{record.get('name', '')[:100]}|{record.get('problem', '')[:100]}"
                content_hash = hashlib.md5(content.encode(), usedforsecurity=False).hexdigest()

                payload = {
                    "content_hash": content_hash,
                    "record_type": "pattern",
                    "category": record.get("category"),
                    "language": ",".join(record.get("languages", []))
                    if record.get("languages")
                    else None,
                    "framework": ",".join(record.get("frameworks", []))
                    if record.get("frameworks")
                    else None,
                    "error_data": {"name": record.get("name"), "problem": record.get("problem")},
                    "solution_data": {
                        "solution": record.get("solution"),
                        "before_code": record.get("before_code"),
                        "after_code": record.get("after_code"),
                        "explanation": record.get("explanation"),
                    },
                    "verification_count": 1,
                    "contributor_hash": "local_sync",
                }

                with httpx.Client() as client:
                    resp = client.post(
                        f"{API_URL}/community_solutions",
                        headers=headers,
                        json=payload,
                        timeout=10.0,
                    )
                    if resp.status_code in (200, 201):
                        synced["patterns"] += 1
            except Exception:
                errors += 1

    print("\n✅ Sync complete!")
    print(f"   Fixes synced:     {synced['fixes']}")
    print(f"   Decisions synced: {synced['decisions']}")
    print(f"   Patterns synced:  {synced['patterns']}")
    if errors > 0:
        print(f"   Errors:           {errors}")
    print()
    return 0


def cmd_setup_claude(args: argparse.Namespace) -> int:
    """Configure vault404 for Claude Code with auto-allow permissions."""
    from pathlib import Path

    # All vault404 MCP tools that need auto-allow permissions
    VAULT404_TOOLS = [
        "mcp__vault404__log_error_fix",
        "mcp__vault404__log_decision",
        "mcp__vault404__log_pattern",
        "mcp__vault404__find_solution",
        "mcp__vault404__find_decision",
        "mcp__vault404__find_pattern",
        "mcp__vault404__verify_solution",
        "mcp__vault404__agent_brain_stats",
    ]

    MCP_SERVER_CONFIG = {"command": "python", "args": ["-m", "vault404.mcp_server"]}

    def get_claude_config_dir() -> Path:
        if sys.platform == "win32":
            return Path.home() / ".claude"
        return Path.home() / ".claude"

    def load_json_file(path: Path) -> dict:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def save_json_file(path: Path, data: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    print("\n" + "=" * 50)
    print("  vault404 Setup for Claude Code")
    print("=" * 50 + "\n")

    config_dir = get_claude_config_dir()
    print(f"Config directory: {config_dir}\n")

    changes_made = False

    # Step 1: MCP Server
    print("[1/2] MCP Server Configuration")
    mcp_config_path = config_dir / "claude_desktop_config.json"
    mcp_config = load_json_file(mcp_config_path)

    if "mcpServers" not in mcp_config:
        mcp_config["mcpServers"] = {}

    if "vault404" not in mcp_config["mcpServers"]:
        mcp_config["mcpServers"]["vault404"] = MCP_SERVER_CONFIG
        save_json_file(mcp_config_path, mcp_config)
        print(f"  MCP server: Registered in {mcp_config_path}")
        changes_made = True
    else:
        print("  MCP server: Already configured")

    # Step 2: Permissions
    print("\n[2/2] Tool Permissions (Auto-Allow)")
    settings_path = config_dir / "settings.json"
    settings = load_json_file(settings_path)

    if "permissions" not in settings:
        settings["permissions"] = {}
    if "allow" not in settings["permissions"]:
        settings["permissions"]["allow"] = []

    existing = set(settings["permissions"]["allow"])
    missing = set(VAULT404_TOOLS) - existing

    if missing:
        settings["permissions"]["allow"].extend(sorted(missing))
        save_json_file(settings_path, settings)
        print(f"  Permissions: Added {len(missing)} tool(s) to {settings_path}")
        changes_made = True
    else:
        print("  Permissions: Already configured")

    # Summary
    print("\n" + "-" * 50)
    if changes_made:
        print("\n Setup complete!")
        print("\n IMPORTANT: Restart Claude Code for changes to take effect.\n")
        print("vault404 will now operate silently:")
        print("  - Searches happen automatically on errors")
        print("  - Fixes are logged without prompts")
        print("  - No permission dialogs will appear")
    else:
        print("\nvault404 is already configured. No changes needed.\n")

    print("=" * 50 + "\n")
    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="vault404",
        description="vault404: AI Coding Agent Memory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    vault404 setup-claude               Configure Claude Code (run this first!)
    vault404 stats                      Show statistics
    vault404 export ~/backup.json       Export data
    vault404 search "connection error"  Search solutions
    vault404 encrypt                    Enable encryption
    vault404 serve --port 8000          Start REST API server
    vault404 serve-mcp                  Start MCP server
        """,
    )

    parser.add_argument("--json", action="store_true", help="Output as JSON")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # setup-claude (FIRST - most important for new users)
    setup_claude_parser = subparsers.add_parser(
        "setup-claude", help="Configure Claude Code (MCP server + auto-allow permissions)"
    )
    setup_claude_parser.set_defaults(func=cmd_setup_claude)

    # sync - push local data to community brain
    sync_parser = subparsers.add_parser(
        "sync", help="Sync all verified local data to the Community Brain"
    )
    sync_parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    sync_parser.set_defaults(func=cmd_sync)

    # stats
    stats_parser = subparsers.add_parser("stats", help="Show knowledge base statistics")
    stats_parser.set_defaults(func=cmd_stats)

    # export
    export_parser = subparsers.add_parser("export", help="Export all data to JSON")
    export_parser.add_argument("output", nargs="?", help="Output file path")
    export_parser.set_defaults(func=cmd_export)

    # purge
    purge_parser = subparsers.add_parser("purge", help="Delete all data")
    purge_parser.add_argument("--confirm", action="store_true", help="Skip confirmation prompt")
    purge_parser.set_defaults(func=cmd_purge)

    # search
    search_parser = subparsers.add_parser("search", help="Search knowledge base")
    search_parser.add_argument("query", nargs="+", help="Search query")
    search_parser.add_argument(
        "--type",
        "-t",
        choices=["solution", "decision", "pattern", "all"],
        default="all",
        help="Type of record to search",
    )
    search_parser.add_argument("--limit", "-n", type=int, default=5, help="Max results")
    search_parser.set_defaults(func=cmd_search)

    # encrypt
    encrypt_parser = subparsers.add_parser("encrypt", help="Enable encryption")
    encrypt_parser.add_argument("--password", "-p", help="Encryption password")
    encrypt_parser.set_defaults(func=cmd_encrypt)

    # serve (REST API)
    serve_parser = subparsers.add_parser("serve", help="Start REST API server")
    serve_parser.add_argument(
        "--host",
        "-H",
        default="0.0.0.0",  # nosec B104 - intentional for development server
        help="Host to bind to (default: 0.0.0.0)",
    )
    serve_parser.add_argument(
        "--port", "-p", type=int, default=8000, help="Port to listen on (default: 8000)"
    )
    serve_parser.add_argument(
        "--reload", "-r", action="store_true", help="Enable auto-reload for development"
    )
    serve_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    serve_parser.set_defaults(func=cmd_serve)

    # serve-mcp (MCP server)
    serve_mcp_parser = subparsers.add_parser("serve-mcp", help="Start MCP server")
    serve_mcp_parser.set_defaults(func=cmd_serve_mcp)

    # recall (recall metrics)
    recall_parser = subparsers.add_parser("recall", help="View recall metrics")
    recall_parser.add_argument("--json", action="store_true", help="Output as JSON")
    recall_parser.add_argument("--export", "-e", help="Export metrics to file")
    recall_parser.add_argument("--weeks", "-w", type=int, default=4, help="Weeks of drift data")
    recall_parser.add_argument("--version", "-v", help="Filter by context version")
    recall_parser.set_defaults(func=cmd_recall)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
