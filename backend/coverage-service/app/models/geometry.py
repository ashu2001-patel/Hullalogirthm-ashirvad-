"""Geometry models and convex hull algorithms."""

from typing import List, Tuple, Optional
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Point:
    """2D geographic point (latitude, longitude)."""
    latitude: float
    longitude: float

    def __repr__(self) -> str:
        return f"Point({self.latitude:.4f}, {self.longitude:.4f})"

    def to_tuple(self) -> Tuple[float, float]:
        return (self.latitude, self.longitude)

    def __hash__(self) -> int:
        return hash((round(self.latitude, 6), round(self.longitude, 6)))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Point):
            return False
        return (abs(self.latitude - other.latitude) < 1e-6 and
                abs(self.longitude - other.longitude) < 1e-6)

    def distance_to(self, other: 'Point') -> float:
        """Euclidean distance to another point (in degrees, approximation)."""
        lat_diff = self.latitude - other.latitude
        lon_diff = self.longitude - other.longitude
        return math.sqrt(lat_diff**2 + lon_diff**2)


@dataclass
class ConvexHullResult:
    """Result of convex hull computation."""
    vertices: List[Point]  # Hull vertices in counterclockwise order
    area: float  # Area in square degrees
    perimeter: float  # Perimeter in degrees
    algorithm: str  # Which algorithm was used
    centroid: Point  # Center of polygon

    def to_polygon_coordinates(self) -> List[Tuple[float, float]]:
        """Return vertices as list of (lat, lon) tuples."""
        return [p.to_tuple() for p in self.vertices]


