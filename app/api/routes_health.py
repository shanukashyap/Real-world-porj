"""Health and readiness for load balancers / K8s / Docker Compose."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready() -> dict[str, str]:
    """Optional: extend with DB ping when strict readiness is required."""
    return {"status": "ready"}
