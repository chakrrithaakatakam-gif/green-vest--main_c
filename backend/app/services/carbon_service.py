"""
Decoupled Carbon Sequestration Service.
Implements Sigmoidal Above-Ground Biomass accumulation, IPCC Tier 1 Root-to-Shoot ratios,
and 20-Year Biophysical Carbon Trajectory modeling with labeled scientific assumptions.
"""

import os
import json
import math
from typing import Dict, Optional, List
from app.config import settings
from app.models.domain.carbon import (
    PlantCarbonProfile,
    CarbonYearPoint,
    CarbonProjection,
)


class CarbonService:
    """Biophysical carbon growth modeling decoupled from botanical constraints."""

    def __init__(self, profiles_path: Optional[str] = None):
        self._profiles_path = self._resolve_path(profiles_path or settings.STRATEGIES_PATH)
        self._profiles: Dict[int, PlantCarbonProfile] = {}
        self._load_profiles()

    @staticmethod
    def _resolve_path(path: str) -> str:
        if os.path.exists(path):
            return path
        backend_rel = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), path)
        if os.path.exists(backend_rel):
            return backend_rel
        workspace_rel = os.path.join(os.getcwd(), "backend", path)
        if os.path.exists(workspace_rel):
            return workspace_rel
        return path

    def _load_profiles(self):
        if not os.path.exists(self._profiles_path):
            return
        with open(self._profiles_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for p in data.get("profiles", []):
                profile = PlantCarbonProfile.model_validate(p)
                self._profiles[profile.crop_id] = profile

    def get_carbon_profile(self, crop_id: int) -> Optional[PlantCarbonProfile]:
        """Fetch carbon growth parameters for species."""
        return self._profiles.get(crop_id)

    def calculate_projection(
        self,
        crop_id: int,
        scientific_name: str,
        common_name: str = "",
        horizon_years: int = 20,
        custom_profile: Optional[PlantCarbonProfile] = None,
    ) -> CarbonProjection:
        """
        Calculate 20-year biophysical carbon accumulation trajectory.
        Uses sigmoid biomass growth: AGB(t) = A_max / (1 + exp(-k * (t - t0))).
        """
        profile = custom_profile or self.get_carbon_profile(crop_id)
        if not profile:
            # Fallback to generalized agroforestry default profile
            profile = PlantCarbonProfile(
                crop_id=crop_id,
                scientific_name=scientific_name,
                common_name=common_name or scientific_name,
                max_above_ground_biomass_t_ha=180.0,
                growth_rate_k=0.25,
                inflection_year_t0=5.0,
                root_to_shoot_ratio=0.24,
                carbon_fraction=0.47,
                data_source="IPCC 2006 AFOLU Tier 1 Default",
                is_assumption=True,
                is_species_specific=False,
                confidence_rating=0.70,
            )

        trajectory: List[CarbonYearPoint] = []
        prev_cumulative_co2e = 0.0

        for yr in range(1, horizon_years + 1):
            # Sigmoid Above-Ground Biomass (AGB) in t/ha
            # AGB(t) = A_max / (1 + exp(-k * (t - t0)))
            exp_term = math.exp(-profile.growth_rate_k * (yr - profile.inflection_year_t0))
            agb = profile.max_above_ground_biomass_t_ha / (1.0 + exp_term)

            # Total Biomass = AGB * (1 + root_to_shoot_ratio)
            total_biomass = agb * (1.0 + profile.root_to_shoot_ratio)

            # Carbon Stock = Total Biomass * carbon_fraction
            carbon_stock = total_biomass * profile.carbon_fraction

            # Cumulative CO2e = Carbon Stock * (44 / 12)
            cumulative_co2e = carbon_stock * (44.0 / 12.0)

            # Annual Increment Delta
            annual_increment = max(0.0, cumulative_co2e - prev_cumulative_co2e)
            prev_cumulative_co2e = cumulative_co2e

            trajectory.append(
                CarbonYearPoint(
                    year=yr,
                    above_ground_biomass_t_ha=round(agb, 2),
                    total_biomass_t_ha=round(total_biomass, 2),
                    carbon_stock_t_ha=round(carbon_stock, 2),
                    cumulative_co2e_t_ha=round(cumulative_co2e, 2),
                    annual_co2e_increment_t_ha=round(annual_increment, 2),
                )
            )

        cumulative_20yr = trajectory[-1].cumulative_co2e_t_ha if trajectory else 0.0
        mean_annual = round(cumulative_20yr / horizon_years, 2) if horizon_years > 0 else 0.0

        return CarbonProjection(
            crop_id=crop_id,
            scientific_name=scientific_name,
            time_horizon_years=horizon_years,
            cumulative_20yr_co2e_t_ha=cumulative_20yr,
            mean_annual_co2e_t_ha=mean_annual,
            trajectory=trajectory,
            is_modeled_estimate=True,
            disclaimer=(
                "Estimated Biophysical Carbon Sequestration. Modeled estimate based on ecological assumptions. "
                "Does not constitute certified carbon credits or guaranteed offset revenue."
            ),
            confidence_rating=profile.confidence_rating,
        )


carbon_service = CarbonService()
