"""Warehouse data models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4


@dataclass
class Warehouse:
    """Warehouse domain model."""
    id: str = field(default_factory=lambda: str(uuid4())[:8])
    name: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    capacity: int = 0  # Daily delivery capacity
    status: str = "active"  # active, inactive, maintenance
    region: str = "default"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Warehouse):
            return self.id == other.id
        return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "capacity": self.capacity,
            "status": self.status,
            "region": self.region,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
