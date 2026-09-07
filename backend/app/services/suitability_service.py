"""
Two-Stage Suitability Engine.
Stage 1: Hard Environmental Feasibility Filtering (RMIN..RMAX, TMIN..TMAX, PHMIN..PHMAX).
Stage 2: Continuous Trapezoidal Suitability Scoring with Renormalization and Data Completeness Tracking.
"""

from typing import List, Dict, Tuple, Optional
from app.config import settings
from app.models.domain.land import LandProfile
from app.models.domain.plant import PlantRequirement
from app.models.domain.suitability import (
    ParameterSuitability,
    FeasibilityResult,
    SuitabilityScore,
    PlantEvaluationResult,
)


class SuitabilityEngine:
    """Evaluates botanical candidate plants against canonical LandProfile."""

    def __init__(self, weights=None):
        self.weights = weights or settings.ENV_WEIGHTS

    def evaluate_plants(
        self,
        land_profile: LandProfile,
        candidates: List[PlantRequirement],
        top_k: int = 20,
    ) -> Tuple[List[PlantEvaluationResult], List[PlantEvaluationResult]]:
        """
        Evaluate candidates against land profile.
        Returns (feasible_ranked, disqualified).
        """
        feasible_results: List[PlantEvaluationResult] = []
        disqualified_results: List[PlantEvaluationResult] = []

        for plant in candidates:
            eval_result = self.evaluate_single_plant(land_profile, plant)
            if eval_result.feasibility.is_feasible:
                feasible_results.append(eval_result)
            else:
                disqualified_results.append(eval_result)

        # Rank feasible candidates by environmental_score descending
        feasible_results.sort(
            key=lambda r: (
                r.suitability.environmental_score if r.suitability else 0.0,
                r.suitability.data_completeness_pct if r.suitability else 0.0,
                r.data_confidence_rating
            ),
            reverse=True
        )

        return feasible_results[:top_k], disqualified_results

    def evaluate_single_plant(
        self,
        land: LandProfile,
        plant: PlantRequirement,
    ) -> PlantEvaluationResult:
        """Run Stage 1 and Stage 2 evaluation for a single plant candidate."""
        climate = land.climate
        soil = land.soil

        # Stage 1: Hard Feasibility Filtering
        feasibility = self._evaluate_stage1_feasibility(climate, soil, plant)

        audit_notes: List[str] = []

        if not feasibility.is_feasible:
            # Plant is environmentally disqualified
            audit_notes.extend(feasibility.failure_reasons)
            return PlantEvaluationResult(
                plant=plant,
                feasibility=feasibility,
                suitability=None,
                data_confidence_rating=land.composite_data_confidence,
                audit_notes=audit_notes,
            )

        # Stage 2: Continuous Trapezoidal Scoring
        suitability, stage2_notes = self._evaluate_stage2_suitability(climate, soil, plant)
        audit_notes.extend(stage2_notes)

        # Data confidence rating combines site confidence and completeness
        combined_confidence = round(
            land.composite_data_confidence * (suitability.data_completeness_pct / 100.0), 2
        )

        return PlantEvaluationResult(
            plant=plant,
            feasibility=feasibility,
            suitability=suitability,
            data_confidence_rating=combined_confidence,
            audit_notes=audit_notes,
        )

    def _evaluate_stage1_feasibility(
        self,
        climate,
        soil,
        plant: PlantRequirement,
    ) -> FeasibilityResult:
        """
        Stage 1: Hard absolute bounds check.
        Disqualifies candidate if measured parameter is strictly outside [MIN, MAX].
        """
        reasons: List[str] = []

        # Rainfall
        rain = climate.annual_rainfall_mm if climate.status == "available" else None
        if rain is not None:
            if rain < plant.rainfall_min:
                reasons.append(
                    f"Annual rainfall {rain:.1f}mm is below absolute survival minimum of {plant.rainfall_min:.1f}mm"
                )
            elif rain > plant.rainfall_max:
                reasons.append(
                    f"Annual rainfall {rain:.1f}mm exceeds absolute survival maximum of {plant.rainfall_max:.1f}mm"
                )

        # Temperature (check mean temperature against absolute bounds)
        temp = climate.mean_temperature_c if climate.status == "available" else None
        if temp is not None:
            if temp < plant.temp_min:
                reasons.append(
                    f"Mean temperature {temp:.1f}°C is below absolute survival minimum of {plant.temp_min:.1f}°C"
                )
            elif temp > plant.temp_max:
                reasons.append(
                    f"Mean temperature {temp:.1f}°C exceeds absolute survival maximum of {plant.temp_max:.1f}°C"
                )

        # Soil pH
        ph = soil.ph if soil.status == "available" else None
        if ph is not None:
            if ph < plant.ph_min:
                reasons.append(
                    f"Soil pH {ph:.2f} is below absolute tolerance minimum of {plant.ph_min:.1f}"
                )
            elif ph > plant.ph_max:
                reasons.append(
                    f"Soil pH {ph:.2f} exceeds absolute tolerance maximum of {plant.ph_max:.1f}"
                )

        is_feasible = len(reasons) == 0
        return FeasibilityResult(is_feasible=is_feasible, failure_reasons=reasons)

    def _evaluate_stage2_suitability(
        self,
        climate,
        soil,
        plant: PlantRequirement,
    ) -> Tuple[SuitabilityScore, List[str]]:
        """
        Stage 2: Continuous trapezoidal scoring across available optimal bounds.
        """
        notes: List[str] = []
        param_evals: Dict[str, ParameterSuitability] = {}

        # 1. Rainfall evaluation
        rain_val = climate.annual_rainfall_mm if climate.status == "available" else None
        rain_eval = self._calculate_trapezoid_score(
            param_name="rainfall",
            value=rain_val,
            min_bound=plant.rainfall_min,
            opt_min=plant.rainfall_opt_min,
            opt_max=plant.rainfall_opt_max,
            max_bound=plant.rainfall_max,
            unit="mm",
        )
        param_evals["rainfall"] = rain_eval
        if not rain_eval.is_evaluable:
            notes.append("Optimal rainfall bounds unavailable in FAO ECOCROP; parameter marked unevaluable.")

        # 2. Temperature evaluation
        temp_val = climate.mean_temperature_c if climate.status == "available" else None
        temp_eval = self._calculate_trapezoid_score(
            param_name="temperature",
            value=temp_val,
            min_bound=plant.temp_min,
            opt_min=plant.temp_opt_min,
            opt_max=plant.temp_opt_max,
            max_bound=plant.temp_max,
            unit="°C",
        )
        param_evals["temperature"] = temp_eval
        if not temp_eval.is_evaluable:
            notes.append("Optimal temperature bounds unavailable in FAO ECOCROP; parameter marked unevaluable.")

        # 3. Soil pH evaluation
        ph_val = soil.ph if soil.status == "available" else None
        ph_eval = self._calculate_trapezoid_score(
            param_name="ph",
            value=ph_val,
            min_bound=plant.ph_min,
            opt_min=plant.ph_opt_min,
            opt_max=plant.ph_opt_max,
            max_bound=plant.ph_max,
            unit="",
        )
        param_evals["ph"] = ph_eval
        if not ph_eval.is_evaluable:
            notes.append("Optimal soil pH bounds unavailable in FAO ECOCROP; parameter marked unevaluable.")

        # Weighted score over evaluable metrics
        weights_map = {
            "rainfall": self.weights.rainfall,
            "temperature": self.weights.temperature,
            "ph": self.weights.ph,
        }

        weighted_sum = 0.0
        sum_weights = 0.0
        evaluable_count = 0

        for name, pe in param_evals.items():
            if pe.is_evaluable and pe.sub_score is not None:
                w = weights_map[name]
                weighted_sum += w * pe.sub_score
                sum_weights += w
                evaluable_count += 1

        if sum_weights > 0.0:
            env_score = round(100.0 * (weighted_sum / sum_weights), 1)
        else:
            env_score = 0.0

        completeness_pct = round((evaluable_count / 3.0) * 100.0, 1)

        score = SuitabilityScore(
            environmental_score=env_score,
            data_completeness_pct=completeness_pct,
            parameters=param_evals,
        )

        return score, notes

    @staticmethod
    def _calculate_trapezoid_score(
        param_name: str,
        value: Optional[float],
        min_bound: float,
        opt_min: Optional[float],
        opt_max: Optional[float],
        max_bound: float,
        unit: str = "",
    ) -> ParameterSuitability:
        """Computes continuous trapezoidal score S(x) in [0.0, 1.0]."""
        unit_str = f" {unit}".strip()

        # If metric is missing or optimal envelope is missing -> mark unevaluable
        if value is None or opt_min is None or opt_max is None:
            return ParameterSuitability(
                parameter_name=param_name,
                measured_value=value,
                min_bound=min_bound,
                opt_min=opt_min,
                opt_max=opt_max,
                max_bound=max_bound,
                sub_score=None,
                status="unevaluable",
                is_evaluable=False,
                explanation=f"{param_name.capitalize()} optimal envelope unavailable in ECOCROP; parameter unevaluable.",
            )

        # Infeasible bounds
        if value < min_bound or value > max_bound:
            return ParameterSuitability(
                parameter_name=param_name,
                measured_value=value,
                min_bound=min_bound,
                opt_min=opt_min,
                opt_max=opt_max,
                max_bound=max_bound,
                sub_score=0.0,
                status="infeasible",
                is_evaluable=True,
                explanation=f"{value:.1f}{unit_str} is outside survival range [{min_bound:.1f}, {max_bound:.1f}]{unit_str}.",
            )

        # Optimal plateau [opt_min, opt_max]
        if opt_min <= value <= opt_max:
            return ParameterSuitability(
                parameter_name=param_name,
                measured_value=value,
                min_bound=min_bound,
                opt_min=opt_min,
                opt_max=opt_max,
                max_bound=max_bound,
                sub_score=1.0,
                status="optimal",
                is_evaluable=True,
                explanation=f"{value:.1f}{unit_str} is in optimal plateau [{opt_min:.1f}, {opt_max:.1f}]{unit_str}.",
            )

        # Marginal lower slope [min_bound, opt_min)
        if min_bound <= value < opt_min:
            denom = opt_min - min_bound
            sub_score = round((value - min_bound) / denom, 3) if denom > 0 else 1.0
            return ParameterSuitability(
                parameter_name=param_name,
                measured_value=value,
                min_bound=min_bound,
                opt_min=opt_min,
                opt_max=opt_max,
                max_bound=max_bound,
                sub_score=sub_score,
                status="marginal",
                is_evaluable=True,
                explanation=f"{value:.1f}{unit_str} is in marginal lower range [{min_bound:.1f}, {opt_min:.1f}]{unit_str} (score: {sub_score:.2f}).",
            )

        # Marginal upper slope (opt_max, max_bound]
        if opt_max < value <= max_bound:
            denom = max_bound - opt_max
            sub_score = round((max_bound - value) / denom, 3) if denom > 0 else 1.0
            return ParameterSuitability(
                parameter_name=param_name,
                measured_value=value,
                min_bound=min_bound,
                opt_min=opt_min,
                opt_max=opt_max,
                max_bound=max_bound,
                sub_score=sub_score,
                status="marginal",
                is_evaluable=True,
                explanation=f"{value:.1f}{unit_str} is in marginal upper range [{opt_max:.1f}, {max_bound:.1f}]{unit_str} (score: {sub_score:.2f}).",
            )

        return ParameterSuitability(
            parameter_name=param_name,
            measured_value=value,
            min_bound=min_bound,
            opt_min=opt_min,
            opt_max=opt_max,
            max_bound=max_bound,
            sub_score=0.0,
            status="infeasible",
            is_evaluable=True,
            explanation=f"{value:.1f}{unit_str} outside tolerance bounds.",
        )


suitability_engine = SuitabilityEngine()
