"""
ISRIC SoilGrids v2.0 Provider.
Queries ISRIC SoilGrids REST API for topsoil pH (0-30cm depth).
Strict resilience: returns status='unavailable' with ph=None upon error or out-of-bounds. Zero fabricated fallbacks!
"""

import logging
import httpx
from app.config import settings
from app.models.domain.land import SoilData
from app.providers.cache import spatial_cache

logger = logging.getLogger("greenvest.soil")


class SoilGridsProvider:
    """Soil chemical properties provider querying ISRIC SoilGrids v2.0."""

    def __init__(self):
        self.base_url = settings.SOILGRIDS_BASE_URL
        self.timeout = settings.PROVIDER_TIMEOUT_SECONDS
        self.max_retries = settings.PROVIDER_MAX_RETRIES

    async def get_soil(self, lat: float, lon: float) -> SoilData:
        """Fetch topsoil pH (0-30cm) for coordinate. Strict zero-fallback handling."""
        # 1. Check spatial quantization cache
        cached = spatial_cache.get("soil", lat, lon)
        if cached:
            logger.debug("Soil cache hit for (%s, %s)", lat, lon)
            return SoilData.model_validate(cached)

        # 2. Query SoilGrids REST API
        # SoilGrids expects: lon, lat, property="phh2o", depth=["0-5cm", "5-15cm", "15-30cm"], value="mean"
        params = [
            ("lat", str(lat)),
            ("lon", str(lon)),
            ("property", "phh2o"),
            ("depth", "0-5cm"),
            ("depth", "5-15cm"),
            ("depth", "15-30cm"),
            ("value", "mean"),
        ]

        last_error = None
        for attempt in range(1, self.max_retries + 2):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(self.base_url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        properties = data.get("properties", {})
                        layers = properties.get("layers", [])
                        
                        ph_values = []
                        for layer in layers:
                            if layer.get("name") == "phh2o":
                                depths = layer.get("depths", [])
                                for d in depths:
                                    values = d.get("values", {})
                                    mean_val = values.get("mean")
                                    if mean_val is not None:
                                        ph_values.append(mean_val)

                        # If no valid soil layer returned (e.g. oceanic coordinates or water bodies)
                        if not ph_values:
                            logger.info("SoilGrids out of bounds/ocean coordinate for (%s, %s)", lat, lon)
                            return SoilData(
                                ph=None,
                                source="ISRIC SoilGrids v2.0 (0-30cm)",
                                status="unavailable",
                                confidence_score=0.0,
                                error_message="SoilGrids API unavailable or coordinate out of bounds"
                            )

                        # SoilGrids represents pH * 10 (e.g., 65 = 6.5 pH)
                        avg_ph = round((sum(ph_values) / len(ph_values)) / 10.0, 2)
                        
                        # Sanity check within 0-14 pH
                        if not (0.0 <= avg_ph <= 14.0):
                            return SoilData(
                                ph=None,
                                source="ISRIC SoilGrids v2.0 (0-30cm)",
                                status="unavailable",
                                confidence_score=0.0,
                                error_message=f"SoilGrids returned out-of-range pH value: {avg_ph}"
                            )

                        result = SoilData(
                            ph=avg_ph,
                            source="ISRIC SoilGrids v2.0 (0-30cm)",
                            status="available",
                            confidence_score=0.90,
                            error_message=None
                        )

                        # Cache successful result
                        spatial_cache.set("soil", lat, lon, result.model_dump())
                        return result
                    else:
                        last_error = f"SoilGrids API unavailable or coordinate out of bounds (HTTP {response.status_code})"
            except (httpx.TimeoutException, httpx.RequestError) as exc:
                last_error = f"SoilGrids API unavailable or coordinate out of bounds: {str(exc)}"
                logger.warning(last_error)

        # 3. Transparent unavailable response (Strict Zero Fabricated Fallbacks)
        return SoilData(
            ph=None,
            source="ISRIC SoilGrids v2.0 (0-30cm)",
            status="unavailable",
            confidence_score=0.0,
            error_message=last_error or "SoilGrids API unavailable or coordinate out of bounds"
        )


soil_provider = SoilGridsProvider()
