"""
API Key Authentication for vault404 REST API.

Write operations (log endpoints) require API key authentication.
Read operations (search endpoints) are public.
"""

import os
import secrets
import hashlib
from typing import Optional
from pathlib import Path

from fastapi import HTTPException, Security, Request
from fastapi.security import APIKeyHeader


# API key header name
API_KEY_HEADER = "X-API-Key"

# Environment variable for master API key (for admin operations)
MASTER_API_KEY_ENV = "VAULT404_MASTER_API_KEY"

# File storing valid API keys (hashed)
API_KEYS_FILE = Path.home() / ".vault404" / "api_keys.json"


# FastAPI security scheme
api_key_header = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)


def hash_api_key(key: str) -> str:
    """Hash an API key for secure storage."""
    return hashlib.sha256(key.encode()).hexdigest()


def generate_api_key() -> str:
    """Generate a new API key."""
    return f"v404_{secrets.token_urlsafe(32)}"


def get_master_key() -> Optional[str]:
    """Get the master API key from environment."""
    return os.environ.get(MASTER_API_KEY_ENV)


def load_api_keys() -> dict:
    """Load API keys from storage."""
    if not API_KEYS_FILE.exists():
        return {}

    import json
    try:
        return json.loads(API_KEYS_FILE.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, IOError):
        return {}


def save_api_keys(keys: dict) -> None:
    """Save API keys to storage."""
    import json
    API_KEYS_FILE.parent.mkdir(parents=True, exist_ok=True)
    API_KEYS_FILE.write_text(json.dumps(keys, indent=2), encoding='utf-8')


def register_api_key(name: str, key: Optional[str] = None) -> str:
    """
    Register a new API key.

    Args:
        name: A friendly name for this key (e.g., "my-agent")
        key: Optional pre-generated key. If None, generates a new one.

    Returns:
        The API key (only shown once!)
    """
    if key is None:
        key = generate_api_key()

    keys = load_api_keys()
    keys[hash_api_key(key)] = {
        "name": name,
        "created_at": __import__('datetime').datetime.now().isoformat(),
    }
    save_api_keys(keys)

    return key


def revoke_api_key(key: str) -> bool:
    """
    Revoke an API key.

    Args:
        key: The API key to revoke

    Returns:
        True if revoked, False if not found
    """
    keys = load_api_keys()
    key_hash = hash_api_key(key)

    if key_hash in keys:
        del keys[key_hash]
        save_api_keys(keys)
        return True

    return False


def validate_api_key(key: str) -> bool:
    """
    Validate an API key.

    Args:
        key: The API key to validate

    Returns:
        True if valid, False otherwise
    """
    if not key:
        return False

    # Check master key first
    master = get_master_key()
    if master and secrets.compare_digest(key, master):
        return True

    # Check registered keys
    keys = load_api_keys()
    return hash_api_key(key) in keys


async def require_api_key(
    request: Request,
    api_key: Optional[str] = Security(api_key_header),
) -> str:
    """
    Dependency that requires a valid API key.

    Use this for write operations (log endpoints).

    Raises:
        HTTPException 401 if no API key provided
        HTTPException 403 if API key is invalid
    """
    # Check if auth is disabled (for development)
    if os.environ.get("VAULT404_AUTH_DISABLED", "").lower() in ("true", "1", "yes"):
        return "auth_disabled"

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Set X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not validate_api_key(api_key):
        raise HTTPException(
            status_code=403,
            detail="Invalid API key",
        )

    return api_key


async def optional_api_key(
    api_key: Optional[str] = Security(api_key_header),
) -> Optional[str]:
    """
    Dependency that optionally validates API key.

    Use this for read operations that can optionally be authenticated
    for higher rate limits.
    """
    if api_key and validate_api_key(api_key):
        return api_key
    return None
