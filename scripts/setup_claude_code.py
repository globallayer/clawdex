#!/usr/bin/env python3
"""
vault404 Setup Script for Claude Code

Automatically configures:
1. MCP server registration
2. Tool permissions (auto-allow for silent operation)

Usage:
    python -m vault404.setup_claude
    # or
    vault404 setup-claude
"""

import json
import os
import sys
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

MCP_SERVER_CONFIG = {
    "command": "python",
    "args": ["-m", "vault404.mcp_server"]
}


def get_claude_config_dir() -> Path:
    """Get Claude Code config directory based on OS."""
    if sys.platform == "win32":
        # Windows: C:\Users\<user>\.claude
        return Path.home() / ".claude"
    elif sys.platform == "darwin":
        # macOS: ~/.claude
        return Path.home() / ".claude"
    else:
        # Linux: ~/.claude
        return Path.home() / ".claude"


def get_claude_mcp_config_path() -> Path:
    """Get the MCP servers config file path."""
    config_dir = get_claude_config_dir()
    # Claude Code uses claude_desktop_config.json for MCP servers
    return config_dir / "claude_desktop_config.json"


def get_claude_settings_path() -> Path:
    """Get the settings.json file path."""
    return get_claude_config_dir() / "settings.json"


def load_json_file(path: Path) -> dict:
    """Load JSON file, return empty dict if doesn't exist."""
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_json_file(path: Path, data: dict) -> None:
    """Save JSON file with pretty formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"  Updated: {path}")


def setup_mcp_server() -> bool:
    """Register vault404 as MCP server."""
    config_path = get_claude_mcp_config_path()
    config = load_json_file(config_path)

    if "mcpServers" not in config:
        config["mcpServers"] = {}

    if "vault404" in config["mcpServers"]:
        print("  MCP server: Already configured")
        return False

    config["mcpServers"]["vault404"] = MCP_SERVER_CONFIG
    save_json_file(config_path, config)
    print("  MCP server: Registered")
    return True


def setup_permissions() -> bool:
    """Add vault404 tools to auto-allow permissions."""
    settings_path = get_claude_settings_path()
    settings = load_json_file(settings_path)

    if "permissions" not in settings:
        settings["permissions"] = {}

    if "allow" not in settings["permissions"]:
        settings["permissions"]["allow"] = []

    existing = set(settings["permissions"]["allow"])
    needed = set(VAULT404_TOOLS)
    missing = needed - existing

    if not missing:
        print("  Permissions: Already configured")
        return False

    settings["permissions"]["allow"].extend(sorted(missing))
    save_json_file(settings_path, settings)
    print(f"  Permissions: Added {len(missing)} tool(s)")
    return True


def main():
    """Main setup function."""
    print("\n" + "=" * 50)
    print("  vault404 Setup for Claude Code")
    print("=" * 50 + "\n")

    config_dir = get_claude_config_dir()
    print(f"Config directory: {config_dir}\n")

    changes_made = False

    # Step 1: MCP Server
    print("[1/2] MCP Server Configuration")
    if setup_mcp_server():
        changes_made = True

    # Step 2: Permissions
    print("\n[2/2] Tool Permissions (Auto-Allow)")
    if setup_permissions():
        changes_made = True

    # Summary
    print("\n" + "-" * 50)
    if changes_made:
        print("\nSetup complete! Please restart Claude Code for changes to take effect.\n")
        print("vault404 will now operate silently:")
        print("  - Searches happen automatically on errors")
        print("  - Fixes are logged without prompts")
        print("  - No permission dialogs will appear")
    else:
        print("\nvault404 is already configured. No changes needed.\n")

    print("=" * 50 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
