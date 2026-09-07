from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from app.models.domain.land import LandProfile
from app.models.domain.suitability import PlantEvaluationResult
from app.models.domain.carbon import CarbonProjection
from app.models.domain.financial import FinancialMetrics


class RiskAssessment(BaseModel):
    """Multi-factor risk evaluation."""
    composite_risk_penalty: float = Field(..., ge=0.0, le=100.0, description="Overall risk penalty score (0-100)")
    climate_risk_score: float = Field(..., ge=0.0, le=100.0)
    data_uncertainty_score: float = Field(..., ge=0.0, le=100.0)
    market_risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_factors: List[str] = Field(default_factory=list)


class AuditTrail(BaseModel):
    """Transparent explainability audit log for recommendations."""
    strengths: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    risk_flags: List[str] = Field(default_factory=list)
    completeness_notes: List[str] = Field(default_factory=list)


class PlantationStrategy(BaseModel):
    """Complete ranked plantation strategy with multi-objective GreenVest score."""
    rank: int
    crop_id: int
    scientific_name: str
    common_name: str
    use_category: Optional[str] = None
    life_form: Optional[str] = None
    
    # Core Engine Outputs
    suitability: PlantEvaluationResult
    carbon_projection: Optional[CarbonProjection] = None
    financial_metrics: Optional[FinancialMetrics] = None
    risk_assessment: RiskAssessment
    
    # Multi-Objective GreenVest Score (0 - 100)
    greenvest_score: float = Field(..., ge=0.0, le=100.0)
    score_breakdown: Dict[str, float]
    audit_trail: AuditTrail


class GreenVestPlan(BaseModel):
    """Top-level investment plan response."""
    land_profile: LandProfile
    investor_mode: str                      # "carbon_first" | "return_first" | "balanced"
    scenario: str                           # "conservative" | "expected" | "optimistic"
    area_hectares: float = 1.0
    
    # Leaderboards
    ranked_strategies: List[PlantationStrategy]
    disqualified_candidates: List[PlantEvaluationResult]
    
    total_evaluated_plants: int
    total_feasible_plants: int
    total_disqualified_plants: int
    generated_at: str
