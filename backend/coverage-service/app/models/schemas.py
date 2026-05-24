"""Pydantic schemas for API validation."""

from typing import List, Tuple, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class WarehouseCreate(BaseModel):
    """Schema for creating a warehouse."""
    name: str = Field(..., min_length=1, max_length=255)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    capacity: int = Field(default=10000, ge=0, le=1000000)
    status: str = Field(default="active", pattern="^(active|inactive|maintenance)$")
    region: str = Field(default="default")

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class WarehouseUpdate(BaseModel):
    """Schema for updating a warehouse."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    capacity: Optional[int] = Field(None, ge=0, le=1000000)
    status: Optional[str] = Field(None, pattern="^(active|inactive|maintenance)$")


class WarehouseResponse(BaseModel):
    """Schema for warehouse API response."""
    id: str
    name: str
    latitude: float
    longitude: float
    capacity: int
    status: str
    region: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PolygonPoint(BaseModel):
    """Single point in polygon."""
    latitude: float
    longitude: float


class CoverageResponse(BaseModel):
    """Schema for coverage API response."""
    warehouse_ids: List[str] = Field(default_factory=list)
    polygon: List[Tuple[float, float]] = Field(default_factory=list)
    area_sq_degrees: float = 0.0
    perimeter_degrees: float = 0.0
    centroid: Tuple[float, float] = (0.0, 0.0)
    algorithm: str = "monotonic_chain"
    computed_at: datetime = Field(default_factory=datetime.utcnow)
    warehouse_count: int = 0


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime
    services: dict


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    status_code: int
