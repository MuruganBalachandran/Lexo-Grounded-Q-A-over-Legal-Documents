from fastapi import APIRouter
from backend.api.schemas.qa import HealthResponse

router = APIRouter(tags=["Health"])

@router.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Service health check."""
    return HealthResponse()
