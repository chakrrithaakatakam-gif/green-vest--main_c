"""
Suitability Evaluation API Endpoint.
Executes Two-Stage botanical feasibility filtering and trapezoidal suitability scoring.
"""

from fastapi import APIRouter
from app.models.schemas.suitability_dto import (
    SuitabilityEvaluationRequest,
    SuitabilityEvaluationResponse,
)
from app.services.ecocrop_service import ecocrop_service
from app.services.suitability_service import suitability_engine

router = APIRouter(tags=["Suitability"])


@router.post("/suitability/evaluate", response_model=SuitabilityEvaluationResponse)
async def evaluate_suitability(request: SuitabilityEvaluationRequest):
    """
    Evaluate candidate plants against a Canonical Land Profile.
    Returns ranked feasible plants and transparent disqualification audit logs.
    """
    # 1. Fetch candidates from ECOCROP database
    candidates = ecocrop_service.get_all_plant_requirements(
        crop_ids=request.crop_ids,
        use_category=request.use_category_filter
    )

    # 2. Execute Two-Stage Suitability Engine
    feasible, disqualified = suitability_engine.evaluate_plants(
        land_profile=request.land_profile,
        candidates=candidates,
        top_k=request.top_k
    )

    return SuitabilityEvaluationResponse(
        feasible_plants=feasible,
        disqualified_plants=disqualified,
        total_evaluated=len(candidates),
        total_feasible=len(feasible),
        total_disqualified=len(disqualified)
    )
