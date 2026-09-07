import pytest
from app.services.carbon_service import carbon_service
from app.services.financial_service import financial_service
from app.models.domain.financial import FinancialAssumptions


def test_carbon_projection_monotonic_accumulation():
    projection = carbon_service.calculate_projection(
        crop_id=101,
        scientific_name="Tectona grandis",
        common_name="Teak",
        horizon_years=20,
    )

    assert projection.time_horizon_years == 20
    assert projection.cumulative_20yr_co2e_t_ha > 100.0
    assert len(projection.trajectory) == 20
    assert "Estimated Biophysical Carbon Sequestration" in projection.disclaimer

    # Check monotonic increase of cumulative CO2e
    for i in range(1, len(projection.trajectory)):
        prev = projection.trajectory[i - 1].cumulative_co2e_t_ha
        curr = projection.trajectory[i].cumulative_co2e_t_ha
        assert curr >= prev
        # Annual increment should be positive
        assert projection.trajectory[i].annual_co2e_increment_t_ha >= 0.0


def test_financial_dcf_cash_flows_and_metrics():
    projection = carbon_service.calculate_projection(
        crop_id=101,
        scientific_name="Tectona grandis",
        common_name="Teak",
        horizon_years=20,
    )

    assumptions = FinancialAssumptions(
        capex_establishment_usd_ha=2500.0,
        opex_annual_usd_ha=350.0,
        yield_revenue_annual_usd_ha=2000.0,
        yield_start_year=5,
        carbon_price_usd_tco2e=25.0,
        discount_rate=0.08,
        buffer_pool_deduction_pct=0.15,
    )

    metrics = financial_service.calculate_dcf(projection, assumptions, horizon_years=20)

    assert metrics.time_horizon_years == 20
    assert len(metrics.cash_flows) == 21  # Year 0 through 20
    assert metrics.cash_flows[0].year == 0
    assert metrics.cash_flows[0].capex_usd_ha == 2500.0
    assert metrics.cash_flows[0].net_cash_flow_usd_ha == -2500.0

    # Year 1: No yield yet (commences at year 5), but positive carbon revenue
    assert metrics.cash_flows[1].yield_revenue_usd_ha == 0.0
    assert metrics.cash_flows[1].carbon_revenue_usd_ha > 0.0

    # Year 5: Yield revenue commenced
    assert metrics.cash_flows[5].yield_revenue_usd_ha == 2000.0

    # NPV should be positive for profitable plantation
    assert metrics.npv_usd_ha > 0.0
    assert metrics.roi_pct > 0.0
    assert metrics.irr_pct is not None
    assert metrics.payback_period_years is not None
    assert metrics.payback_period_years > 0.0
