import pytest
from app.services.ecocrop_service import ecocrop_service


def test_list_plants():
    summaries, total = ecocrop_service.list_plants(limit=10)
    assert total >= 25
    assert len(summaries) == 10
    teak = next((s for s in summaries if "Teak" in s.common_name), None)
    if teak:
        assert teak.crop_id == 101
        assert "mm" in teak.rainfall_range


def test_get_plant_by_id():
    teak = ecocrop_service.get_plant_by_id(101)
    assert teak is not None
    assert teak.scientific_name == "Tectona grandis"
    assert teak.rainfall_min == 800.0
    assert teak.temp_min == 15.0
    assert teak.ph_min == 5.0
    assert teak.has_complete_optimal_ranges is True


def test_incomplete_optimal_ranges():
    melia = ecocrop_service.get_plant_by_id(126)
    assert melia is not None
    assert melia.common_name == "Malabar Neem"
    assert melia.rainfall_opt_min is None
    assert melia.has_complete_optimal_ranges is False


def test_filter_by_category():
    timber_plants, count = ecocrop_service.list_plants(category="Timber")
    assert count > 0
    assert all(p.use_category.lower() == "timber" for p in timber_plants)
