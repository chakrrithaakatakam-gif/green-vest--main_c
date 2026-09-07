from typing import List, Dict
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentalWeights(BaseModel):
    """Configurable weights for the environmental suitability engine (MVP: Rain, Temp, pH)."""
    rainfall: float = Field(0.40, ge=0.0, le=1.0, description="Weight for rainfall suitability")
    temperature: float = Field(0.35, ge=0.0, le=1.0, description="Weight for temperature suitability")
    ph: float = Field(0.25, ge=0.0, le=1.0, description="Weight for soil pH suitability")


class InvestorModeWeights(BaseModel):
    """Multi-objective weights for final GreenVest score calculation."""
    suitability: float = Field(..., ge=0.0, le=1.0)
    carbon: float = Field(..., ge=0.0, le=1.0)
    financial: float = Field(..., ge=0.0, le=1.0)
    risk_penalty: float = Field(..., ge=0.0, le=1.0)


class Settings(BaseSettings):
    """GreenVest application settings and runtime configuration."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server Info
    APP_NAME: str = "GreenVest"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    # Provider Endpoints
    OPEN_METEO_BASE_URL: str = "https://archive-api.open-meteo.com/v1/archive"
    SOILGRIDS_BASE_URL: str = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    PROVIDER_TIMEOUT_SECONDS: float = 4.0
    PROVIDER_MAX_RETRIES: int = 2

    # Cache Settings
    CACHE_TTL_SECONDS: int = 86400  # 24 hours
    ENABLE_PERSISTENT_CACHE: bool = True
    SPATIAL_CACHE_DB_PATH: str = "data/cache/spatial_cache.db"
    ECOCROP_DB_PATH: str = "data/processed/ecocrop.db"
    STRATEGIES_PATH: str = "data/strategies/carbon_profiles.json"

    # Default Environmental Weights
    ENV_WEIGHTS: EnvironmentalWeights = Field(default_factory=EnvironmentalWeights)

    # Investor Mode Multi-Objective Weights
    INVESTOR_MODES: Dict[str, InvestorModeWeights] = {
        "carbon_first": InvestorModeWeights(
            suitability=0.35,
            carbon=0.45,
            financial=0.10,
            risk_penalty=0.10
        ),
        "return_first": InvestorModeWeights(
            suitability=0.25,
            carbon=0.15,
            financial=0.50,
            risk_penalty=0.10
        ),
        "balanced": InvestorModeWeights(
            suitability=0.35,
            carbon=0.25,
            financial=0.25,
            risk_penalty=0.15
        )
    }

    # Financial & Carbon Modeling Baseline Defaults
    DEFAULT_DISCOUNT_RATE: float = 0.08
    DEFAULT_CARBON_PRICE_USD: float = 20.0
    DEFAULT_HORIZON_YEARS: int = 20
    DEFAULT_BUFFER_DISCOUNT_PCT: float = 0.15  # 15% standard buffer pool deduction


settings = Settings()
