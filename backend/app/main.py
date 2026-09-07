from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.router import api_router


# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("greenvest")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown routines."""
    logger.info(
        "Starting GreenVest API Server v%s [%s]",
        settings.APP_VERSION,
        settings.ENVIRONMENT
    )

    yield

    logger.info("Shutting down GreenVest API Server")


def create_app() -> FastAPI:
    """FastAPI application factory."""

    app = FastAPI(
        title="GreenVest API",
        description="Land-to-Carbon Intelligence & Investment Planner API",
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API routes
    app.include_router(api_router)

    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "message": "Welcome to GreenVest API — Land-to-Carbon Intelligence & Investment Planner",
            "docs": "/docs",
            "health": "/api/v1/health",
            "version": settings.APP_VERSION
        }

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception
    ):
        logger.error(
            "Unhandled Exception at %s: %s",
            request.url.path,
            str(exc),
            exc_info=True
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": (
                    str(exc)
                    if settings.DEBUG
                    else "An unexpected error occurred."
                )
            }
        )

    return app


# Create FastAPI application
app = create_app()


# Allow running this file directly
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )