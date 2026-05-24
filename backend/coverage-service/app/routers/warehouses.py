"""Warehouse management endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from datetime import datetime
from app.models.schemas import (
    WarehouseCreate, WarehouseUpdate, WarehouseResponse
)
from app.services import warehouse_service

router = APIRouter()


@router.post("/warehouses", response_model=WarehouseResponse, status_code=201)
async def create_warehouse(data: WarehouseCreate):
    """
    Create a new warehouse.

    Example:
    ```json
    {
      "name": "Mumbai Central Hub",
      "latitude": 12.9716,
      "longitude": 77.5946,
      "capacity": 10000,
      "status": "active"
    }
    ```
    """
    warehouse = warehouse_service.create(data)
    return warehouse.to_dict()


@router.get("/warehouses/stats", response_model=dict)
async def warehouse_stats():
    """Get warehouse statistics."""
    all_warehouses = warehouse_service.get_all()
    active = [w for w in all_warehouses if w.status == "active"]

    total_capacity = sum(w.capacity for w in all_warehouses)
    avg_capacity = total_capacity / len(all_warehouses) if all_warehouses else 0

    return {
        "total_warehouses": len(all_warehouses),
        "active_warehouses": len(active),
        "inactive_warehouses": len(all_warehouses) - len(active),
        "total_capacity": total_capacity,
        "average_capacity": avg_capacity,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/warehouses", response_model=dict)
async def list_warehouses(status: str = Query(None, pattern="^(active|inactive|maintenance|all)$")):
    """
    List all warehouses.

    Query Parameters:
    - status: Filter by status (active, inactive, maintenance, or all)
    """
    if status and status != "all":
        warehouses = [w for w in warehouse_service.get_all() if w.status == status]
    else:
        warehouses = warehouse_service.get_all()

    return {
        "count": len(warehouses),
        "warehouses": [w.to_dict() for w in warehouses]
    }


@router.get("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(warehouse_id: str):
    """Get a specific warehouse by ID."""
    warehouse = warehouse_service.get(warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse.to_dict()


@router.put("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(warehouse_id: str, data: WarehouseUpdate):
    """Update a warehouse."""
    warehouse = warehouse_service.update(warehouse_id, data)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse.to_dict()


@router.delete("/warehouses/{warehouse_id}", status_code=200)
async def delete_warehouse(warehouse_id: str):
    """Delete a warehouse."""
    if not warehouse_service.delete(warehouse_id):
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return {"message": "Warehouse deleted successfully", "id": warehouse_id}


@router.delete("/warehouses", status_code=200)
async def clear_all_warehouses():
    """Clear all warehouses (for testing)."""
    warehouse_service.clear()
    return {"message": "All warehouses cleared", "timestamp": datetime.utcnow().isoformat()}
