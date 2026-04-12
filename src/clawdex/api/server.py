"""
FastAPI server for the Clawdex REST API.

Provides HTTP endpoints for the collective AI coding agent brain.
"""

import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import (
    solutions_router,
    decisions_router,
    patterns_router,
    stats_router,
    API_VERSION,
)


# Rate limiting (optional, requires slowapi)
RATE_LIMIT_ENABLED = os.environ.get("CLAWDEX_RATE_LIMIT", "").lower() in ("true", "1", "yes")

# CORS settings
CORS_ORIGINS = os.environ.get(
    "CLAWDEX_CORS_ORIGINS",
    "*"  # Default to allow all for development
).split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print(f"Clawdex API v{API_VERSION} starting...")
    yield
    # Shutdown
    print("Clawdex API shutting down...")


def create_app(
    title: str = "Clawdex API",
    description: str = "Collective AI Coding Agent Brain - REST API",
    cors_origins: Optional[list] = None,
    enable_rate_limiting: bool = False,
) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        title: API title for OpenAPI docs
        description: API description for OpenAPI docs
        cors_origins: List of allowed CORS origins
        enable_rate_limiting: Whether to enable rate limiting

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title=title,
        description=description,
        version=API_VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=[
            {
                "name": "solutions",
                "description": "Search and log error fixes",
            },
            {
                "name": "decisions",
                "description": "Search and log architectural decisions",
            },
            {
                "name": "patterns",
                "description": "Search and log reusable patterns",
            },
            {
                "name": "stats",
                "description": "Statistics and health checks",
            },
        ],
    )

    # Add CORS middleware
    origins = cors_origins or CORS_ORIGINS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Optional rate limiting
    if enable_rate_limiting or RATE_LIMIT_ENABLED:
        try:
            from slowapi import Limiter, _rate_limit_exceeded_handler
            from slowapi.util import get_remote_address
            from slowapi.errors import RateLimitExceeded

            limiter = Limiter(key_func=get_remote_address)
            app.state.limiter = limiter
            app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
            print("Rate limiting enabled")
        except ImportError:
            print("Warning: slowapi not installed, rate limiting disabled")

    # Include routers under /api/v1
    app.include_router(solutions_router, prefix="/api/v1")
    app.include_router(decisions_router, prefix="/api/v1")
    app.include_router(patterns_router, prefix="/api/v1")
    app.include_router(stats_router, prefix="/api/v1")

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "Clawdex API",
            "description": "Collective AI Coding Agent Brain",
            "version": API_VERSION,
            "docs": "/docs",
            "health": "/api/v1/health",
        }

    return app


# Create default app instance
app = create_app()


def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    log_level: str = "info",
):
    """
    Run the API server.

    Args:
        host: Host to bind to
        port: Port to listen on
        reload: Enable auto-reload for development
        log_level: Logging level
    """
    try:
        import uvicorn
    except ImportError:
        print("Error: uvicorn is required to run the server")
        print("Install it with: pip install uvicorn")
        return

    uvicorn.run(
        "clawdex.api.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
    )


if __name__ == "__main__":
    run_server()
