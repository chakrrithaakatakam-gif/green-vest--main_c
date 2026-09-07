"""
Multi-Objective Optimizer & Plan Generation Service.
Synthesizes environmental suitability, biophysical carbon trajectories, DCF financial returns,
and risk modeling across investor modes (carbon-first, return-first, balanced) and scenarios.
"""

from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple
from app.config import settings
from app.models.domain.land import LandProfile
from app.models.domain.plant import PlantRequirement
from app.models.domain.suitability import PlantEvaluationResult
from app.models.domain.carbon import CarbonProjection
from app.models.domain.financial import FinancialMetrics, FinancialAssumptions
from app.models.domain.strategy import (
    RiskAssessment,
    AuditTrail,
    PlantationStrategy,
    GreenVestPlan,
)
from app.services.carbon_service import carbon_service
from app.services.financial_service import financial_service


class OptimizerService:
    """Orchestrates multi-objective investment strategy ranking and audit trail generation."""

    def __init__(self):
        self.investor_modes = settings.INVESTOR_MODES

    def generate_plan(
        self,
        land_profile: LandProfile,
        feasible_results: List[PlantEvaluationResult],
        disqualified_results: List[PlantEvaluationResult],
        investor_mode: str = "balanced",
        scenario: str = "expected",
        area_hectares: float = 1.0,
        custom_discount_rate: Optional[float] = None,
        custom_carbon_price: Optional[float] = None,
        top_k: int = 10,
    ) -> GreenVestPlan:
        """Generate optimized multi-objective plantation investment plan."""
        # 1. Adjust assumptions based on scenario
        adjusted_carbon_price, adjusted_discount_rate, yield_multiplier = self._apply_scenario_adjustments(
            scenario=scenario,
            custom_carbon_price=custom_carbon_price,
            custom_discount_rate=custom_discount_rate,
        )

        # 2. Compute Carbon Projections and Financial Metrics for all feasible candidates
        evaluated_candidates: List[Tuple[PlantEvaluationResult, CarbonProjection, FinancialMetrics]] = []
        for res in feasible_results:
            plant = res.plant
            carbon_proj = carbon_service.calculate_projection(
                crop_id=plant.crop_id,
                scientific_name=plant.scientific_name,
                common_name=plant.common_name,
                horizon_years=20,
            )

            assumptions = financial_service.get_default_assumptions(
                crop_id=plant.crop_id,
                custom_discount_rate=adjusted_discount_rate,
                custom_carbon_price=adjusted_carbon_price,
            )
            # Adjust yield by scenario multiplier
            assumptions.yield_revenue_annual_usd_ha = round(
                assumptions.yield_revenue_annual_usd_ha * yield_multiplier, 2
            )

            fin_metrics = financial_service.calculate_dcf(
                carbon_projection=carbon_proj,
                assumptions=assumptions,
                horizon_years=20,
            )
            evaluated_candidates.append((res, carbon_proj, fin_metrics))

        # 3. Find maximums for relative normalization across candidates
        max_co2e = max((c[1].cumulative_20yr_co2e_t_ha for c in evaluated_candidates), default=1.0)
        max_npv = max((c[2].npv_usd_ha for c in evaluated_candidates), default=1.0)

        # 4. Get mode weights
        weights = self.investor_modes.get(investor_mode, self.investor_modes["balanced"])

        # 5. Build ranked PlantationStrategy objects
        strategies: List[PlantationStrategy] = []
        for eval_res, carbon_proj, fin_metrics in evaluated_candidates:
            risk = self._assess_risk(land_profile, eval_res, fin_metrics)
            
            # Scores normalized to 0 - 100
            s_env = eval_res.suitability.environmental_score if eval_res.suitability else 0.0
            s_carbon = round((carbon_proj.cumulative_20yr_co2e_t_ha / max_co2e) * 100.0, 1) if max_co2e > 0 else 0.0
            s_financial = round((max(0.0, fin_metrics.npv_usd_ha) / max_npv) * 100.0, 1) if max_npv > 0 else 0.0
            risk_penalty = risk.composite_risk_penalty

            # Multi-objective synthesis:
            # Score = w_suit * S_env + w_carb * S_carb + w_fin * S_fin - w_risk * Risk
            greenvest_score = (
                weights.suitability * s_env +
                weights.carbon * s_carbon +
                weights.financial * s_financial -
                weights.risk_penalty * risk_penalty
            )
            greenvest_score = max(0.0, min(100.0, round(greenvest_score, 1)))

            score_breakdown = {
                "suitability_score": s_env,
                "carbon_score": s_carbon,
                "financial_score": s_financial,
                "risk_penalty": risk_penalty,
                "weighted_suitability": round(weights.suitability * s_env, 1),
                "weighted_carbon": round(weights.carbon * s_carbon, 1),
                "weighted_financial": round(weights.financial * s_financial, 1),
                "weighted_risk_deduction": round(weights.risk_penalty * risk_penalty, 1),
            }

            audit_trail = self._build_audit_trail(
                eval_res=eval_res,
                carbon_proj=carbon_proj,
                fin_metrics=fin_metrics,
                risk=risk,
                scenario=scenario,
            )

            strategies.append(
                PlantationStrategy(
                    rank=0,  # assigned after sorting
                    crop_id=eval_res.plant.crop_id,
                    scientific_name=eval_res.plant.scientific_name,
                    common_name=eval_res.plant.common_name,
                    use_category=eval_res.plant.use_category,
                    life_form=eval_res.plant.life_form,
                    suitability=eval_res,
                    carbon_projection=carbon_proj,
                    financial_metrics=fin_metrics,
                    risk_assessment=risk,
                    greenvest_score=greenvest_score,
                    score_breakdown=score_breakdown,
                    audit_trail=audit_trail,
                )
            )

        # Sort strategies by greenvest_score descending
        strategies.sort(key=lambda s: s.greenvest_score, reverse=True)
        for idx, strat in enumerate(strategies):
            strat.rank = idx + 1

        top_strategies = strategies[:top_k]

        total_eval = len(feasible_results) + len(disqualified_results)

        return GreenVestPlan(
            land_profile=land_profile,
            investor_mode=investor_mode,
            scenario=scenario,
            area_hectares=area_hectares,
            ranked_strategies=top_strategies,
            disqualified_candidates=disqualified_results,
            total_evaluated_plants=total_eval,
            total_feasible_plants=len(feasible_results),
            total_disqualified_plants=len(disqualified_results),
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def _apply_scenario_adjustments(
        scenario: str,
        custom_carbon_price: Optional[float],
        custom_discount_rate: Optional[float],
    ) -> Tuple[float, float, float]:
        """Apply macro scenario variations."""
        base_price = custom_carbon_price if custom_carbon_price is not None else settings.DEFAULT_CARBON_PRICE_USD
        base_rate = custom_discount_rate if custom_discount_rate is not None else settings.DEFAULT_DISCOUNT_RATE

        if scenario == "conservative":
            adj_price = max(5.0, base_price * 0.80)       # -20% carbon price
            adj_rate = min(0.25, base_rate + 0.02)         # +200 bps discount rate
            yield_mult = 0.85                              # -15% crop yield
        elif scenario == "optimistic":
            adj_price = base_price * 1.20                  # +20% carbon price
            adj_rate = max(0.04, base_rate - 0.01)         # -100 bps discount rate
            yield_mult = 1.15                              # +15% crop yield
        else:  # expected
            adj_price = base_price
            adj_rate = base_rate
            yield_mult = 1.0

        return round(adj_price, 2), round(adj_rate, 4), yield_mult

    @staticmethod
    def _assess_risk(
        land: LandProfile,
        eval_res: PlantEvaluationResult,
        fin: FinancialMetrics,
    ) -> RiskAssessment:
        """Calculate multi-factor risk penalty."""
        factors: List[str] = []

        # 1. Climate risk: based on marginal suitability sub-scores
        climate_risk = 0.0
        if eval_res.suitability:
            marginal_count = sum(
                1 for p in eval_res.suitability.parameters.values() if p.status == "marginal"
            )
            climate_risk = min(100.0, marginal_count * 25.0)
            if marginal_count > 0:
                factors.append(f"{marginal_count} environmental parameter(s) in marginal tolerance zone.")

        # 2. Data uncertainty risk
        uncertainty = round((1.0 - land.composite_data_confidence) * 100.0, 1)
        if uncertainty > 20.0:
            factors.append(f"Physical telemetry uncertainty is {uncertainty:.0f}%.")

        # 3. Market / Financial risk: long payback or negative IRR
        market_risk = 15.0
        if fin.payback_period_years is None or fin.payback_period_years > 8.0:
            market_risk += 35.0
            factors.append("Extended capital payback horizon (>8 years).")
        if fin.npv_usd_ha < 1000.0:
            market_risk += 25.0
            factors.append("Low modeled NPV under current financial assumptions.")

        composite = round(
            (climate_risk * 0.40) + (uncertainty * 0.35) + (market_risk * 0.25), 1
        )

        return RiskAssessment(
            composite_risk_penalty=min(100.0, composite),
            climate_risk_score=round(climate_risk, 1),
            data_uncertainty_score=uncertainty,
            market_risk_score=round(market_risk, 1),
            risk_factors=factors,
        )

    @staticmethod
    def _build_audit_trail(
        eval_res: PlantEvaluationResult,
        carbon_proj: CarbonProjection,
        fin_metrics: FinancialMetrics,
        risk: RiskAssessment,
        scenario: str,
    ) -> AuditTrail:
        """Synthesize explainability log for plantation strategy."""
        strengths: List[str] = []
        constraints: List[str] = []
        completeness_notes: List[str] = []

        if eval_res.suitability:
            for name, param in eval_res.suitability.parameters.items():
                if param.status == "optimal":
                    strengths.append(f"{name.capitalize()} in optimal botanical envelope.")
                elif param.status == "marginal":
                    constraints.append(param.explanation)
                elif param.status == "unevaluable":
                    completeness_notes.append(f"{name.capitalize()} optimal envelope missing in ECOCROP.")

        if carbon_proj.cumulative_20yr_co2e_t_ha > 150.0:
            strengths.append(
                f"High 20-yr carbon sequestration potential ({carbon_proj.cumulative_20yr_co2e_t_ha:.1f} tCO2e/ha)."
            )

        if fin_metrics.npv_usd_ha > 3000.0:
            strengths.append(f"Robust modeled 20-yr NPV of ${fin_metrics.npv_usd_ha:,.0f}/ha.")

        if fin_metrics.payback_period_years:
            strengths.append(f"Estimated payback achieved in {fin_metrics.payback_period_years:.1f} years.")

        completeness_notes.append(f"Evaluated under '{scenario}' economic scenario.")

        return AuditTrail(
            strengths=strengths,
            constraints=constraints,
            risk_flags=risk.risk_factors,
            completeness_notes=completeness_notes,
        )


optimizer_service = OptimizerService()
