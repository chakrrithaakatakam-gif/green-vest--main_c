from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from app.models.domain.plant import PlantRequirement


class ParameterSuitability(BaseModel):
    """Evaluation breakdown for a single environmental metric."""
    parameter_name: str                     # "rainfall" | "temperature" | "ph"
    measured_value: Optional[float]
    min_bound: float
    opt_min: Optional[float]
    opt_max: Optional[float]
    max_bound: float
    sub_score: Optional[float]              # 0.0 to 1.0, or None if optimal range is missing/parameter unavailable
    status: str                             # "optimal" | "marginal" | "infeasible" | "unevaluable"
    is_evaluable: bool                      # False if optimal bounds or land metric is null
    explanation: str


class FeasibilityResult(BaseModel):
    """Result of Stage 1 hard environmental boundary filtering."""
    is_feasible: bool
    failure_reasons: List[str] = Field(default_factory=list)


class SuitabilityScore(BaseModel):
    """Result of Stage 2 continuous trapezoidal tolerance scoring."""
    environmental_score: float = Field(..., ge=0.0, le=100.0, description="Overall environmental score (0-100)")
    data_completeness_pct: float = Field(..., ge=0.0, le=100.0, description="Percentage of parameters fully evaluable")
    parameters: Dict[str, ParameterSuitability]


class PlantEvaluationResult(BaseModel):
    """Combined Stage 1 Feasibility + Stage 2 Suitability for a single plant candidate."""
    plant: PlantRequirement
    feasibility: FeasibilityResult
    suitability: Optional[SuitabilityScore] = None
    data_confidence_rating: float = Field(..., ge=0.0, le=1.0)
    audit_notes: List[str] = Field(default_factory=list)
