#!/usr/bin/env python
"""Generate random warehouse test data around a center point.

Useful for stress-testing the convex hull algorithms with many points.

Examples:
    # Write 500 random warehouses near Bangalore to a CSV
    python scripts/generate_test_data.py --count 500 --out data/generated.csv

    # Generate 1000 points and POST them straight into the API (clears first)
    python scripts/generate_test_data.py --count 1000 --post --clear

    # Cluster around Delhi with a wider 0.5-degree spread
    python scripts/generate_test_data.py --count 200 --center-lat 28.70 --center-lon 77.10 --spread 0.5 --out data/delhi.csv
"""

import argparse
import csv
import random
import sys


def generate(count, center_lat, center_lon, spread, gaussian):
    rows = []
    for i in range(count):
        if gaussian:
            # Gaussian cluster: dense in the middle, sparse at edges
            lat = center_lat + random.gauss(0, spread / 3)
            lon = center_lon + random.gauss(0, spread / 3)
        else:
            # Uniform square spread
            lat = center_lat + random.uniform(-spread, spread)
            lon = center_lon + random.uniform(-spread, spread)
        # Clamp to valid ranges
        lat = max(-90.0, min(90.0, lat))
        lon = max(-180.0, min(180.0, lon))
        rows.append({
            "name": f"Warehouse-{i+1:04d}",
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "capacity": random.randint(3000, 20000),
            "region": "generated",
            "status": "active",
        })
    return rows


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "latitude", "longitude", "capacity", "region", "status"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"[OK] Wrote {len(rows)} warehouses to {path}")


def post_rows(rows, base_url, clear):
    try:
        import requests
    except ImportError:
        print("[ERROR] 'requests' not installed. Run: pip install requests")
        sys.exit(1)

    api = base_url.rstrip("/") + "/api/v1"
    if clear:
        try:
            requests.delete(f"{api}/warehouses", timeout=5)
            print("[OK] Cleared existing warehouses")
        except Exception as e:
            print(f"[WARN] Could not clear: {e}")

    added = 0
    for row in rows:
        try:
            r = requests.post(f"{api}/warehouses", json=row, timeout=5)
            if r.status_code == 201:
                added += 1
        except Exception as e:
            print(f"[ERROR] {row['name']}: {e}")
    print(f"[OK] Posted {added}/{len(rows)} warehouses to {api}")

    try:
        cov = requests.get(f"{api}/coverage", timeout=10).json()
        print(f"Coverage: {len(cov.get('polygon', []))} hull vertices from {cov.get('warehouse_count', 0)} points")
    except Exception as e:
        print(f"[WARN] Could not fetch coverage: {e}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Generate random warehouse test data")
    p.add_argument("--count", type=int, default=100, help="Number of warehouses (default 100)")
    p.add_argument("--center-lat", type=float, default=12.9716, help="Center latitude (default Bangalore)")
    p.add_argument("--center-lon", type=float, default=77.5946, help="Center longitude")
    p.add_argument("--spread", type=float, default=0.3, help="Spread in degrees (default 0.3 ~33km)")
    p.add_argument("--gaussian", action="store_true", help="Cluster densely in the middle (default uniform)")
    p.add_argument("--out", help="Write to this CSV file")
    p.add_argument("--post", action="store_true", help="POST directly to the API")
    p.add_argument("--clear", action="store_true", help="Clear existing before posting")
    p.add_argument("--base-url", default="http://127.0.0.1:8001", help="API base URL")
    args = p.parse_args()

    rows = generate(args.count, args.center_lat, args.center_lon, args.spread, args.gaussian)

    if args.out:
        write_csv(rows, args.out)
    if args.post:
        post_rows(rows, args.base_url, args.clear)
    if not args.out and not args.post:
        print("[INFO] Nothing done. Add --out <file.csv> and/or --post")
        print("Example: python scripts/generate_test_data.py --count 500 --out data/generated.csv")
