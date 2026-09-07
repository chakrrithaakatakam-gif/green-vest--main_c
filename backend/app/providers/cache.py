"""
Spatial coordinate quantization cache for Open-Meteo climate and SoilGrids soil data.
Quantizes coordinates to ~1.1km grid cells (2 decimal places) and enforces 24h TTL.
"""

import os
import json
import sqlite3
import time
from typing import Optional, Dict, Any
from app.config import settings


class SpatialCache:
    """SQLite-backed spatial cache with coordinate quantization."""

    def __init__(self, db_path: Optional[str] = None, ttl_seconds: int = 86400):
        self.ttl_seconds = ttl_seconds or settings.CACHE_TTL_SECONDS
        self._db_path = self._resolve_path(db_path or settings.SPATIAL_CACHE_DB_PATH)
        self._init_db()

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
        return backend_rel

    def _init_db(self):
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS spatial_cache (
                cache_key TEXT PRIMARY KEY,
                data_type TEXT NOT NULL,
                data_json TEXT NOT NULL,
                cached_at REAL NOT NULL
            )
            """)
            conn.commit()

    @staticmethod
    def quantize_coordinate(lat: float, lon: float) -> str:
        """Round coordinates to 2 decimal places (~1.1 km resolution)."""
        return f"{round(lat, 2):.2f}_{round(lon, 2):.2f}"

    def get(self, data_type: str, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Retrieve unexpired cached data."""
        if not settings.ENABLE_PERSISTENT_CACHE:
            return None

        coord_key = self.quantize_coordinate(lat, lon)
        full_key = f"{data_type}_{coord_key}"
        now = time.time()

        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data_json, cached_at FROM spatial_cache WHERE cache_key = ?",
                    (full_key,)
                )
                row = cursor.fetchone()
                if not row:
                    return None
                data_json, cached_at = row
                if now - cached_at > self.ttl_seconds:
                    return None  # Expired
                return json.loads(data_json)
        except Exception:
            return None

    def set(self, data_type: str, lat: float, lon: float, data: Dict[str, Any]):
        """Persist data into cache."""
        if not settings.ENABLE_PERSISTENT_CACHE:
            return

        coord_key = self.quantize_coordinate(lat, lon)
        full_key = f"{data_type}_{coord_key}"
        now = time.time()

        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT OR REPLACE INTO spatial_cache (cache_key, data_type, data_json, cached_at)
                VALUES (?, ?, ?, ?)
                """, (full_key, data_type, json.dumps(data), now))
                conn.commit()
        except Exception:
            pass


spatial_cache = SpatialCache()
