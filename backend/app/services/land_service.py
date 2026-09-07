"""
Land Service orchestrator.
Concurrently fetches climate telemetry and soil properties to build canonical LandProfile.
"""

import asyncio
from datetime import datetime, timezone
from typing import Optional
from app.models.domain.land import LandProfile
from app.providers.climate import climate_provider
from app.providers.soil import soil_provider


class LandService:
    """Orchestrates concurrent physical land telemetry acquisition."""

    def __init__(self, climate_prov=None, soil_prov=None):
        self.climate_provider = climate_prov or climate_provider
        self.soil_provider = soil_prov or soil_provider

    async def get_land_profile(self, lat: float, lon: float) -> LandProfile:
        """Fetch concurrent climate and soil profiles for coordinate."""
        climate_task = self.climate_provider.get_climate(lat, lon)
        soil_task = self.soil_provider.get_soil(lat, lon)

        climate_data, soil_data = await asyncio.gather(climate_task, soil_task)

        # Compute composite data confidence
        # Climate weighted 55%, Soil pH weighted 45%
        climate_conf = climate_data.confidence_score if climate_data.status == "available" else 0.0
        soil_conf = soil_data.confidence_score if soil_data.status == "available" else 0.0

        if climate_data.status == "available" and soil_data.status == "available":
            composite_confidence = round((climate_conf * 0.55) + (soil_conf * 0.45), 2)
        elif climate_data.status == "available":
            composite_confidence = round(climate_conf * 0.55, 2)
        elif soil_data.status == "available":
            composite_confidence = round(soil_conf * 0.45, 2)
        else:
            composite_confidence = 0.0

        return LandProfile(
            latitude=lat,
            longitude=lon,
            climate=climate_data,
            soil=soil_data,
            composite_data_confidence=composite_confidence,
            evaluated_at=datetime.now(timezone.utc).isoformat()
        )


land_service = LandService()
