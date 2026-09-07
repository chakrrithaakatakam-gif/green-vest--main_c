"""
Open-Meteo Historical Climate Reanalysis Provider.
Queries Open-Meteo archive API for annual rainfall and temperature metrics.
"""

import logging
import httpx
from app.config import settings
from app.models.domain.land import ClimateData
from app.providers.cache import spatial_cache

logger = logging.getLogger("greenvest.climate")


class OpenMeteoClimateProvider:
    """Historical climate provider utilizing Open-Meteo Reanalysis API."""

    def __init__(self):
        self.base_url = settings.OPEN_METEO_BASE_URL
        self.timeout = settings.PROVIDER_TIMEOUT_SECONDS
        self.max_retries = settings.PROVIDER_MAX_RETRIES

    async def get_climate(self, lat: float, lon: float) -> ClimateData:
        """Fetch historical annual rainfall and temperature averages for a coordinate."""
        # 1. Check spatial quantization cache
        cached = spatial_cache.get("climate", lat, lon)
        if cached:
            logger.debug("Climate cache hit for (%s, %s)", lat, lon)
            return ClimateData.model_validate(cached)

        # 2. Query Open-Meteo Archive API
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "daily": [
                "precipitation_sum",
                "temperature_2m_mean",
                "temperature_2m_min",
                "temperature_2m_max"
            ],
            "timezone": "auto"
        }

        last_error = None
        for attempt in range(1, self.max_retries + 2):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(self.base_url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        daily = data.get("daily", {})
                        precip_list = [p for p in daily.get("precipitation_sum", []) if p is not None]
                        temp_mean_list = [t for t in daily.get("temperature_2m_mean", []) if t is not None]
                        temp_min_list = [t for t in daily.get("temperature_2m_min", []) if t is not None]
                        temp_max_list = [t for t in daily.get("temperature_2m_max", []) if t is not None]

                        if not precip_list or not temp_mean_list:
                            return ClimateData(
                                annual_rainfall_mm=None,
                                mean_temperature_c=None,
                                min_temperature_c=None,
                                max_temperature_c=None,
                                status="unavailable",
                                confidence_score=0.0,
                                error_message="Open-Meteo returned empty historical timeseries"
                            )

                        annual_rainfall = round(sum(precip_list), 1)
                        mean_temp = round(sum(temp_mean_list) / len(temp_mean_list), 1)
                        # Mean monthly or minimum of daily minimums
                        min_temp = round(min(temp_min_list), 1)
                        max_temp = round(max(temp_max_list), 1)

                        result = ClimateData(
                            annual_rainfall_mm=annual_rainfall,
                            mean_temperature_c=mean_temp,
                            min_temperature_c=min_temp,
                            max_temperature_c=max_temp,
                            source="Open-Meteo Historical Climate Reanalysis",
                            status="available",
                            confidence_score=0.95,
                            error_message=None
                        )

                        # Cache successful result
                        spatial_cache.set("climate", lat, lon, result.model_dump())
                        return result
                    else:
                        last_error = f"Open-Meteo HTTP {response.status_code}: {response.text[:200]}"
            except (httpx.TimeoutException, httpx.RequestError) as exc:
                last_error = f"Climate network error (attempt {attempt}): {str(exc)}"
                logger.warning(last_error)

        # 3. Transparent unavailable response (Zero fabricated data)
        return ClimateData(
            annual_rainfall_mm=None,
            mean_temperature_c=None,
            min_temperature_c=None,
            max_temperature_c=None,
            source="Open-Meteo Historical Climate Reanalysis",
            status="unavailable",
            confidence_score=0.0,
            error_message=last_error or "Open-Meteo API unreachable after retries"
        )


climate_provider = OpenMeteoClimateProvider()
