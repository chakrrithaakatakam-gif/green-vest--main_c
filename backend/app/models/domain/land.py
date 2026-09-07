from typing import Optional
from pydantic import BaseModel, Field


class Coordinate(BaseModel):
    """Geographic coordinate representation."""
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")


class ClimateData(BaseModel):
    """Climate profile derived from historical reanalysis (Open-Meteo)."""
    annual_rainfall_mm: Optional[float] = Field(None, ge=0.0, description="Annual precipitation in mm")
    mean_temperature_c: Optional[float] = Field(None, description="Annual mean temperature in °C")
    min_temperature_c: Optional[float] = Field(None, description="Mean minimum monthly temperature in °C")
    max_temperature_c: Optional[float] = Field(None, description="Mean maximum monthly temperature in °C")
    source: str = "Open-Meteo Historical Climate Reanalysis"
    status: str = Field("available", description="'available' | 'unavailable'")
    confidence_score: float = Field(1.0, ge=0.0, le=1.0)
    error_message: Optional[str] = None


class SoilData(BaseModel):
    """Soil chemical properties derived from SoilGrids (pH 0-30cm)."""
    ph: Optional[float] = Field(None, ge=0.0, le=14.0, description="Soil pH in H2O (0-30cm)")
    source: str = "ISRIC SoilGrids v2.0 (0-30cm)"
    status: str = Field("available", description="'available' | 'unavailable'")
    confidence_score: float = Field(1.0, ge=0.0, le=1.0)
    error_message: Optional[str] = None


class LandProfile(BaseModel):
    """Canonical Land Profile representing physical site conditions (MVP scope: Rain, Temp, pH)."""
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    climate: ClimateData
    soil: SoilData
    composite_data_confidence: float = Field(1.0, ge=0.0, le=1.0, description="Aggregated confidence rating")
    evaluated_at: Optional[str] = None
