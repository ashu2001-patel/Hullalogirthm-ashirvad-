"""Health check endpoints."""

from fastapi import APIRouter
from datetime import datetime
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """System health status."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow(),
        services={
            "api": "up",
            "database": "up",  # In-memory for Phase 1-3
            "cache": "up"
        }
    )


@router.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe."""
    return {"ready": True, "timestamp": datetime.utcnow().isoformat()}


@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"alive": True, "timestamp": datetime.utcnow().isoformat()}
