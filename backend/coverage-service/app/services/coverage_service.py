"""Coverage service for convex hull calculation."""

from typing import List, Optional, Tuple
from datetime import datetime
from app.models.geometry import Point, ConvexHullAlgorithms, ConvexHullResult
from app.models.warehouse import Warehouse
from app.models.schemas import CoverageResponse


class CoverageService:
    """Coverage calculation and management."""

    def __init__(self):
        self.last_coverage: Optional[CoverageResponse] = None
        self.last_warehouse_ids: List[str] = []
        self.algorithm = "monotonic_chain"
        self.cache_dirty = True

    def calculate_coverage(
        self,
        warehouses: List[Warehouse],
        algorithm: str = "monotonic_chain"
    ) -> CoverageResponse:
        """
        Calculate coverage area from warehouse locations.

        Args:
            warehouses: List of active warehouses
            algorithm: Convex hull algorithm to use

        Returns:
            Coverage polygon and metrics
        """
        self.algorithm = algorithm

        if not warehouses:
            return CoverageResponse()

        if len(warehouses) == 1:
            w = warehouses[0]
            return CoverageResponse(
                warehouse_ids=[w.id],
                polygon=[(w.latitude, w.longitude)],
                area_sq_degrees=0.0,
                perimeter_degrees=0.0,
                centroid=(w.latitude, w.longitude),
                algorithm=algorithm,
                warehouse_count=1,
            )

        # Convert warehouses to points
        points = [Point(w.latitude, w.longitude) for w in warehouses]

        # Calculate hull using selected algorithm
        hull_result = self._calculate_hull(points, algorithm)

        # Build response
        response = CoverageResponse(
            warehouse_ids=[w.id for w in warehouses],
            polygon=hull_result.to_polygon_coordinates(),
            area_sq_degrees=hull_result.area,
            perimeter_degrees=hull_result.perimeter,
            centroid=hull_result.centroid.to_tuple(),
            algorithm=algorithm,
            warehouse_count=len(warehouses),
            computed_at=datetime.utcnow(),
        )

        # Cache result
        self.last_coverage = response
        self.last_warehouse_ids = [w.id for w in warehouses]
        self.cache_dirty = False

        return response

    def _calculate_hull(self, points: List[Point], algorithm: str) -> ConvexHullResult:
        """Calculate convex hull using specified algorithm."""
        if algorithm == "monotonic_chain":
            return ConvexHullAlgorithms.monotonic_chain(points)
        elif algorithm == "graham_scan":
            return ConvexHullAlgorithms.graham_scan(points)
        elif algorithm == "jarvis_march":
            return ConvexHullAlgorithms.jarvis_march(points)
        elif algorithm == "quickhull":
            return ConvexHullAlgorithms.quickhull(points)
        else:
            return ConvexHullAlgorithms.monotonic_chain(points)

    def get_cached_coverage(self) -> Optional[CoverageResponse]:
        """Get cached coverage if available."""
        if not self.cache_dirty and self.last_coverage:
            return self.last_coverage
        return None

    def invalidate_cache(self) -> None:
        """Mark cache as dirty (when warehouses change)."""
        self.cache_dirty = True

    def point_in_polygon(self, lat: float, lon: float, polygon: List[Tuple[float, float]]) -> bool:
        """
        Check if point is inside polygon using ray casting algorithm.
        """
        if len(polygon) < 3:
            return False

        point = (lat, lon)
        x, y = point
        inside = False

        p1x, p1y = polygon[0]
        for i in range(1, len(polygon) + 1):
            p2x, p2y = polygon[i % len(polygon)]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def polygon_area_km2(self, polygon: List[Tuple[float, float]]) -> float:
        """
        Convert polygon area from square degrees to square kilometers.
        Approximate conversion: 1 degree ≈ 111.32 km at equator
        """
        area_sq_degrees = self.shoelace_area(polygon)
        # Rough approximation (varies by latitude)
        km_per_degree = 111.32
        return area_sq_degrees * (km_per_degree ** 2)

    @staticmethod
    def shoelace_area(polygon: List[Tuple[float, float]]) -> float:
        """Calculate polygon area using shoelace formula."""
        if len(polygon) < 3:
            return 0.0

        area = 0.0
        for i in range(len(polygon)):
            lat1, lon1 = polygon[i]
            lat2, lon2 = polygon[(i + 1) % len(polygon)]
            area += lat1 * lon2 - lat2 * lon1

        return abs(area) / 2.0

    def detect_expansion(
        self,
        old_polygon: Optional[List[Tuple[float, float]]],
        new_polygon: List[Tuple[float, float]]
    ) -> Tuple[bool, float]:
        """
        Detect if coverage has expanded.

        Returns:
            (expanded: bool, area_change: float)
        """
        if not old_polygon:
            return True, self.polygon_area_km2(new_polygon)

        old_area = self.polygon_area_km2(old_polygon)
        new_area = self.polygon_area_km2(new_polygon)
        change = new_area - old_area

        return change > 0, change
