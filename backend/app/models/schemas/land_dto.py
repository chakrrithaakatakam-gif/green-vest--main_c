from typing import Optional
from pydantic import BaseModel, Field
from app.models.domain.land import LandProfile


class LandProfileRequest(BaseModel):
    """Request payload to acquire a Land Profile."""
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")


class LandProfileResponse(BaseModel):
    """Audited response containing physical land parameters."""
    profile: LandProfile
    message: str = "Land profile acquired successfully"
