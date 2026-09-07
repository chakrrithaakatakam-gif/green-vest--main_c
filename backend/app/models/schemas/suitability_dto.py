from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.domain.land import LandProfile
from app.models.domain.suitability import PlantEvaluationResult


class SuitabilityEvaluationRequest(BaseModel):
    """Request to evaluate candidate plants against a Land Profile."""
    land_profile: LandProfile
    crop_ids: Optional[List[int]] = Field(None, description="Optional specific crop IDs to evaluate")
    use_category_filter: Optional[str] = Field(None, description="Filter by crop use (e.g. 'timber', 'fruit')")
    top_k: int = Field(20, ge=1, le=100)


class SuitabilityEvaluationResponse(BaseModel):
    """Result of two-stage feasibility filtering and suitability scoring."""
    feasible_plants: List[PlantEvaluationResult]
    disqualified_plants: List[PlantEvaluationResult]
    total_evaluated: int
    total_feasible: int
    total_disqualified: int
