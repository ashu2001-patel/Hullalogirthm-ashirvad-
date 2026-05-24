"""Demo script to showcase the geospatial system."""

import requests
import json
from time import sleep
import sys

BASE_URL = "http://127.0.0.1:8001"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo():
    """Run demonstration of the system."""

    print_section("GEOSPATIAL DELIVERY COVERAGE SYSTEM - LIVE DEMO")

    # 1. Health check
    print_section("1. Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(json.dumps(response.json(), indent=2))

    # 2. Add warehouses
    print_section("2. Adding Warehouses")

    warehouses = [
        {
            "name": "Mumbai Central Hub",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "capacity": 10000,
            "status": "active"
        },
        {
            "name": "Mumbai South Hub",
            "latitude": 12.9352,
            "longitude": 77.6245,
            "capacity": 8000,
            "status": "active"
        },
        {
            "name": "Mumbai East Hub",
            "latitude": 13.0827,
            "longitude": 77.6151,
            "capacity": 12000,
            "status": "active"
        },
    ]

    warehouse_ids = []
    for warehouse in warehouses:
        response = requests.post(f"{BASE_URL}/api/v1/warehouses", json=warehouse)
        data = response.json()
        warehouse_ids.append(data['id'])
        print("[OK] Created: {} ({})".format(data['name'], data['id']))
        print("     Location: {:.4f}, {:.4f}".format(data['latitude'], data['longitude']))

    # 3. List warehouses
    print_section("3. Warehouse Statistics")
    response = requests.get(f"{BASE_URL}/api/v1/warehouses/stats")
    stats = response.json()
    print("Total Warehouses: {}".format(stats['total_warehouses']))
    print("Active Warehouses: {}".format(stats['active_warehouses']))
    print("Total Capacity: {:,} orders/day".format(stats['total_capacity']))
    print("Average Capacity: {:.0f} orders/day".format(stats['average_capacity']))

    # 4. Calculate coverage (using different algorithms)
    print_section("4. Coverage Calculation - Algorithm Comparison")

    algorithms = ["monotonic_chain", "graham_scan", "jarvis_march", "quickhull"]

    for algo in algorithms:
        response = requests.get(f"{BASE_URL}/api/v1/coverage?algorithm={algo}")
        coverage = response.json()

        print("\n[{}]".format(algo.upper()))
        print("   Polygon Vertices: {}".format(len(coverage['polygon'])))
        print("   Area: {:.4f} sq degrees".format(coverage['area_sq_degrees']))
        print("   Perimeter: {:.4f} degrees".format(coverage['perimeter_degrees']))
        print("   Centroid: ({:.4f}, {:.4f})".format(coverage['centroid'][0], coverage['centroid'][1]))

    # 5. Get coverage as GeoJSON
    print_section("5. Coverage Polygon (GeoJSON Format)")
    response = requests.get(f"{BASE_URL}/api/v1/coverage/polygon")
    geojson = response.json()
    print(json.dumps(geojson, indent=2))

    # 6. Coverage metrics
    print_section("6. Coverage Metrics")
    response = requests.get(f"{BASE_URL}/api/v1/coverage/metrics")
    metrics = response.json()
    print(json.dumps(metrics, indent=2))

    # 7. Point-in-polygon check
    print_section("7. Point-in-Coverage Check")

    test_points = [
        (12.97, 77.59, "Inside expected coverage"),
        (12.95, 77.61, "Inside expected coverage"),
        (15.0, 75.0, "Outside coverage (far away)"),
    ]

    for lat, lon, desc in test_points:
        response = requests.get(f"{BASE_URL}/api/v1/coverage/point-in-polygon?latitude={lat}&longitude={lon}")
        result = response.json()
        status = "[INSIDE]" if result['inside_coverage'] else "[OUTSIDE]"
        print("{}: ({}, {}) - {}".format(status, lat, lon, desc))

    # 8. Add another warehouse and show expansion detection
    print_section("8. Expansion Detection - Adding New Warehouse")

    new_warehouse = {
        "name": "Mumbai North Hub (New)",
        "latitude": 13.1939,
        "longitude": 77.6245,
        "capacity": 5000,
        "status": "active"
    }

    response = requests.post(f"{BASE_URL}/api/v1/warehouses", json=new_warehouse)
    new_wh = response.json()
    print("[OK] Added: {}".format(new_wh['name']))

    response = requests.post(f"{BASE_URL}/api/v1/coverage/recalculate?force=true")
    result = response.json()

    print("\nCoverage Changed:")
    print("   New Area: {:.4f} sq degrees".format(result['coverage']['area_sq_degrees']))
    print("   Expanded: {}".format(result['change']['expanded']))
    print("   Change: {:+.2f} km2".format(result['change']['area_change_km2']))

    # 9. Summary
    print_section("DEMO COMPLETE - SUCCESS")
    print("""
The system successfully demonstrated:
  [OK] Creating warehouses
  [OK] Calculating convex hull coverage using 4 algorithms
  [OK] Converting to GeoJSON format
  [OK] Point-in-polygon queries
  [OK] Expansion detection
  [OK] Coverage metrics calculation

Backend API: http://127.0.0.1:8001/docs
Database: PostgreSQL + PostGIS (Phase 5+)
Frontend: React + Leaflet (Phase 4+)
    """)


if __name__ == "__main__":
    try:
        demo()
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to server at http://127.0.0.1:8001")
        print("\nMake sure the backend is running:")
        print("  cd backend/coverage-service")
        print("  python -m uvicorn app.main:app --host 127.0.0.1 --port 8001")
        sys.exit(1)
    except Exception as e:
        print("[ERROR] {}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
