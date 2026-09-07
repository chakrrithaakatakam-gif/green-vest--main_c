"""
ECOCROP botanical data access service.
Queries SQLite database for plant requirements and summaries.
"""

import os
import sqlite3
from typing import List, Optional, Tuple
from app.config import settings
from app.models.domain.plant import PlantRequirement, PlantSummary


class EcocropService:
    """Provides thread-safe access to FAO ECOCROP botanical knowledge base."""

    def __init__(self, db_path: Optional[str] = None):
        self._db_path = self._resolve_path(db_path or settings.ECOCROP_DB_PATH)

    @staticmethod
    def _resolve_path(path: str) -> str:
        """Resolve database path relative to workspace or backend directory."""
        if os.path.exists(path):
            return path
        backend_rel = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), path)
        if os.path.exists(backend_rel):
            return backend_rel
        workspace_rel = os.path.join(os.getcwd(), "backend", path)
        if os.path.exists(workspace_rel):
            return workspace_rel
        return path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_plant_by_id(self, crop_id: int) -> Optional[PlantRequirement]:
        """Fetch a single plant requirement by crop_id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM plants WHERE crop_id = ?", (crop_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_requirement(row)

    def list_plants(
        self,
        limit: int = 50,
        offset: int = 0,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[PlantSummary], int]:
        """Fetch paginated plant summaries with optional category and search filters."""
        query = "SELECT * FROM plants WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM plants WHERE 1=1"
        params: list = []

        if category:
            query += " AND LOWER(use_category) = LOWER(?)"
            count_query += " AND LOWER(use_category) = LOWER(?)"
            params.append(category)

        if search:
            query += " AND (LOWER(common_name) LIKE ? OR LOWER(scientific_name) LIKE ?)"
            count_query += " AND (LOWER(common_name) LIKE ? OR LOWER(scientific_name) LIKE ?)"
            term = f"%{search.lower()}%"
            params.extend([term, term])

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]

            query += " ORDER BY common_name ASC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            cursor.execute(query, params)
            rows = cursor.fetchall()

            summaries = [self._row_to_summary(r) for r in rows]
            return summaries, total_count

    def get_all_plant_requirements(
        self,
        crop_ids: Optional[List[int]] = None,
        use_category: Optional[str] = None,
    ) -> List[PlantRequirement]:
        """Fetch full plant requirements for evaluation."""
        query = "SELECT * FROM plants WHERE 1=1"
        params: list = []

        if crop_ids:
            placeholders = ",".join("?" for _ in crop_ids)
            query += f" AND crop_id IN ({placeholders})"
            params.extend(crop_ids)

        if use_category:
            query += " AND LOWER(use_category) = LOWER(?)"
            params.append(use_category)

        query += " ORDER BY crop_id ASC"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_requirement(r) for r in rows]

    @staticmethod
    def _row_to_requirement(row: sqlite3.Row) -> PlantRequirement:
        return PlantRequirement(
            crop_id=row["crop_id"],
            scientific_name=row["scientific_name"],
            common_name=row["common_name"],
            use_category=row["use_category"],
            life_form=row["life_form"],
            growth_cycle_days_min=row["growth_cycle_days_min"],
            growth_cycle_days_max=row["growth_cycle_days_max"],
            RMIN=row["rainfall_min"],
            ROPMN=row["rainfall_opt_min"],
            ROPMX=row["rainfall_opt_max"],
            RMAX=row["rainfall_max"],
            TMIN=row["temp_min"],
            TOPMN=row["temp_opt_min"],
            TOPMX=row["temp_opt_max"],
            TMAX=row["temp_max"],
            PHMIN=row["ph_min"],
            PHOPMN=row["ph_opt_min"],
            PHOPMX=row["ph_opt_max"],
            PHMAX=row["ph_max"],
            has_complete_optimal_ranges=bool(row["has_complete_optimal_ranges"]),
            source=row["source"],
        )

    @staticmethod
    def _row_to_summary(row: sqlite3.Row) -> PlantSummary:
        return PlantSummary(
            crop_id=row["crop_id"],
            scientific_name=row["scientific_name"],
            common_name=row["common_name"],
            use_category=row["use_category"],
            life_form=row["life_form"],
            rainfall_range=f"{row['rainfall_min']:.0f} - {row['rainfall_max']:.0f} mm",
            temp_range=f"{row['temp_min']:.0f} - {row['temp_max']:.0f} °C",
            ph_range=f"{row['ph_min']:.1f} - {row['ph_max']:.1f}",
            has_complete_optimal_ranges=bool(row["has_complete_optimal_ranges"]),
        )


# Global singleton
ecocrop_service = EcocropService()
