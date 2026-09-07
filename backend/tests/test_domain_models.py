import pytest
from app.models.domain.land import Coordinate, ClimateData, SoilData, LandProfile
from app.models.domain.plant import PlantRequirement, PlantSummary
from app.models.domain.carbon import PlantCarbonProfile, CarbonProjection, CarbonYearPoint
from app.models.domain.suitability import ParameterSuitability, FeasibilityResult, SuitabilityScore
from app.models.domain.financial import FinancialAssumptions, AnnualCashFlow, FinancialMetrics


def test_coordinate_validation():
    coord = Coordinate(latitude=12.9716, longitude=80.2209)
    assert coord.latitude == 12.9716
    assert coord.longitude == 80.2209

    with pytest.raises(Exception):
        Coordinate(latitude=100.0, longitude=0.0)


def test_land_profile_creation():
    climate = ClimateData(
        annual_rainfall_mm=1320.0,
        mean_temperature_c=28.1,
        min_temperature_c=21.4,
        max_temperature_c=34.8,
        status="available"
    )
    soil = SoilData(ph=6.7, status="available")
    profile = LandProfile(
        latitude=12.9716,
        longitude=80.2209,
        climate=climate,
        soil=soil,
        composite_data_confidence=0.92
    )

    assert profile.climate.annual_rainfall_mm == 1320.0
    assert profile.soil.ph == 6.7
    assert profile.composite_data_confidence == 0.92


def test_land_profile_unavailable_state():
    climate = ClimateData(annual_rainfall_mm=None, status="unavailable", confidence_score=0.0)
    soil = SoilData(ph=None, status="unavailable", confidence_score=0.0)
    profile = LandProfile(
        latitude=0.0,
        longitude=0.0,
        climate=climate,
        soil=soil,
        composite_data_confidence=0.0
    )

    assert profile.climate.annual_rainfall_mm is None
    assert profile.climate.status == "unavailable"
    assert profile.soil.ph is None
    assert profile.soil.status == "unavailable"


def test_plant_requirement_alias_mapping():
    raw_ecocrop = {
        "crop_id": 101,
        "scientific_name": "Tectona grandis",
        "common_name": "Teak",
        "RMIN": 800.0,
        "ROPMN": 1200.0,
        "ROPMX": 2500.0,
        "RMAX": 4000.0,
        "TMIN": 15.0,
        "TOPMN": 22.0,
        "TOPMX": 32.0,
        "TMAX": 42.0,
        "PHMIN": 5.5,
        "PHOPMN": 6.5,
        "PHOPMX": 7.5,
        "PHMAX": 8.5,
        "USE": "Timber"
    }

    plant = PlantRequirement.model_validate(raw_ecocrop)
    assert plant.scientific_name == "Tectona grandis"
    assert plant.rainfall_min == 800.0
    assert plant.rainfall_opt_min == 1200.0
    assert plant.rainfall_opt_max == 2500.0
    assert plant.rainfall_max == 4000.0
    assert plant.temp_min == 15.0
    assert plant.ph_min == 5.5
    assert plant.has_complete_optimal_ranges is True


def test_plant_carbon_profile_assumptions():
    carbon_profile = PlantCarbonProfile(
        crop_id=101,
        scientific_name="Tectona grandis",
        common_name="Teak",
        max_above_ground_biomass_t_ha=220.0,
        growth_rate_k=0.18,
        inflection_year_t0=7.0,
        root_to_shoot_ratio=0.24,
        carbon_fraction=0.47,
        data_source="FAO Forestry Paper 177",
        is_assumption=True,
        confidence_rating=0.80
    )

    assert carbon_profile.is_assumption is True
    assert carbon_profile.root_to_shoot_ratio == 0.24
    assert carbon_profile.carbon_fraction == 0.47
