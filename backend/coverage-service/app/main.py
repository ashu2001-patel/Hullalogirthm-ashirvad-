"""FastAPI application for coverage service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from datetime import datetime
from app.routers import warehouses, coverage, health
from app.models.schemas import HealthResponse

# Create FastAPI app
app = FastAPI(
    title="Geospatial Delivery Coverage API",
    description="Real-time delivery coverage area calculation using computational geometry",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gzip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(warehouses.router, prefix="/api/v1", tags=["warehouses"])
app.include_router(coverage.router, prefix="/api/v1", tags=["coverage"])


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint."""
    return {
        "service": "Geospatial Delivery Coverage API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


# Startup events commented out to avoid issues
# @app.on_event("startup")
# async def startup_event():
#     """Application startup."""
#     pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
