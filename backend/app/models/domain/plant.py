from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PlantRequirement(BaseModel):
    """
    Plant botanical requirements mapped from FAO ECOCROP.
    Contains strictly environmental constraints without embedded carbon constants.
    """
    model_config = ConfigDict(populate_by_name=True)

    crop_id: int
    scientific_name: str
    common_name: str
    use_category: Optional[str] = None     # e.g., Timber, Fruit, Agroforestry, Oil, Biomass
    life_form: Optional[str] = None        # e.g., Tree, Shrub, Herb, Grass
    growth_cycle_days_min: Optional[int] = Field(None, alias="GMIN")
    growth_cycle_days_max: Optional[int] = Field(None, alias="GMAX")

    # Absolute Environmental Bounds (Required for Stage 1 Feasibility)
    rainfall_min: float = Field(..., alias="RMIN", description="Absolute minimum annual rainfall (mm)")
    rainfall_max: float = Field(..., alias="RMAX", description="Absolute maximum annual rainfall (mm)")
    temp_min: float = Field(..., alias="TMIN", description="Absolute minimum temperature (°C)")
    temp_max: float = Field(..., alias="TMAX", description="Absolute maximum temperature (°C)")
    ph_min: float = Field(..., alias="PHMIN", description="Absolute minimum soil pH")
    ph_max: float = Field(..., alias="PHMAX", description="Absolute maximum soil pH")

    # Optimal Environmental Bounds (For Stage 2 Trapezoidal Suitability Scoring)
    rainfall_opt_min: Optional[float] = Field(None, alias="ROPMN", description="Optimal lower rainfall (mm)")
    rainfall_opt_max: Optional[float] = Field(None, alias="ROPMX", description="Optimal upper rainfall (mm)")
    temp_opt_min: Optional[float] = Field(None, alias="TOPMN", description="Optimal lower temperature (°C)")
    temp_opt_max: Optional[float] = Field(None, alias="TOPMX", description="Optimal upper temperature (°C)")
    ph_opt_min: Optional[float] = Field(None, alias="PHOPMN", description="Optimal lower soil pH")
    ph_opt_max: Optional[float] = Field(None, alias="PHOPMX", description="Optimal upper soil pH")

    # Metadata & Quality Flags
    has_complete_optimal_ranges: bool = Field(
        True,
        description="False if one or more optimal ranges (ROPMN, TOPMN, PHOPMN) are missing in ECOCROP"
    )
    source: str = "FAO ECOCROP Knowledge Base"


class PlantSummary(BaseModel):
    """Compact summary of a plant record for list views."""
    crop_id: int
    scientific_name: str
    common_name: str
    use_category: Optional[str] = None
    life_form: Optional[str] = None
    rainfall_range: str
    temp_range: str
    ph_range: str
    has_complete_optimal_ranges: bool
