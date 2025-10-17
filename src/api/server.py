"""FastAPI server for OpsAgent API."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import structlog

logger = structlog.get_logger(__name__)


def create_app(config) -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Multi-Cloud OpsAgent",
        description="Intelligent AIOps for Kubernetes, AWS, and Azure",
        version="0.1.0",
    )

    @app.get("/")
    async def root():
        return {"status": "ok", "service": "ops-agent"}

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    @app.get("/metrics")
    async def metrics():
        # TODO: Return Prometheus metrics
        return JSONResponse(content={"metrics": "not_implemented"})

    logger.info("FastAPI application created")
    return app
