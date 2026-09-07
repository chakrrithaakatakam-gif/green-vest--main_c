from typing import List, Optional
from pydantic import BaseModel
from app.models.domain.plant import PlantSummary, PlantRequirement


class PlantListResponse(BaseModel):
    """Paginated list of plant records from the ECOCROP knowledge base."""
    total_count: int
    limit: int
    offset: int
    plants: List[PlantSummary]


class PlantDetailResponse(BaseModel):
    """Full detail of a single plant record."""
    plant: PlantRequirement