class ConvexHullAlgorithms:
    """Implementation of 4 convex hull algorithms."""

    @staticmethod
    def _cross_product(o: Point, a: Point, b: Point) -> float:
        """
        Calculate cross product of vectors OA and OB.
        Positive: counterclockwise (left turn)
        Negative: clockwise (right turn)
        Zero: collinear
        """
        return (a.latitude - o.latitude) * (b.longitude - o.longitude) - \
               (a.longitude - o.longitude) * (b.latitude - o.latitude)

    @staticmethod
    def _compute_metrics(hull_points: List[Point]) -> Tuple[float, float, Point]:
        """Compute area, perimeter, and centroid of polygon."""
        if len(hull_points) < 3:
            return 0.0, 0.0, Point(0, 0)

        # Close the polygon
        points = hull_points + [hull_points[0]]

        # Shoelace formula for area
        area = 0.0
        for i in range(len(points) - 1):
            area += (points[i].latitude * points[i + 1].longitude -
                    points[i + 1].latitude * points[i].longitude)
        area = abs(area) / 2.0

        # Perimeter (sum of distances)
        perimeter = 0.0
        for i in range(len(points) - 1):
            perimeter += points[i].distance_to(points[i + 1])

        # Centroid
        cx, cy = 0.0, 0.0
        for i in range(len(points) - 1):
            cross = (points[i].latitude * points[i + 1].longitude -
                    points[i + 1].latitude * points[i].longitude)
            cx += (points[i].latitude + points[i + 1].latitude) * cross
            cy += (points[i].longitude + points[i + 1].longitude) * cross

        if area != 0:
            cx /= (6 * area)
            cy /= (6 * area)
        else:
            cx = sum(p.latitude for p in hull_points) / len(hull_points)
            cy = sum(p.longitude for p in hull_points) / len(hull_points)

        centroid = Point(cx, cy)
        return area, perimeter, centroid

    @staticmethod
    def monotonic_chain(points: List[Point]) -> ConvexHullResult:
        """
        Monotonic Chain (Andrew's algorithm) - RECOMMENDED
        Time: O(n log n), Space: O(n)
        Fastest in practice, most reliable.
        """
        if len(points) <= 2:
            return ConvexHullResult(points, 0.0, 0.0, "monotonic_chain",
                                   Point(0, 0))

        # Sort points lexicographically
        sorted_points = sorted(points, key=lambda p: (p.latitude, p.longitude))

        # Build lower hull
        lower = []
        for p in sorted_points:
            while len(lower) >= 2 and ConvexHullAlgorithms._cross_product(
                    lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)

        # Build upper hull
        upper = []
        for p in reversed(sorted_points):
            while len(upper) >= 2 and ConvexHullAlgorithms._cross_product(
                    upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)

        # Remove last point of each half because it's repeated
        hull = lower[:-1] + upper[:-1]

        if len(hull) < 3:
            return ConvexHullResult(sorted_points, 0.0, 0.0, "monotonic_chain",
                                   Point(0, 0))

        area, perimeter, centroid = ConvexHullAlgorithms._compute_metrics(hull)
        return ConvexHullResult(hull, area, perimeter, "monotonic_chain", centroid)

    @staticmethod
    def graham_scan(points: List[Point]) -> ConvexHullResult:
        """
        Graham Scan
        Time: O(n log n), Space: O(n)
        Classic, educational algorithm.
        """
        if len(points) <= 2:
            return ConvexHullResult(points, 0.0, 0.0, "graham_scan", Point(0, 0))

        # Find point with lowest y-coordinate (longitude)
        start = min(points, key=lambda p: (p.longitude, p.latitude))

        # Sort points by polar angle with respect to start
        def polar_angle_key(p):
            if p == start:
                return -math.pi, 0
            angle = math.atan2(p.longitude - start.longitude,
                              p.latitude - start.latitude)
            dist = start.distance_to(p)
            return angle, dist

        sorted_points = sorted(points, key=polar_angle_key)

        # Build hull using stack
        hull = []
        for p in sorted_points:
            while len(hull) >= 2 and ConvexHullAlgorithms._cross_product(
                    hull[-2], hull[-1], p) <= 0:
                hull.pop()
            hull.append(p)

        if len(hull) < 3:
            return ConvexHullResult(sorted_points, 0.0, 0.0, "graham_scan",
                                   Point(0, 0))

        area, perimeter, centroid = ConvexHullAlgorithms._compute_metrics(hull)
        return ConvexHullResult(hull, area, perimeter, "graham_scan", centroid)

    @staticmethod
    def jarvis_march(points: List[Point]) -> ConvexHullResult:
        """
        Jarvis March (Gift Wrapping)
        Time: O(n × h) where h = hull vertices, Space: O(h)
        Best when hull is small. Intuitive algorithm.
        """
        if len(points) <= 2:
            return ConvexHullResult(points, 0.0, 0.0, "jarvis_march", Point(0, 0))

        # Find leftmost point
        l = min(range(len(points)), key=lambda i: (points[i].latitude,
                                                    points[i].longitude))

        hull = []
        p = l

        while True:
            hull.append(points[p])

            # Find the most counterclockwise point from current
            q = (p + 1) % len(points)

            for i in range(len(points)):
                if ConvexHullAlgorithms._cross_product(points[p], points[i],
                                                       points[q]) > 0:
                    q = i

            p = q

            # Stop when we wrap back to starting point
            if p == l:
                break

        if len(hull) < 3:
            return ConvexHullResult(points, 0.0, 0.0, "jarvis_march", Point(0, 0))

        area, perimeter, centroid = ConvexHullAlgorithms._compute_metrics(hull)
        return ConvexHullResult(hull, area, perimeter, "jarvis_march", centroid)

    @staticmethod
    def quickhull(points: List[Point]) -> ConvexHullResult:
        """
        QuickHull
        Time: O(n log n) average, O(n²) worst, Space: O(log n)
        Divide and conquer approach. Fast in practice.
        """
        if len(points) <= 2:
            return ConvexHullResult(points, 0.0, 0.0, "quickhull", Point(0, 0))

        def quickhull_helper(pts: List[Point], p1: Point, p2: Point) -> List[Point]:
            if not pts:
                return []

            # Find point with maximum distance from line p1-p2
            max_dist = -1
            max_point = None

            for p in pts:
                # Distance from point to line
                dist = abs(ConvexHullAlgorithms._cross_product(p1, p2, p))
                if dist > max_dist:
                    max_dist = dist
                    max_point = p

            if max_point is None:
                return []

            # Partition points
            left_set = []
            for p in pts:
                if ConvexHullAlgorithms._cross_product(p1, max_point, p) > 0:
                    left_set.append(p)

            right_set = []
            for p in pts:
                if ConvexHullAlgorithms._cross_product(max_point, p2, p) > 0:
                    right_set.append(p)

            # Recursively find hull
            return (quickhull_helper(left_set, p1, max_point) +
                   [max_point] +
                   quickhull_helper(right_set, max_point, p2))

        # Find leftmost and rightmost points
        min_point = min(points, key=lambda p: (p.latitude, p.longitude))
        max_point = max(points, key=lambda p: (p.latitude, p.longitude))

        # Partition into upper and lower
        upper = []
        lower = []

        for p in points:
            if ConvexHullAlgorithms._cross_product(min_point, max_point, p) >= 0:
                upper.append(p)
            else:
                lower.append(p)

        # Compute hull for each partition
        hull = ([min_point] +
               quickhull_helper(upper, min_point, max_point) +
               [max_point] +
               quickhull_helper(lower, max_point, min_point))

        # Remove duplicates while preserving order
        seen = set()
        hull = [p for p in hull if not (p in seen or seen.add(p))]

        if len(hull) < 3:
            return ConvexHullResult(points, 0.0, 0.0, "quickhull", Point(0, 0))

        area, perimeter, centroid = ConvexHullAlgorithms._compute_metrics(hull)
        return ConvexHullResult(hull, area, perimeter, "quickhull", centroid)
