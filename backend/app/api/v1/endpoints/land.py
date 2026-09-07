"""
Land Profile API Endpoint.
Acquires real-time physical environmental telemetry (Rainfall, Temp, Soil pH).
"""

from fastapi import APIRouter
from app.models.schemas.land_dto import LandProfileRequest, LandProfileResponse
from app.services.land_service import land_service

router = APIRouter(tags=["Land"])


@router.post("/land/profile", response_model=LandProfileResponse)
async def acquire_land_profile(request: LandProfileRequest):
    """
    Acquire Canonical Land Profile for given coordinates.
    Concurrently streams Open-Meteo climate reanalysis and ISRIC SoilGrids pH.
    """
    profile = await land_service.get_land_profile(request.latitude, request.longitude)
    return LandProfileResponse(
        profile=profile,
        message="Canonical land profile acquired successfully."
    )
