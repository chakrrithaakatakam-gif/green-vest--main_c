import pytest
import respx
import httpx
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_full_plan_optimization_e2e():
    transport = ASGITransport(app=app)

    mock_soil = {
        "properties": {
            "layers": [
                {
                    "name": "phh2o",
                    "depths": [
                        {"values": {"mean": 65}},
                        {"values": {"mean": 68}}
                    ]
                }
            ]
        }
    }
    mock_climate = {
        "daily": {
            "precipitation_sum": [150.0] * 10,  # 1500 mm
            "temperature_2m_mean": [26.0] * 10,  # 26 °C
            "temperature_2m_min": [20.0] * 10,
            "temperature_2m_max": [32.0] * 10
        }
    }

    with respx.mock(assert_all_called=False) as respx_mock:
        respx_mock.get(url__regex=r"https://rest\.isric\.org/soilgrids/.*").mock(
            return_value=httpx.Response(200, json=mock_soil)
        )
        respx_mock.get(url__regex=r"https://archive-api\.open-meteo\.com/.*").mock(
            return_value=httpx.Response(200, json=mock_climate)
        )

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Test Land Profile API
            land_res = await client.post("/api/v1/land/profile", json={"latitude": 10.5, "longitude": 76.2})
            assert land_res.status_code == 200
            land_data = land_res.json()["profile"]
            assert land_data["climate"]["annual_rainfall_mm"] == 1500.0
            assert land_data["soil"]["ph"] == 6.65

            # 2. Test Plants API
            plants_res = await client.get("/api/v1/plants?limit=10")
            assert plants_res.status_code == 200
            assert plants_res.json()["total_count"] >= 25

            # 3. Test Suitability Evaluation API
            suit_res = await client.post(
                "/api/v1/suitability/evaluate",
                json={"land_profile": land_data, "top_k": 5}
            )
            assert suit_res.status_code == 200
            suit_json = suit_res.json()
            assert suit_json["total_feasible"] > 0
            assert len(suit_json["feasible_plants"]) <= 5

            # 4. Test Plan Optimization API (Balanced Mode)
            plan_res = await client.post(
                "/api/v1/plan/optimize",
                json={
                    "latitude": 10.5,
                    "longitude": 76.2,
                    "investor_mode": "balanced",
                    "scenario": "expected",
                    "area_hectares": 5.0,
                    "top_k": 5
                }
            )
            assert plan_res.status_code == 200
            plan = plan_res.json()["plan"]
            assert plan["investor_mode"] == "balanced"
            assert len(plan["ranked_strategies"]) > 0
            
            top_strat = plan["ranked_strategies"][0]
            assert top_strat["rank"] == 1
            assert 0.0 <= top_strat["greenvest_score"] <= 100.0
            assert top_strat["carbon_projection"] is not None
            assert top_strat["financial_metrics"] is not None
            assert len(top_strat["audit_trail"]["strengths"]) > 0

            # 5. Test Carbon-First Mode
            carbon_plan_res = await client.post(
                "/api/v1/plan/optimize",
                json={
                    "latitude": 10.5,
                    "longitude": 76.2,
                    "investor_mode": "carbon_first",
                    "scenario": "expected",
                    "area_hectares": 5.0,
                    "top_k": 5
                }
            )
            assert carbon_plan_res.status_code == 200
            carbon_plan = carbon_plan_res.json()["plan"]
            assert carbon_plan["investor_mode"] == "carbon_first"
