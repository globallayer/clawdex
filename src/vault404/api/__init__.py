"""
Vault404 REST API

FastAPI-based REST API server for the Vault404 collective AI coding agent brain.
Provides HTTP endpoints for searching and logging solutions, decisions, and patterns.

Authentication:
    Write operations (log/verify) require API key authentication.
    Set X-API-Key header with a valid key.

Rate Limiting:
    - Search endpoints: 60 req/min (unauthenticated), 120 req/min (authenticated)
    - Write endpoints: 20 req/min
"""

from .server import app, create_app, run_server
from .auth import (
    generate_api_key,
    register_api_key,
    revoke_api_key,
    validate_api_key,
    require_api_key,
    optional_api_key,
)

__all__ = [
    # Server
    "app",
    "create_app",
    "run_server",
    # Auth
    "generate_api_key",
    "register_api_key",
    "revoke_api_key",
    "validate_api_key",
    "require_api_key",
    "optional_api_key",
]
