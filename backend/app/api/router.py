from fastapi import APIRouter
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.plants import router as plants_router
from app.api.v1.endpoints.land import router as land_router
from app.api.v1.endpoints.suitability import router as suitability_router
from app.api.v1.endpoints.plan import router as plan_router

api_router = APIRouter(prefix="/api/v1")

# Mount API endpoints
api_router.include_router(health_router)
api_router.include_router(plants_router)
api_router.include_router(land_router)
api_router.include_router(suitability_router)
api_router.include_router(plan_router)
