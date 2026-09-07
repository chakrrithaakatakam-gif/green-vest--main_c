from typing import List, Optional
from pydantic import BaseModel, Field


class FinancialAssumptions(BaseModel):
    """Configurable financial parameters (clearly labeled as assumptions)."""
    capex_establishment_usd_ha: float = Field(..., description="Initial establishment & planting cost ($/ha)")
    opex_annual_usd_ha: float = Field(..., description="Annual maintenance, pruning, monitoring cost ($/ha)")
    yield_revenue_annual_usd_ha: float = Field(..., description="Expected mature annual agricultural/timber yield ($/ha)")
    yield_start_year: int = Field(3, description="Year when harvest revenue commences")
    carbon_price_usd_tco2e: float = Field(20.0, description="Assumed voluntary carbon credit price ($/tCO2e)")
    discount_rate: float = Field(0.08, ge=0.0, le=0.30, description="Annual discount rate for DCF")
    buffer_pool_deduction_pct: float = Field(0.15, description="Carbon risk buffer deduction (15%)")
    is_assumption: bool = True


class AnnualCashFlow(BaseModel):
    """Detailed cash flow projection for a single year."""
    year: int
    capex_usd_ha: float
    opex_usd_ha: float
    yield_revenue_usd_ha: float
    carbon_revenue_usd_ha: float
    net_cash_flow_usd_ha: float
    discounted_cash_flow_usd_ha: float
    cumulative_cash_flow_usd_ha: float


class FinancialMetrics(BaseModel):
    """20-Year discounted cash flow investment returns."""
    time_horizon_years: int = 20
    npv_usd_ha: float = Field(..., description="Net Present Value ($/ha) at given discount rate")
    irr_pct: Optional[float] = Field(None, description="Internal Rate of Return (%)")
    roi_pct: float = Field(..., description="Return on Investment (%)")
    payback_period_years: Optional[float] = Field(None, description="Simple payback period in years")
    discounted_payback_years: Optional[float] = Field(None, description="Discounted payback period in years")
    total_net_cash_flow_usd_ha: float
    cash_flows: List[AnnualCashFlow]
    is_modeled_assumption: bool = True
    disclaimer: str = (
        "Financial model results are projections based on user assumptions and do not constitute guaranteed investment returns."
    )
