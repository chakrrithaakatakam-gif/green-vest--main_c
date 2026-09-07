from datetime import datetime, timezone
from fastapi import APIRouter
from app.config import settings

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify backend status, version, and active configurations."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "providers": {
            "climate": {
                "name": "Open-Meteo Historical Climate Reanalysis",
                "status": "configured",
                "base_url": settings.OPEN_METEO_BASE_URL
            },
            "soil": {
                "name": "ISRIC SoilGrids v2.0 (pH 0-30cm)",
                "status": "configured",
                "base_url": settings.SOILGRIDS_BASE_URL
            }
        },
        "environmental_weights": settings.ENV_WEIGHTS.model_dump(),
        "investor_modes": list(settings.INVESTOR_MODES.keys()),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
