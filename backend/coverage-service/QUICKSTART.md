# Coverage Service - Quick Start

## Installation

### 1. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Server

### Start the API Server

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### View API Documentation

Open your browser:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/test_geometry.py::TestConvexHull::test_monotonic_chain_square -v
```

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Create Warehouse
```bash
curl -X POST http://localhost:8000/api/v1/warehouses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mumbai Hub",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "capacity": 10000,
    "status": "active"
  }'
```

### List Warehouses
```bash
curl http://localhost:8000/api/v1/warehouses
```

### Get Coverage
```bash
curl "http://localhost:8000/api/v1/coverage?algorithm=monotonic_chain"
```

### Get Coverage as GeoJSON
```bash
curl http://localhost:8000/api/v1/coverage/polygon
```

### Check Point in Coverage
```bash
curl "http://localhost:8000/api/v1/coverage/point-in-polygon?latitude=13.0&longitude=77.6"
```

## Project Structure

```
backend/coverage-service/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app
│   ├── models/
│   │   ├── geometry.py             # Convex hull algorithms
│   │   ├── warehouse.py            # Warehouse model
│   │   └── schemas.py              # Pydantic schemas
│   ├── services/
│   │   ├── warehouse_service.py    # Warehouse CRUD
│   │   └── coverage_service.py     # Coverage calculation
│   └── routers/
│       ├── warehouses.py           # Warehouse endpoints
│       ├── coverage.py             # Coverage endpoints
│       └── health.py               # Health check
├── tests/
│   ├── test_geometry.py            # Convex hull tests
│   └── __init__.py
├── requirements.txt
└── QUICKSTART.md
```

## Convex Hull Algorithms Supported

1. **Monotonic Chain** (Recommended)
   - O(n log n) time
   - Fastest in practice
   - `?algorithm=monotonic_chain`

2. **Graham Scan**
   - O(n log n) time
   - Educational, reliable
   - `?algorithm=graham_scan`

3. **Jarvis March**
   - O(n × h) time
   - Good for small hulls
   - `?algorithm=jarvis_march`

4. **QuickHull**
   - O(n log n) average
   - Divide & conquer
   - `?algorithm=quickhull`

## Example Workflow

### 1. Add Multiple Warehouses
```bash
# Warehouse 1
curl -X POST http://localhost:8000/api/v1/warehouses \
  -H "Content-Type: application/json" \
  -d '{"name": "Hub1", "latitude": 12.97, "longitude": 77.59, "capacity": 10000}'

# Warehouse 2
curl -X POST http://localhost:8000/api/v1/warehouses \
  -H "Content-Type: application/json" \
  -d '{"name": "Hub2", "latitude": 13.00, "longitude": 77.60, "capacity": 15000}'

# Warehouse 3
curl -X POST http://localhost:8000/api/v1/warehouses \
  -H "Content-Type: application/json" \
  -d '{"name": "Hub3", "latitude": 12.95, "longitude": 77.65, "capacity": 12000}'
```

### 2. Get Coverage
```bash
curl http://localhost:8000/api/v1/coverage
```

### 3. Get Coverage as GeoJSON (for map)
```bash
curl http://localhost:8000/api/v1/coverage/polygon
```

### 4. Get Warehouse Stats
```bash
curl http://localhost:8000/api/v1/warehouses/stats
```

## Troubleshooting

### Port Already in Use
```bash
# Use a different port
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Import Errors
```bash
# Make sure you're in the right directory
cd backend/coverage-service

# Reinstall dependencies
pip install -r requirements.txt
```

### Tests Failing
```bash
# Run with verbose output
pytest tests/ -v --tb=short
```

## Next Steps

1. ✅ Backend API running
2. ⏳ Frontend (React + Leaflet) - coming next
3. ⏳ Database integration (PostgreSQL + PostGIS)
4. ⏳ Real-time streaming (Kafka)

---

**Version:** 1.0.0
**Phase:** 2-3 (Algorithms & API)
**Status:** Ready for use
