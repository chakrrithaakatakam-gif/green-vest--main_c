from typing import Protocol
from app.models.domain.land import ClimateData, SoilData


class ClimateProvider(Protocol):
    """Protocol for historical climate reanalysis providers (Open-Meteo)."""
    async def get_climate(self, lat: float, lon: float) -> ClimateData:
        """Fetch historical annual rainfall and temperature averages for a coordinate."""
        ...


class SoilProvider(Protocol):
    """Protocol for soil chemical data providers (SoilGrids pH)."""
    async def get_soil(self, lat: float, lon: float) -> SoilData:
        """Fetch topsoil pH (0-30cm) for a coordinate."""
        ...
