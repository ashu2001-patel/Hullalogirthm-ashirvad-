"""Warehouse service for CRUD operations."""

from typing import List, Optional, Dict
from datetime import datetime
from app.models.warehouse import Warehouse
from app.models.schemas import WarehouseCreate, WarehouseUpdate


class WarehouseService:
    """In-memory warehouse management (Phase 1-3)."""

    def __init__(self):
        self.warehouses: Dict[str, Warehouse] = {}

    def create(self, data: WarehouseCreate) -> Warehouse:
        """Create a new warehouse."""
        warehouse = Warehouse(
            name=data.name,
            latitude=data.latitude,
            longitude=data.longitude,
            capacity=data.capacity,
            status=data.status,
            region=data.region,
        )
        self.warehouses[warehouse.id] = warehouse
        return warehouse

    def get(self, warehouse_id: str) -> Optional[Warehouse]:
        """Get warehouse by ID."""
        return self.warehouses.get(warehouse_id)

    def get_all(self) -> List[Warehouse]:
        """Get all warehouses."""
        return list(self.warehouses.values())

    def get_active(self) -> List[Warehouse]:
        """Get all active warehouses."""
        return [w for w in self.warehouses.values() if w.status == "active"]

    def update(self, warehouse_id: str, data: WarehouseUpdate) -> Optional[Warehouse]:
        """Update a warehouse."""
        warehouse = self.warehouses.get(warehouse_id)
        if not warehouse:
            return None

        if data.name is not None:
            warehouse.name = data.name
        if data.capacity is not None:
            warehouse.capacity = data.capacity
        if data.status is not None:
            warehouse.status = data.status

        warehouse.updated_at = datetime.utcnow()
        return warehouse

    def delete(self, warehouse_id: str) -> bool:
        """Delete a warehouse."""
        if warehouse_id in self.warehouses:
            del self.warehouses[warehouse_id]
            return True
        return False

    def count(self) -> int:
        """Get total warehouse count."""
        return len(self.warehouses)

    def exists(self, warehouse_id: str) -> bool:
        """Check if warehouse exists."""
        return warehouse_id in self.warehouses

    def clear(self) -> None:
        """Clear all warehouses (for testing)."""
        self.warehouses.clear()
