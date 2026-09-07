from typing import Optional
from pydantic import BaseModel, Field
from app.models.domain.strategy import GreenVestPlan


class PlanOptimizationRequest(BaseModel):
    """Top-level request to generate a complete optimized investment plan."""
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    area_hectares: float = Field(1.0, gt=0.0, le=10000.0, description="Plantation project land area in hectares")
    investor_mode: str = Field(
        "balanced",
        pattern="^(carbon_first|return_first|balanced)$",
        description="'carbon_first' | 'return_first' | 'balanced'"
    )
    scenario: str = Field(
        "expected",
        pattern="^(conservative|expected|optimistic)$",
        description="'conservative' | 'expected' | 'optimistic'"
    )
    custom_discount_rate: Optional[float] = Field(None, ge=0.0, le=0.30)
    custom_carbon_price: Optional[float] = Field(None, ge=0.0, le=200.0)
    top_k: int = Field(10, ge=1, le=50)


class PlanOptimizationResponse(BaseModel):
    """Optimized plantation recommendations, DCF cash flows, and explainability audit."""
    plan: GreenVestPlan
