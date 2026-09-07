"""
Plants API Endpoints.
Provides access to FAO ECOCROP botanical knowledge base.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas.plant_dto import PlantListResponse, PlantDetailResponse
from app.services.ecocrop_service import ecocrop_service

router = APIRouter(tags=["Plants"])


@router.get("/plants", response_model=PlantListResponse)
async def list_plants(
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Offset index"),
    category: Optional[str] = Query(None, description="Filter by use category (e.g., Timber, Fruit)"),
    search: Optional[str] = Query(None, description="Search term for common or scientific name"),
):
    """Retrieve paginated plants from the ECOCROP knowledge base."""
    summaries, total = ecocrop_service.list_plants(
        limit=limit, offset=offset, category=category, search=search
    )
    return PlantListResponse(
        total_count=total,
        limit=limit,
        offset=offset,
        plants=summaries,
    )


@router.get("/plants/{crop_id}", response_model=PlantDetailResponse)
async def get_plant(crop_id: int):
    """Retrieve botanical constraints for a specific plant by crop_id."""
    plant = ecocrop_service.get_plant_by_id(crop_id)
    if not plant:
        raise HTTPException(
            status_code=404,
            detail=f"Plant with crop_id {crop_id} not found in ECOCROP knowledge base."
        )
    return PlantDetailResponse(plant=plant)
