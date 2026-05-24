"""Coverage calculation endpoints."""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from app.models.schemas import CoverageResponse
from app.services import warehouse_service, coverage_service

router = APIRouter()


@router.get("/coverage", response_model=CoverageResponse)
async def get_coverage(
    algorithm: str = Query("monotonic_chain", pattern="^(monotonic_chain|graham_scan|jarvis_march|quickhull)$")
):
    """
    Get current delivery coverage area.

    Query Parameters:
    - algorithm: Convex hull algorithm (monotonic_chain, graham_scan, jarvis_march, quickhull)

    Returns:
    - polygon: List of (latitude, longitude) vertices
    - area_sq_degrees: Area of coverage polygon
    - perimeter_degrees: Perimeter of polygon
    - centroid: Center point of polygon
    - warehouse_count: Number of warehouses contributing
    """
    active_warehouses = warehouse_service.get_active()

    if not active_warehouses:
        return CoverageResponse()

    return coverage_service.calculate_coverage(active_warehouses, algorithm)


@router.post("/coverage/recalculate", response_model=dict)
async def recalculate_coverage(
    algorithm: str = Query("monotonic_chain", pattern="^(monotonic_chain|graham_scan|jarvis_march|quickhull)$"),
    force: bool = Query(False)
):
    """
    Force recalculation of coverage area.

    Query Parameters:
    - algorithm: Which convex hull algorithm to use
    - force: Force recalculation even if cached

    Returns:
    - coverage: New coverage polygon and metrics
    - change: Change from previous coverage (if any)
    """
    if force:
        coverage_service.invalidate_cache()

    active_warehouses = warehouse_service.get_active()

    if not active_warehouses:
        raise HTTPException(status_code=400, detail="No active warehouses")

    new_coverage = coverage_service.calculate_coverage(active_warehouses, algorithm)

    old_polygon = coverage_service.last_coverage.polygon if coverage_service.last_coverage else None
    expanded, area_change = coverage_service.detect_expansion(old_polygon, new_coverage.polygon)

    return {
        "message": "Coverage recalculated successfully",
        "coverage": new_coverage,
        "change": {
            "expanded": expanded,
            "area_change_km2": coverage_service.polygon_area_km2(new_coverage.polygon),
            "timestamp": datetime.utcnow().isoformat()
        }
    }


@router.get("/coverage/polygon", response_model=dict)
async def get_coverage_polygon():
    """
    Get coverage polygon coordinates in GeoJSON format.

    Returns GeoJSON Feature object.
    """
    active_warehouses = warehouse_service.get_active()

    if not active_warehouses:
        return {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": []
            },
            "properties": {
                "warehouse_count": 0,
                "area_sq_km": 0.0
            }
        }

    coverage = coverage_service.calculate_coverage(active_warehouses)

    # Convert to GeoJSON format (lon, lat order)
    coordinates = [[(lon, lat) for lat, lon in coverage.polygon]]

    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": coordinates
        },
        "properties": {
            "warehouse_count": coverage.warehouse_count,
            "area_sq_km": coverage_service.polygon_area_km2(coverage.polygon),
            "centroid": {
                "latitude": coverage.centroid[0],
                "longitude": coverage.centroid[1]
            },
            "algorithm": coverage.algorithm,
            "computed_at": coverage.computed_at.isoformat()
        }
    }


@router.get("/coverage/metrics", response_model=dict)
async def get_coverage_metrics():
    """Get coverage statistics and metrics."""
    active_warehouses = warehouse_service.get_active()
    coverage = coverage_service.calculate_coverage(active_warehouses)

    area_km2 = coverage_service.polygon_area_km2(coverage.polygon)

    return {
        "warehouse_count": coverage.warehouse_count,
        "area_sq_km": area_km2,
        "perimeter_km": coverage.perimeter_degrees * 111.32,  # Rough conversion
        "centroid": {
            "latitude": coverage.centroid[0],
            "longitude": coverage.centroid[1]
        },
        "algorithm": coverage.algorithm,
        "computed_at": coverage.computed_at.isoformat()
    }


@router.post("/coverage/point-in-polygon", response_model=dict)
async def check_point_in_polygon(latitude: float, longitude: float):
    """Check if a point is inside the coverage polygon."""
    active_warehouses = warehouse_service.get_active()

    if not active_warehouses:
        return {
            "point": {"latitude": latitude, "longitude": longitude},
            "inside_coverage": False,
            "message": "No active warehouses"
        }

    coverage = coverage_service.calculate_coverage(active_warehouses)
    inside = coverage_service.point_in_polygon(latitude, longitude, coverage.polygon)

    return {
        "point": {"latitude": latitude, "longitude": longitude},
        "inside_coverage": inside,
        "warehouse_count": coverage.warehouse_count,
        "timestamp": datetime.utcnow().isoformat()
    }
