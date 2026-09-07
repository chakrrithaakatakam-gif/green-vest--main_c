from typing import List, Optional
from pydantic import BaseModel, Field


class PlantCarbonProfile(BaseModel):
    """
    Decoupled carbon and biomass growth parameters.
    Every parameter is explicitly labeled with provenance, assumption status, and confidence.
    """
    crop_id: int
    scientific_name: str
    common_name: str
    
    # Growth & Biomass Parameters
    max_above_ground_biomass_t_ha: float = Field(
        ..., 
        description="Maximum asymptotic Above-Ground Biomass (AGB) in tonnes/ha"
    )
    growth_rate_k: float = Field(
        ..., 
        description="Sigmoid growth curve slope parameter k (1/year)"
    )
    inflection_year_t0: float = Field(
        ..., 
        description="Year of inflection (maximum mean annual biomass increment)"
    )
    
    # Biophysical Ratios (Explicitly Labeled as Assumptions)
    root_to_shoot_ratio: float = Field(
        0.24, 
        description="GreenVest modeling assumption based on IPCC Tier 1 defaults (not a species-specific measured value)"
    )
    carbon_fraction: float = Field(
        0.47, 
        description="GreenVest modeling assumption based on IPCC forestry guidelines (fraction of dry biomass that is carbon)"
    )
    
    # Audit & Scientific Provenance
    data_source: str = "FAO Forestry Papers / IPCC 2006 Guidelines for AFOLU"
    is_assumption: bool = Field(
        True,
        description="True if parameters are generalized model assumptions rather than site-specific field measurements"
    )
    is_species_specific: bool = Field(
        False,
        description="True if parameters are calibrated specifically for this botanical species"
    )
    confidence_rating: float = Field(0.75, ge=0.0, le=1.0)


class CarbonYearPoint(BaseModel):
    """Annual point on the 20-year biophysical carbon accumulation trajectory."""
    year: int
    above_ground_biomass_t_ha: float
    total_biomass_t_ha: float
    carbon_stock_t_ha: float
    cumulative_co2e_t_ha: float
    annual_co2e_increment_t_ha: float


class CarbonProjection(BaseModel):
    """
    Complete 20-year biophysical carbon sequestration trajectory.
    Expressed in Estimated Biophysical Carbon Sequestration (tCO2e/ha).
    """
    crop_id: int
    scientific_name: str
    time_horizon_years: int = 20
    cumulative_20yr_co2e_t_ha: float
    mean_annual_co2e_t_ha: float
    trajectory: List[CarbonYearPoint]
    is_modeled_estimate: bool = True
    disclaimer: str = (
        "Estimated Biophysical Carbon Sequestration. Modeled estimate based on ecological assumptions. "
        "Does not constitute certified carbon credits or guaranteed offset revenue."
    )
    confidence_rating: float
