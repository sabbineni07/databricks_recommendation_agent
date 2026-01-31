"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.config.settings import settings
from shared.utils.logging import get_logger
from API.src.routes import recommendations, health

logger = get_logger(__name__)

app = FastAPI(
    title="Databricks Recommendation Agent API",
    description="AI-powered cluster configuration recommendations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(health.router, prefix="/api/health", tags=["health"])


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("application_startup", env=settings.app_env)


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("application_shutdown")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "API.src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.app_env == "development"
    )

