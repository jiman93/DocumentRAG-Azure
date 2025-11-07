"""
Health check endpoints
"""
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str


@router.get("", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
    )


@router.get("/ready")
async def readiness_check():
    """Readiness check - verify dependencies are available"""
    # Check if services are initialized
    # For now, just return ready
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/live")
async def liveness_check():
    """Liveness check - verify service is running"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }

