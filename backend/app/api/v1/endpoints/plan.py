"""
Plan Optimization API Endpoint.
Orchestrates Land Acquisition -> ECOCROP Evaluation -> Carbon -> Financial -> Multi-Objective Ranking.
"""

from fastapi import APIRouter
from app.models.schemas.plan_dto import PlanOptimizationRequest, PlanOptimizationResponse
from app.services.land_service import land_service
from app.services.ecocrop_service import ecocrop_service
from app.services.suitability_service import suitability_engine
from app.services.optimizer_service import optimizer_service

router = APIRouter(tags=["Plan"])


@router.post("/plan/optimize", response_model=PlanOptimizationResponse)
async def optimize_plantation_plan(request: PlanOptimizationRequest):
    """
    Generate complete GreenVest investment plan for coordinate and investor profile.
    Orchestrates physical telemetry streaming, botanical feasibility, continuous suitability scoring,
    decoupled biophysical carbon projections, 20-year DCF modeling, and multi-objective ranking.
    """
    # 1. Acquire Land Profile (concurrence of Open-Meteo and SoilGrids)
    land_profile = await land_service.get_land_profile(
        lat=request.latitude,
        lon=request.longitude
    )

    # 2. Retrieve botanical candidate requirements from ECOCROP
    candidates = ecocrop_service.get_all_plant_requirements()

    # 3. Two-Stage Suitability Evaluation
    feasible, disqualified = suitability_engine.evaluate_plants(
        land_profile=land_profile,
        candidates=candidates,
        top_k=len(candidates)  # Pass all feasible candidates to optimizer
    )

    # 4. Multi-Objective Optimization across Investor Mode & Scenario
    plan = optimizer_service.generate_plan(
        land_profile=land_profile,
        feasible_results=feasible,
        disqualified_results=disqualified,
        investor_mode=request.investor_mode,
        scenario=request.scenario,
        area_hectares=request.area_hectares,
        custom_discount_rate=request.custom_discount_rate,
        custom_carbon_price=request.custom_carbon_price,
        top_k=request.top_k,
    )

    return PlanOptimizationResponse(plan=plan)
