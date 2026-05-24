#!/usr/bin/env python
"""Bulk-load warehouses from a CSV file into the running Coverage API.

Usage:
    python scripts/load_csv.py data/warehouses_india.csv
    python scripts/load_csv.py data/warehouses_bangalore.csv --clear
    python scripts/load_csv.py data/my.csv --base-url http://127.0.0.1:8001

CSV columns (header required):
    name,latitude,longitude,capacity,region,status
Only name, latitude, longitude are mandatory; the rest have defaults.
"""

import argparse
import csv
import sys

try:
    import requests
except ImportError:
    print("[ERROR] 'requests' not installed. Run: pip install requests")
    sys.exit(1)


def load(csv_path, base_url, clear):
    api = base_url.rstrip("/") + "/api/v1"

    # Optional: wipe existing warehouses first
    if clear:
        try:
            requests.delete(f"{api}/warehouses", timeout=5)
            print("[OK] Cleared existing warehouses")
        except Exception as e:
            print(f"[WARN] Could not clear: {e}")

    added, failed = 0, 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                payload = {
                    "name": row["name"].strip(),
                    "latitude": float(row["latitude"]),
                    "longitude": float(row["longitude"]),
                    "capacity": int(row.get("capacity") or 8000),
                    "region": (row.get("region") or "default").strip(),
                    "status": (row.get("status") or "active").strip(),
                }
                r = requests.post(f"{api}/warehouses", json=payload, timeout=5)
                if r.status_code == 201:
                    print(f"[OK]   {payload['name']:35s} ({payload['latitude']:.4f}, {payload['longitude']:.4f})")
                    added += 1
                else:
                    print(f"[FAIL] {payload['name']}: HTTP {r.status_code} {r.text[:80]}")
                    failed += 1
            except Exception as e:
                print(f"[ERROR] row {row}: {e}")
                failed += 1

    print("\n" + "=" * 50)
    print(f"Loaded {added} warehouses, {failed} failed")

    # Show resulting coverage
    try:
        cov = requests.get(f"{api}/coverage", timeout=5).json()
        print(f"Coverage: {len(cov.get('polygon', []))} hull vertices, "
              f"{cov.get('warehouse_count', 0)} warehouses, "
              f"area={cov.get('area_sq_degrees', 0):.4f} sq deg")
    except Exception as e:
        print(f"[WARN] Could not fetch coverage: {e}")
    print("=" * 50)
    print("Open http://127.0.0.1:5000 to see the map.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Bulk-load warehouses from CSV")
    p.add_argument("csv_file", help="Path to CSV file")
    p.add_argument("--base-url", default="http://127.0.0.1:8001", help="API base URL")
    p.add_argument("--clear", action="store_true", help="Delete existing warehouses first")
    args = p.parse_args()
    load(args.csv_file, args.base_url, args.clear)
