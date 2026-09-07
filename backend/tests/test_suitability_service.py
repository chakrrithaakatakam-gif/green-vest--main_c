import pytest
from app.models.domain.land import LandProfile, ClimateData, SoilData
from app.models.domain.plant import PlantRequirement
from app.services.suitability_service import suitability_engine


def make_test_land(rain: float, temp: float, ph: float) -> LandProfile:
    return LandProfile(
        latitude=12.0,
        longitude=76.0,
        climate=ClimateData(
            annual_rainfall_mm=rain,
            mean_temperature_c=temp,
            min_temperature_c=temp - 5,
            max_temperature_c=temp + 5,
            status="available",
        ),
        soil=SoilData(ph=ph, status="available"),
        composite_data_confidence=0.95,
    )


def test_stage1_hard_disqualification_low_rainfall():
    # Teak requires RMIN=800mm. Provide 400mm.
    land = make_test_land(rain=400.0, temp=25.0, ph=6.8)
    
    plant = PlantRequirement(
        crop_id=101,
        scientific_name="Tectona grandis",
        common_name="Teak",
        RMIN=800.0,
        ROPMN=1200.0,
        ROPMX=2500.0,
        RMAX=4000.0,
        TMIN=15.0,
        TOPMN=22.0,
        TOPMX=32.0,
        TMAX=44.0,
        PHMIN=5.0,
        PHOPMN=6.5,
        PHOPMX=7.5,
        PHMAX=8.5,
    )

    result = suitability_engine.evaluate_single_plant(land, plant)
    assert result.feasibility.is_feasible is False
    assert result.suitability is None
    assert len(result.feasibility.failure_reasons) == 1
    assert "below absolute survival minimum of 800.0mm" in result.feasibility.failure_reasons[0]


def test_stage2_optimal_plateau():
    # Ideal conditions for Teak
    land = make_test_land(rain=1800.0, temp=28.0, ph=7.0)
    
    plant = PlantRequirement(
        crop_id=101,
        scientific_name="Tectona grandis",
        common_name="Teak",
        RMIN=800.0,
        ROPMN=1200.0,
        ROPMX=2500.0,
        RMAX=4000.0,
        TMIN=15.0,
        TOPMN=22.0,
        TOPMX=32.0,
        TMAX=44.0,
        PHMIN=5.0,
        PHOPMN=6.5,
        PHOPMX=7.5,
        PHMAX=8.5,
    )

    result = suitability_engine.evaluate_single_plant(land, plant)
    assert result.feasibility.is_feasible is True
    assert result.suitability is not None
    assert result.suitability.environmental_score == 100.0
    assert result.suitability.data_completeness_pct == 100.0
    assert result.suitability.parameters["rainfall"].status == "optimal"
    assert result.suitability.parameters["rainfall"].sub_score == 1.0


def test_stage2_marginal_slope():
    # Marginal rainfall: RMIN=800, ROPMN=1200. Give 1000 -> (1000-800)/(1200-800) = 0.5
    land = make_test_land(rain=1000.0, temp=28.0, ph=7.0)
    
    plant = PlantRequirement(
        crop_id=101,
        scientific_name="Tectona grandis",
        common_name="Teak",
        RMIN=800.0,
        ROPMN=1200.0,
        ROPMX=2500.0,
        RMAX=4000.0,
        TMIN=15.0,
        TOPMN=22.0,
        TOPMX=32.0,
        TMAX=44.0,
        PHMIN=5.0,
        PHOPMN=6.5,
        PHOPMX=7.5,
        PHMAX=8.5,
    )

    result = suitability_engine.evaluate_single_plant(land, plant)
    assert result.feasibility.is_feasible is True
    rain_param = result.suitability.parameters["rainfall"]
    assert rain_param.status == "marginal"
    assert rain_param.sub_score == 0.5


def test_missing_optimal_bounds_policy():
    # Plant with missing optimal rainfall (ROPMN=None, ROPMX=None)
    land = make_test_land(rain=1200.0, temp=25.0, ph=6.8)

    plant = PlantRequirement(
        crop_id=999,
        scientific_name="Test species",
        common_name="Incomplete Data Plant",
        RMIN=500.0,
        ROPMN=None,
        ROPMX=None,
        RMAX=3000.0,
        TMIN=10.0,
        TOPMN=20.0,
        TOPMX=30.0,
        TMAX=40.0,
        PHMIN=5.0,
        PHOPMN=6.0,
        PHOPMX=7.5,
        PHMAX=8.5,
    )

    result = suitability_engine.evaluate_single_plant(land, plant)
    assert result.feasibility.is_feasible is True
    assert result.suitability is not None
    # 2 out of 3 parameters are evaluable: completeness should be 66.7%
    assert result.suitability.data_completeness_pct == 66.7
    assert result.suitability.parameters["rainfall"].status == "unevaluable"
    assert result.suitability.parameters["rainfall"].sub_score is None
    # Evaluated across temp (0.35) and pH (0.25), both are optimal (1.0) -> score is 100.0
    assert result.suitability.environmental_score == 100.0
