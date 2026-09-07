import pytest
import respx
import httpx
from app.providers.climate import OpenMeteoClimateProvider
from app.providers.soil import SoilGridsProvider
from app.services.land_service import LandService


@pytest.mark.asyncio
async def test_soilgrids_success():
    provider = SoilGridsProvider()
    
    mock_soil_response = {
        "properties": {
            "layers": [
                {
                    "name": "phh2o",
                    "depths": [
                        {"values": {"mean": 62}},
                        {"values": {"mean": 65}},
                        {"values": {"mean": 68}}
                    ]
                }
            ]
        }
    }

    with respx.mock(assert_all_called=False) as respx_mock:
        respx_mock.get(url__regex=r"https://rest\.isric\.org/soilgrids/.*").mock(
            return_value=httpx.Response(200, json=mock_soil_response)
        )
        soil = await provider.get_soil(12.34, 56.78)
        assert soil.status == "available"
        assert soil.ph == 6.5  # Mean of (62, 65, 68) / 10 = 65 / 10 = 6.5
        assert soil.confidence_score == 0.90


@pytest.mark.asyncio
async def test_soilgrids_ocean_or_error_unavailable():
    provider = SoilGridsProvider()

    # Empty layers or 404
    with respx.mock(assert_all_called=False) as respx_mock:
        respx_mock.get(url__regex=r"https://rest\.isric\.org/soilgrids/.*").mock(
            return_value=httpx.Response(404, text="Out of bounds")
        )
        soil = await provider.get_soil(0.0, 0.0)
        assert soil.status == "unavailable"
        assert soil.ph is None
        assert soil.confidence_score == 0.0
        assert "unavailable" in soil.error_message.lower()


@pytest.mark.asyncio
async def test_climate_provider_success():
    provider = OpenMeteoClimateProvider()

    mock_climate_response = {
        "daily": {
            "precipitation_sum": [10.0, 20.0, 30.0],
            "temperature_2m_mean": [25.0, 27.0, 26.0],
            "temperature_2m_min": [18.0, 19.0, 20.0],
            "temperature_2m_max": [32.0, 34.0, 33.0]
        }
    }

    with respx.mock(assert_all_called=False) as respx_mock:
        respx_mock.get(url__regex=r"https://archive-api\.open-meteo\.com/.*").mock(
            return_value=httpx.Response(200, json=mock_climate_response)
        )
        climate = await provider.get_climate(11.11, 22.22)
        assert climate.status == "available"
        assert climate.annual_rainfall_mm == 60.0
        assert climate.mean_temperature_c == 26.0
        assert climate.min_temperature_c == 18.0
        assert climate.max_temperature_c == 34.0


@pytest.mark.asyncio
async def test_land_service_aggregation():
    mock_soil = {
        "properties": {
            "layers": [
                {"name": "phh2o", "depths": [{"values": {"mean": 70}}]}
            ]
        }
    }
    mock_climate = {
        "daily": {
            "precipitation_sum": [100.0],
            "temperature_2m_mean": [25.0],
            "temperature_2m_min": [20.0],
            "temperature_2m_max": [30.0]
        }
    }

    with respx.mock(assert_all_called=False) as respx_mock:
        respx_mock.get(url__regex=r"https://rest\.isric\.org/soilgrids/.*").mock(
            return_value=httpx.Response(200, json=mock_soil)
        )
        respx_mock.get(url__regex=r"https://archive-api\.open-meteo\.com/.*").mock(
            return_value=httpx.Response(200, json=mock_climate)
        )
        service = LandService()
        profile = await service.get_land_profile(15.55, 75.55)
        assert profile.climate.status == "available"
        assert profile.soil.status == "available"
        assert profile.composite_data_confidence > 0.8
