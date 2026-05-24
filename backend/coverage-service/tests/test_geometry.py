"""Tests for convex hull algorithms."""

import pytest
from app.models.geometry import Point, ConvexHullAlgorithms


class TestConvexHull:
    """Test all convex hull algorithm implementations."""

    @pytest.fixture
    def square_points(self):
        """Square: 4 points."""
        return [
            Point(0, 0),
            Point(1, 0),
            Point(1, 1),
            Point(0, 1),
        ]

    @pytest.fixture
    def triangle_points(self):
        """Triangle: 3 points."""
        return [
            Point(0, 0),
            Point(2, 0),
            Point(1, 2),
        ]

    @pytest.fixture
    def irregular_points(self):
        """Irregular polygon with 10 points."""
        return [
            Point(0, 0),
            Point(1, 0.5),
            Point(2, 0),
            Point(3, 0.5),
            Point(3, 2),
            Point(2, 2.5),
            Point(1, 2),
            Point(0, 2),
            Point(-0.5, 1.5),
            Point(-0.5, 0.5),
        ]

    def test_monotonic_chain_square(self, square_points):
        """Test monotonic chain with square."""
        result = ConvexHullAlgorithms.monotonic_chain(square_points)
        assert len(result.vertices) == 4
        assert result.algorithm == "monotonic_chain"
        assert result.area > 0
        assert result.perimeter > 0

    def test_graham_scan_triangle(self, triangle_points):
        """Test Graham scan with triangle."""
        result = ConvexHullAlgorithms.graham_scan(triangle_points)
        assert len(result.vertices) == 3
        assert result.algorithm == "graham_scan"
        assert result.area > 0

    def test_jarvis_march_irregular(self, irregular_points):
        """Test Jarvis march with irregular polygon."""
        result = ConvexHullAlgorithms.jarvis_march(irregular_points)
        assert len(result.vertices) >= 3
        assert result.algorithm == "jarvis_march"
        assert result.area > 0

    def test_quickhull_square(self, square_points):
        """Test QuickHull with square."""
        result = ConvexHullAlgorithms.quickhull(square_points)
        assert len(result.vertices) == 4
        assert result.algorithm == "quickhull"
        assert result.area > 0

    def test_all_algorithms_same_result(self, irregular_points):
        """All algorithms should produce same area (within tolerance)."""
        mc = ConvexHullAlgorithms.monotonic_chain(irregular_points)
        gs = ConvexHullAlgorithms.graham_scan(irregular_points)
        jm = ConvexHullAlgorithms.jarvis_march(irregular_points)
        qh = ConvexHullAlgorithms.quickhull(irregular_points)

        # Areas should be approximately equal
        assert abs(mc.area - gs.area) < 0.01
        assert abs(mc.area - jm.area) < 0.01
        assert abs(mc.area - qh.area) < 0.01

    def test_single_point(self):
        """Single point should return that point."""
        points = [Point(5, 10)]
        result = ConvexHullAlgorithms.monotonic_chain(points)
        assert len(result.vertices) == 1

    def test_two_points(self):
        """Two points should return both."""
        points = [Point(0, 0), Point(1, 1)]
        result = ConvexHullAlgorithms.monotonic_chain(points)
        assert len(result.vertices) == 2

    def test_collinear_points(self):
        """Collinear points should form a line."""
        points = [
            Point(0, 0),
            Point(1, 1),
            Point(2, 2),
            Point(3, 3),
        ]
        result = ConvexHullAlgorithms.monotonic_chain(points)
        # Should reduce to endpoints
        assert result.area == 0.0

    def test_duplicate_points(self):
        """Should handle duplicate points."""
        points = [
            Point(0, 0),
            Point(1, 0),
            Point(1, 0),  # Duplicate
            Point(1, 1),
            Point(0, 1),
        ]
        result = ConvexHullAlgorithms.monotonic_chain(points)
        assert len(result.vertices) >= 3
        assert result.area > 0

    def test_centroid_calculation(self, square_points):
        """Centroid should be at center of polygon."""
        result = ConvexHullAlgorithms.monotonic_chain(square_points)
        # Square centroid should be near (0.5, 0.5)
        assert 0.4 < result.centroid.latitude < 0.6
        assert 0.4 < result.centroid.longitude < 0.6

    def test_to_polygon_coordinates(self, triangle_points):
        """Should convert vertices to list of tuples."""
        result = ConvexHullAlgorithms.monotonic_chain(triangle_points)
        coords = result.to_polygon_coordinates()
        assert len(coords) == 3
        assert all(isinstance(c, tuple) for c in coords)
        assert all(len(c) == 2 for c in coords)
