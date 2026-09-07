"""
20-Year Discounted Cash Flow (DCF) Financial Service.
Models CAPEX establishment, annual OPEX, agricultural/timber yield, voluntary carbon revenue
(with 15% buffer pool deduction), NPV, IRR, ROI, and Payback Period.
"""

import os
import json
from typing import List, Optional, Dict
from app.config import settings
from app.models.domain.carbon import CarbonProjection
from app.models.domain.financial import (
    FinancialAssumptions,
    AnnualCashFlow,
    FinancialMetrics,
)


class FinancialService:
    """20-Year institutional agroforestry financial DCF modeling."""

    def __init__(self, defaults_path: Optional[str] = None):
        self._defaults_path = self._resolve_path(defaults_path or "data/strategies/financial_defaults.json")
        self._species_defaults: Dict[int, dict] = {}
        self._baseline_defaults: dict = {}
        self._load_defaults()

    @staticmethod
    def _resolve_path(path: str) -> str:
        if os.path.exists(path):
            return path
        backend_rel = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), path)
        if os.path.exists(backend_rel):
            return backend_rel
        workspace_rel = os.path.join(os.getcwd(), "backend", path)
        if os.path.exists(workspace_rel):
            return workspace_rel
        return path

    def _load_defaults(self):
        if not os.path.exists(self._defaults_path):
            return
        try:
            with open(self._defaults_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._baseline_defaults = data.get("defaults", {})
                for crop_id_str, spec in data.get("species", {}).items():
                    self._species_defaults[int(crop_id_str)] = spec
        except Exception:
            pass

    def get_default_assumptions(
        self,
        crop_id: int,
        custom_discount_rate: Optional[float] = None,
        custom_carbon_price: Optional[float] = None,
    ) -> FinancialAssumptions:
        """Construct financial assumptions for crop with optional user overrides."""
        spec = self._species_defaults.get(crop_id, {})
        base = self._baseline_defaults

        capex = spec.get("capex_establishment_usd_ha", base.get("default_capex_usd_ha", 2500.0))
        opex = spec.get("opex_annual_usd_ha", base.get("default_opex_usd_ha", 350.0))
        yield_rev = spec.get("yield_revenue_annual_usd_ha", base.get("default_yield_usd_ha", 1800.0))
        yield_start = spec.get("yield_start_year", base.get("default_yield_start_year", 4))

        discount_rate = custom_discount_rate if custom_discount_rate is not None else settings.DEFAULT_DISCOUNT_RATE
        carbon_price = custom_carbon_price if custom_carbon_price is not None else settings.DEFAULT_CARBON_PRICE_USD

        return FinancialAssumptions(
            capex_establishment_usd_ha=float(capex),
            opex_annual_usd_ha=float(opex),
            yield_revenue_annual_usd_ha=float(yield_rev),
            yield_start_year=int(yield_start),
            carbon_price_usd_tco2e=float(carbon_price),
            discount_rate=float(discount_rate),
            buffer_pool_deduction_pct=settings.DEFAULT_BUFFER_DISCOUNT_PCT,
            is_assumption=True,
        )

    def calculate_dcf(
        self,
        carbon_projection: CarbonProjection,
        assumptions: FinancialAssumptions,
        horizon_years: int = 20,
    ) -> FinancialMetrics:
        """Compute 20-year annual cash flows and institutional DCF investment returns."""
        cash_flows: List[AnnualCashFlow] = []
        r = assumptions.discount_rate
        net_cash_flow_series: List[float] = []
        discounted_cash_flow_series: List[float] = []

        # Year 0: Initial Capital Expenditure (CAPEX)
        year_0_net = -assumptions.capex_establishment_usd_ha
        net_cash_flow_series.append(year_0_net)
        discounted_cash_flow_series.append(year_0_net)

        cash_flows.append(
            AnnualCashFlow(
                year=0,
                capex_usd_ha=round(assumptions.capex_establishment_usd_ha, 2),
                opex_usd_ha=0.0,
                yield_revenue_usd_ha=0.0,
                carbon_revenue_usd_ha=0.0,
                net_cash_flow_usd_ha=round(year_0_net, 2),
                discounted_cash_flow_usd_ha=round(year_0_net, 2),
                cumulative_cash_flow_usd_ha=round(year_0_net, 2),
            )
        )

        running_cum_cash_flow = year_0_net
        running_cum_discounted = year_0_net
        payback_year: Optional[float] = None
        discounted_payback_year: Optional[float] = None

        # Build trajectory increment lookup: year -> annual increment tCO2e/ha
        inc_map = {pt.year: pt.annual_co2e_increment_t_ha for pt in carbon_projection.trajectory}

        for yr in range(1, horizon_years + 1):
            # Harvest yield commences at yield_start_year
            yield_rev = assumptions.yield_revenue_annual_usd_ha if yr >= assumptions.yield_start_year else 0.0

            # Carbon revenue with buffer deduction
            # Net tCO2e = annual_inc * (1 - buffer_pool_deduction_pct)
            annual_inc = inc_map.get(yr, 0.0)
            net_tco2e = annual_inc * (1.0 - assumptions.buffer_pool_deduction_pct)
            carbon_rev = net_tco2e * assumptions.carbon_price_usd_tco2e

            opex = assumptions.opex_annual_usd_ha
            net_cf = yield_rev + carbon_rev - opex
            discount_factor = (1.0 + r) ** yr
            dcf = net_cf / discount_factor if discount_factor > 0 else 0.0

            prev_cum = running_cum_cash_flow
            running_cum_cash_flow += net_cf

            prev_cum_disc = running_cum_discounted
            running_cum_discounted += dcf

            # Check simple payback
            if payback_year is None and running_cum_cash_flow >= 0.0 and prev_cum < 0.0:
                fraction = (-prev_cum) / net_cf if net_cf > 0 else 0.0
                payback_year = round((yr - 1) + fraction, 1)

            # Check discounted payback
            if discounted_payback_year is None and running_cum_discounted >= 0.0 and prev_cum_disc < 0.0:
                fraction = (-prev_cum_disc) / dcf if dcf > 0 else 0.0
                discounted_payback_year = round((yr - 1) + fraction, 1)

            net_cash_flow_series.append(net_cf)
            discounted_cash_flow_series.append(dcf)

            cash_flows.append(
                AnnualCashFlow(
                    year=yr,
                    capex_usd_ha=0.0,
                    opex_usd_ha=round(opex, 2),
                    yield_revenue_usd_ha=round(yield_rev, 2),
                    carbon_revenue_usd_ha=round(carbon_rev, 2),
                    net_cash_flow_usd_ha=round(net_cf, 2),
                    discounted_cash_flow_usd_ha=round(dcf, 2),
                    cumulative_cash_flow_usd_ha=round(running_cum_cash_flow, 2),
                )
            )

        # Calculate NPV
        npv = sum(discounted_cash_flow_series)

        # Calculate IRR
        irr = self._calculate_irr(net_cash_flow_series)

        # Calculate ROI %: (Total net cash flow / Total CAPEX) * 100
        capex_total = assumptions.capex_establishment_usd_ha
        total_net_cf = running_cum_cash_flow
        roi = round((total_net_cf / capex_total) * 100.0, 1) if capex_total > 0 else 0.0

        return FinancialMetrics(
            time_horizon_years=horizon_years,
            npv_usd_ha=round(npv, 2),
            irr_pct=round(irr * 100.0, 2) if irr is not None else None,
            roi_pct=roi,
            payback_period_years=payback_year,
            discounted_payback_years=discounted_payback_year,
            total_net_cash_flow_usd_ha=round(total_net_cf, 2),
            cash_flows=cash_flows,
            is_modeled_assumption=True,
            disclaimer=(
                "Financial model results are projections based on user assumptions "
                "and do not constitute guaranteed investment returns."
            ),
        )

    @staticmethod
    def _calculate_irr(cash_flows: List[float], max_iter: int = 100) -> Optional[float]:
        """Robust Internal Rate of Return (IRR) calculation using hybrid secant/bisection method."""
        if not cash_flows or cash_flows[0] >= 0:
            return None

        # Check if all remaining cash flows are non-positive
        if all(cf <= 0 for cf in cash_flows[1:]):
            return None

        def npv_at(rate: float) -> float:
            total = 0.0
            for t, cf in enumerate(cash_flows):
                denom = (1.0 + rate) ** t
                if denom == 0:
                    return float("inf")
                total += cf / denom
            return total

        # Search bracket between -0.5 (-50%) and 2.0 (200%)
        low, high = -0.5, 2.0
        npv_low = npv_at(low)
        npv_high = npv_at(high)

        # If signs are opposite, use bisection / secant
        if npv_low * npv_high > 0:
            # Expand high bracket
            high = 5.0
            npv_high = npv_at(high)
            if npv_low * npv_high > 0:
                return None

        for _ in range(max_iter):
            mid = (low + high) / 2.0
            npv_mid = npv_at(mid)
            if abs(npv_mid) < 1e-4 or (high - low) < 1e-5:
                return mid
            if npv_low * npv_mid < 0:
                high = mid
                npv_high = npv_mid
            else:
                low = mid
                npv_low = npv_mid

        return (low + high) / 2.0


financial_service = FinancialService()
