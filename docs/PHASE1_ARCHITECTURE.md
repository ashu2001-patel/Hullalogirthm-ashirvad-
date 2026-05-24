# PHASE 1: SYSTEM ARCHITECTURE DESIGN

## 🎯 Objective
Design a production-grade, scalable geospatial delivery coverage system. Define architecture, service boundaries, data flow, and API contracts.

---

## 📐 HIGH-LEVEL ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE LAYER                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  React Frontend + Leaflet Map                             │   │
│  │  - Display warehouses                                     │   │
│  │  - Show delivery coverage polygons                        │   │
│  │  - Real-time coverage updates                            │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │ REST API (HTTP/JSON)
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                   API GATEWAY LAYER                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  FastAPI (Async Python Framework)                        │   │
│  │  - Request routing & validation                          │   │
│  │  - Authentication & CORS                                 │   │
│  │  - Error handling & rate limiting                        │   │
│  │  - OpenAPI/Swagger documentation                         │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
│ WAREHOUSE    │ │ COVERAGE     │ │ ANALYTICS        │
│ SERVICE      │ │ SERVICE      │ │ SERVICE          │
├──────────────┤ ├──────────────┤ ├──────────────────┤
│- Add/Update  │ │- Calculate   │ │- Coverage area   │
│  Warehouse   │ │  convex hull │ │  statistics      │
│- Remove      │ │- Generate    │ │- Growth trends   │
│  Warehouse   │ │  polygon     │ │- Gap detection   │
│- List all    │ │- Compute     │ │- Overlap analysis│
│  Warehouses  │ │  metrics     │ └──────────────────┘
└──────────────┘ └──────────────┘
        │                │
        ▼                ▼
┌──────────────────────────────────┐
│  DATA ACCESS LAYER               │
│  ┌────────────────────────────┐  │
│  │ In-Memory Storage          │  │
│  │ (Phase 1-3: Python dict)   │  │
│  │ (Phase 5+: PostgreSQL)     │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
```

---

## 🏛️ LOW-LEVEL ARCHITECTURE (Component Diagram)

```
FRONTEND LAYER:
├── React Application (localhost:3000)
│   ├── Map Component (Leaflet)
│   ├── Warehouse Manager
│   └── Coverage Visualizer
│
API LAYER (FastAPI - localhost:8000):
├── Router: /api/v1/warehouses
│   ├── POST   /              → Create warehouse
│   ├── GET    /              → List all warehouses
│   ├── GET    /{id}          → Get specific warehouse
│   ├── PUT    /{id}          → Update warehouse
│   └── DELETE /{id}          → Delete warehouse
│
├── Router: /api/v1/coverage
│   ├── GET    /              → Get coverage for all warehouses
│   ├── POST   /recalculate   → Trigger coverage recalculation
│   ├── GET    /{id}          → Get coverage for warehouse
│   └── GET    /{id}/polygon  → Get polygon coordinates
│
├── Router: /api/v1/analytics
│   ├── GET    /stats         → Coverage statistics
│   ├── GET    /overlaps      → Overlapping regions
│   └── GET    /gaps          → Coverage gaps
│
└── Router: /health
    └── GET /               → Health check

BUSINESS LOGIC LAYER:
├── WarehouseService
│   ├── create_warehouse()
│   ├── update_warehouse()
│   ├── delete_warehouse()
│   ├── get_all_warehouses()
│   └── validate_coordinates()
│
├── CoverageService
│   ├── calculate_convex_hull()
│   ├── compute_coverage()
│   ├── calculate_area()
│   └── detect_overlaps()
│
└── GeometryEngine (Algorithms)
    ├── ConvexHullGrahamScan
    ├── ConvexHullMonotonicChain
    ├── ConvexHullJarvisMarch
    ├── ConvexHullQuickHull
    └── GeometryUtils
        ├── calculate_distance()
        ├── point_in_polygon()
        ├── polygon_area()
        └── polygon_perimeter()

DATA LAYER:
└── WarehouseRepository (In-Memory Dict)
    ├── Storage: {warehouse_id: Warehouse}
    └── (Phase 5: PostgreSQL + PostGIS)
```

---

## 🔄 SERVICE COMMUNICATION FLOW

### Use Case 1: Add Warehouse & Compute Coverage

```
1. CLIENT REQUEST
   POST /api/v1/warehouses
   {
     "name": "Bangalore Hub",
     "latitude": 12.9716,
     "longitude": 77.5946,
     "coverage_radius_km": 10
   }
   ↓
2. FASTAPI VALIDATION
   - Validate coordinates (range, format)
   - Validate name (length, characters)
   - Check uniqueness
   ↓
3. WAREHOUSE SERVICE
   - Create warehouse object
   - Store in repository
   - Return warehouse with ID
   ↓
4. COVERAGE SERVICE (Auto-triggered)
   - Get all warehouses
   - Calculate convex hull of all points
   - Compute coverage area & perimeter
   - Generate polygon coordinates
   ↓
5. RESPONSE
   {
     "warehouse_id": 1,
     "coverage": {
       "polygon": [[12.97, 77.59], ...],
       "area_km2": 314.2,
       "perimeter_km": 62.8
     }
   }
```

### Use Case 2: Delete Warehouse & Recalculate Coverage

```
1. CLIENT REQUEST
   DELETE /api/v1/warehouses/{id}
   ↓
2. WAREHOUSE SERVICE
   - Find and remove warehouse
   ↓
3. COVERAGE SERVICE (Auto-triggered)
   - Recalculate convex hull with remaining warehouses
   - Update coverage metrics
   ↓
4. RESPONSE
   {
     "message": "Warehouse deleted, coverage recalculated",
     "new_coverage": {
       "polygon": [[...], [...], ...],
       "area_km2": 287.5,
       "warehouses_count": 4
     }
   }
```

---

## 📊 DATA MODELS

### Warehouse Model

```python
class Warehouse:
    """Represents a delivery warehouse/hub"""
    id: int                    # Unique identifier
    name: str                  # Human-readable name
    latitude: float            # Geographic latitude (-90 to 90)
    longitude: float           # Geographic longitude (-180 to 180)
    capacity: int              # Daily delivery capacity (orders)
    status: str                # "active" | "inactive" | "maintenance"
    created_at: datetime       # Timestamp
    updated_at: datetime       # Last update timestamp
```

### Coverage Model

```python
class Coverage:
    """Represents delivery coverage area"""
    warehouse_ids: List[int]          # Which warehouses contribute
    polygon: List[Tuple[float, float]]  # Vertices of convex hull
    area_km2: float                   # Area in square kilometers
    perimeter_km: float               # Perimeter in kilometers
    centroid: Tuple[float, float]     # Geographic center
    bounding_box: Dict[str, float]    # min_lat, max_lat, min_lon, max_lon
    algorithm: str                    # Which algorithm computed it
    computed_at: datetime             # When coverage was calculated
```

### GeoPoint Model

```python
class GeoPoint:
    """Single geographic coordinate"""
    latitude: float    # -90 to 90
    longitude: float   # -180 to 180
    
    @property
    def as_tuple(self) -> Tuple[float, float]:
        return (self.latitude, self.longitude)
```

---

## 🔌 API CONTRACTS

### 1. Warehouse Endpoints

#### POST /api/v1/warehouses
**Create a new warehouse**

Request:
```json
{
  "name": "Bangalore Central Hub",
  "latitude": 12.9716,
  "longitude": 77.5946,
  "capacity": 10000,
  "status": "active"
}
```

Response (201 Created):
```json
{
  "id": 1,
  "name": "Bangalore Central Hub",
  "latitude": 12.9716,
  "longitude": 77.5946,
  "capacity": 10000,
  "status": "active",
  "created_at": "2026-05-24T10:30:00Z",
  "updated_at": "2026-05-24T10:30:00Z"
}
```

---

#### GET /api/v1/warehouses
**List all warehouses**

Response:
```json
{
  "count": 5,
  "warehouses": [
    {
      "id": 1,
      "name": "Bangalore Hub",
      "latitude": 12.9716,
      "longitude": 77.5946,
      "capacity": 10000,
      "status": "active"
    },
    ...
  ]
}
```

---

#### GET /api/v1/warehouses/{id}
**Get specific warehouse**

Response:
```json
{
  "id": 1,
  "name": "Bangalore Hub",
  "latitude": 12.9716,
  "longitude": 77.5946,
  "capacity": 10000,
  "status": "active",
  "created_at": "2026-05-24T10:30:00Z"
}
```

---

#### PUT /api/v1/warehouses/{id}
**Update warehouse**

Request:
```json
{
  "capacity": 15000,
  "status": "maintenance"
}
```

Response:
```json
{
  "id": 1,
  "name": "Bangalore Hub",
  "latitude": 12.9716,
  "longitude": 77.5946,
  "capacity": 15000,
  "status": "maintenance",
  "updated_at": "2026-05-24T11:00:00Z"
}
```

---

#### DELETE /api/v1/warehouses/{id}
**Delete warehouse**

Response (200 OK):
```json
{
  "message": "Warehouse deleted successfully",
  "id": 1
}
```

---

### 2. Coverage Endpoints

#### GET /api/v1/coverage
**Get overall delivery coverage**

Response:
```json
{
  "warehouse_count": 5,
  "polygon": [
    [12.8, 77.4],
    [13.1, 77.4],
    [13.1, 77.8],
    [12.8, 77.8]
  ],
  "area_km2": 4284.5,
  "perimeter_km": 214.2,
  "centroid": [12.95, 77.6],
  "bounding_box": {
    "min_lat": 12.8,
    "max_lat": 13.1,
    "min_lon": 77.4,
    "max_lon": 77.8
  },
  "algorithm": "graham_scan",
  "computed_at": "2026-05-24T10:35:00Z"
}
```

---

#### GET /api/v1/coverage/{warehouse_id}
**Get coverage contributed by single warehouse**

Response:
```json
{
  "warehouse_id": 1,
  "warehouse_name": "Bangalore Hub",
  "individual_polygon": [
    [12.95, 77.55],
    [12.98, 77.56],
    [12.96, 77.58]
  ],
  "contribution_to_total": 0.25,
  "overlapping_warehouses": [2, 3]
}
```

---

#### POST /api/v1/coverage/recalculate
**Force recalculation of coverage**

Response:
```json
{
  "message": "Coverage recalculated successfully",
  "new_area_km2": 4284.5,
  "previous_area_km2": 4200.0,
  "change_percent": 2.0,
  "timestamp": "2026-05-24T10:40:00Z"
}
```

---

### 3. Analytics Endpoints

#### GET /api/v1/analytics/stats
**Get coverage statistics**

Response:
```json
{
  "total_warehouses": 5,
  "total_coverage_area_km2": 4284.5,
  "avg_capacity_per_warehouse": 8000,
  "coverage_density": 0.85,
  "polygon_complexity": 12,
  "last_update": "2026-05-24T10:35:00Z"
}
```

---

#### GET /api/v1/analytics/overlaps
**Find overlapping coverage areas**

Response:
```json
{
  "overlapping_regions": [
    {
      "warehouse_ids": [1, 2],
      "overlap_area_km2": 125.3,
      "overlap_percent": 4.2
    },
    {
      "warehouse_ids": [2, 3, 4],
      "overlap_area_km2": 89.5,
      "overlap_percent": 2.8
    }
  ],
  "total_overlap_area_km2": 214.8,
  "total_overlap_percent": 7.0
}
```

---

#### GET /api/v1/analytics/gaps
**Find coverage gaps**

Response:
```json
{
  "gaps_detected": [
    {
      "gap_id": "gap_001",
      "center_latitude": 13.05,
      "center_longitude": 77.65,
      "radius_km": 5.2,
      "distance_to_nearest_warehouse_km": 8.3
    }
  ],
  "total_gaps": 2,
  "largest_gap_radius_km": 5.2
}
```

---

### 4. Health Check

#### GET /health
**System health status**

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-05-24T10:45:00Z",
  "services": {
    "api": "up",
    "database": "up",
    "cache": "up"
  }
}
```

---

## 📈 SCALABILITY CONSIDERATIONS

### Bottlenecks & Solutions

| Bottleneck | Current (Phase 1-3) | Future Solution (Phase 5+) |
|-----------|------------|----------|
| **Warehouse Storage** | Python dict (~1K warehouses) | PostgreSQL sharding (~1M warehouses) |
| **Coverage Calculation** | In-process (100ms) | Distributed workers + caching |
| **Real-time Updates** | REST polling | Kafka event streaming |
| **Spatial Queries** | Linear search | PostGIS R-tree indexing |
| **API Rate Limiting** | None | Redis + Token bucket |

### Scaling Strategy

**Phase 1-3: Single Service (Vertical Scaling)**
- Run all services in one FastAPI process
- In-memory storage (dict)
- Suitable for: <10 warehouses, <1000 requests/sec

**Phase 4-5: Monolith + Database (Horizontal Ready)**
- Add PostgreSQL + PostGIS
- Multiple FastAPI instances (load balanced)
- Suitable for: <1000 warehouses, <10K requests/sec

**Phase 6+: Microservices (Full Horizontal Scaling)**
- Separate Warehouse, Coverage, Analytics services
- Kafka for async communication
- Regional sharding
- Suitable for: >10K warehouses, >100K requests/sec

---

## 🔒 SECURITY CONSIDERATIONS

### Input Validation
- ✅ Coordinate bounds: -90 ≤ lat ≤ 90, -180 ≤ lon ≤ 180
- ✅ Name length: 1-255 characters
- ✅ Capacity: 0-1,000,000 orders
- ✅ Unique warehouse IDs

### Authentication (Phase 5+)
- JWT token-based API keys
- Role-based access control (RBAC)
- Audit logging for all changes

### Data Protection
- HTTPS only (TLS 1.3)
- SQL injection prevention (parameterized queries)
- CORS policy (restrict to frontend domain)

---

## 🎯 DESIGN DECISIONS & TRADEOFFS

### Decision 1: Convex Hull for Coverage Boundary

**Why convex hull?**
- ✅ Mathematically optimal for coverage
- ✅ Fast computation (O(n log n))
- ✅ Works with any warehouse distribution
- ✅ Directly computable from points

**Tradeoff:**
- ❌ May include areas between warehouses (union of coverage circles would be more realistic)
- Solution (Phase 5): Add "coverage radius" per warehouse, compute actual Voronoi cells

---

### Decision 2: In-Memory Storage (Phase 1-3)

**Why in-memory dict?**
- ✅ Fast prototyping
- ✅ No database setup required
- ✅ Easy to test algorithms
- ✅ Suitable for <10 warehouses

**Tradeoff:**
- ❌ Data lost on restart
- ❌ No persistence
- Solution (Phase 5): Add PostgreSQL

---

### Decision 3: Synchronous API (vs. Async Events)

**Why REST (Phase 1-3)?**
- ✅ Familiar, well-understood
- ✅ Request/response model works for small datasets
- ✅ Easy to debug

**Tradeoff:**
- ❌ Slow for large updates
- Solution (Phase 6): Add Kafka for async updates

---

## 🎓 INTERVIEW QUESTIONS

### Question 1: System Design
**"How would you scale this to handle 1 million warehouses?"**

Expected Answer:
- Shard warehouses by geographic region
- Use PostGIS spatial indexing
- Distribute convex hull computation across workers
- Kafka for event-driven updates
- Redis caching for frequent queries

---

### Question 2: Algorithm Choice
**"Why convex hull? Isn't it too simplistic?"**

Expected Answer:
- Convex hull is optimal for true geometric boundary
- Alternative: Voronoi cells (more realistic coverage)
- Alternative: Minimum spanning tree
- Depends on business requirements (speed vs. accuracy)

---

### Question 3: Database Design
**"How would you store polygons in PostgreSQL?"**

Expected Answer:
- Use PostGIS POLYGON type
- Create spatial indexes (GIST, BRIN)
- Use ST_Contains for point-in-polygon queries
- Partition by region for large tables

---

---

## 🏭 PRODUCTION-GRADE ARCHITECTURE DETAILS

### Scalability Bottlenecks & Solutions

#### Bottleneck 1: Hull Recalculation with Millions of Points

**Problem:**
- Monotonic Chain algorithm: O(n log n) time complexity
- 1M points → ~20 million comparisons
- CPU becomes bottleneck
- Recalculating for every GPS update = too expensive

**Solutions by Phase:**

```
Phase 3 (Current): 
  ✅ Cache hull results (TTL: 5-10 minutes)
  ✅ Only recalculate if new point outside hull
  ✅ Batch updates (every 100 points or 30 seconds)
  🎯 Performance: ~100ms for 100K warehouses

Phase 6 (Real-time):
  ✅ Incremental hull update (add/remove single point)
  ✅ Maintains running convex hull O(log n) per point
  ✅ No full recomputation needed
  🎯 Performance: <5ms per update

Phase 8 (Advanced):
  ✅ Parallel hull computation (multi-threaded)
  ✅ Split into regions (KD-tree partitioning)
  ✅ Merge smaller hulls (O(n) merge with sorted lists)
  🎯 Performance: <100ms for 1B points

Phase 9 (Distributed):
  ✅ Horizontal partitioning by geography
  ✅ Each region computes regional hull
  ✅ Global hull = merge of regional hulls
  🎯 Performance: Process 10B points/day across cluster
```

---

#### Bottleneck 2: Spatial Indexes on Growing Dataset

**Problem:**
- GIST indexes degrade as warehouses grow
- vehicle_locations grows 100M+ records/day
- Index rebuild locks table for hours

**Solutions:**

```
1. Table Partitioning (vehicle_locations)
   ├─ Partition by date (YYYY_MM_DD)
   ├─ Automatic cleanup: drop partition after 90 days
   ├─ Index rebuild only on new partition (fast)
   └─ Result: BRIN index shrinks from 100MB → 10MB per partition

2. Coverage Zones Partitioning
   ├─ Partition by warehouse_id (hash partitioning)
   ├─ Enables parallel queries across regions
   └─ Each partition fits in memory

3. Materialized Views
   ├─ Periodic refresh (every hour) offline
   ├─ Queries hit cached result
   └─ No locks during refresh

4. Read Replicas
   ├─ Heavy queries (analytics) hit replicas
   ├─ Writes go to primary
   └─ Replicas lag: <1-2 seconds (acceptable)
```

---

#### Bottleneck 3: Network Latency in Geospatial Queries

**Problem:**
- Round-trip to PostgreSQL: 10-50ms per request
- Nearest warehouse query × 1000 clients → high latency
- Frontend map can't redraw quickly

**Solutions:**

```
1. Redis Cache (Coverage Service)
   ├─ Cache hull polygon: TTL 10 min → 90% hit rate
   ├─ Cache warehouse list: TTL 5 min → 95% hit rate
   └─ Result: 10x speedup (50ms → 5ms)

2. Edge Caching (Cloudflare, CloudFront)
   ├─ Cache static assets (map tiles, polygons)
   ├─ GeoIP routing to nearest edge
   └─ Result: 50ms → 5ms latency

3. Client-Side Caching (React)
   ├─ Cache coverage polygon locally
   ├─ Only fetch updates (delta sync)
   └─ Result: Reduce bandwidth 50KB → 2KB per update

4. Spatial Indexing
   ├─ Binary search + GIST index
   ├─ Nearest warehouse: O(log n) vs O(n) full scan
   └─ Result: 1000 points = 10ms vs 100ms
```

**Performance Targets:**
- Warehouse lookup: <10ms
- Coverage update: <100ms
- Analytics query: <500ms
- WebSocket message delivery: <100ms

---

### Database Scaling Strategy

#### Vertical Scaling (Scale Up)

**Phase 1-3 (MVP):**
```
Instance: t3.xlarge (4 vCPU, 16GB RAM)
Storage: 100GB SSD
Throughput: ~5K writes/sec, ~50K reads/sec
Cost: ~$200/month
Suitable for: <1K warehouses, <10K requests/sec

Limit: Single writer maxes out around 10K writes/sec
```

**Phase 5-6 (Growth):**
```
Instance: r6g.2xlarge (8 vCPU, 64GB RAM)
Storage: 500GB SSD
Throughput: ~10K writes/sec, ~100K reads/sec
Cost: ~$600/month
Suitable for: 10K-100K warehouses

Hit ceiling: Can't exceed 10K writes/sec
```

#### Horizontal Scaling (Scale Out) - Phase 7+

```
Architecture: Regional Sharding

┌──────────────────┐
│  Router/Gateway  │  (Directs queries by region)
└────┬─────────┬───┘
     │         │
┌────▼──┐  ┌──▼────┐
│ North │  │ South │  Each region: separate DB cluster
│Region │  │Region │  with primary + read replicas
│  DB   │  │  DB   │
└───────┘  └───────┘

Benefits:
  ✅ North Region: 20 warehouses → separate DB
  ✅ South Region: 30 warehouses → separate DB
  ✅ Each can scale independently
  ✅ Total writes: 10K/sec per shard × N shards

Challenges:
  ⚠️ Cross-shard queries (global coverage)
  ⚠️ Transaction coordination (SAGA pattern)
  ⚠️ Operational complexity

Recommendation:
  Start with single database (Phase 1-5)
  Add sharding only when needed (~1M warehouses)
```

---

### High Availability (HA) Architecture

**Target:** 99.9% uptime (8.6 hours downtime/year)

```
┌────────────────────────────────────────────┐
│ AWS Application Load Balancer (Multi-AZ)   │
├────────────────────────────────────────────┤
│                                            │
│  ┌──────────┐  ┌──────────┐  ┌──────┐    │
│  │ Service-1│  │ Service-2│  │Svc-3 │    │
│  │(us-east- │  │(us-east- │  │(us-e │    │
│  │  1a)     │  │  1b)     │  │ ast- │    │
│  └────┬─────┘  └────┬─────┘  │ 1c)  │    │
│       │              │        └──┬───┘    │
└───────┼──────────────┼───────────┼────────┘
        │              │           │
    ┌───▼──────────────▼───────────▼──┐
    │ RDS Multi-AZ Primary (us-east-1a)│
    │ (Auto-failover to Standby)       │
    │ Write latency: <1ms              │
    └────────────────┬─────────────────┘
                     │
        ┌────────────▼────────────┐
        │  Read Replicas          │
        │  (us-east-1a, 1b)       │
        │  Replication lag: <1ms  │
        └─────────────────────────┘

Kafka Cluster (High Availability):
┌──────────────────────────────────┐
│ us-east-1a  us-east-1b  us-east-1c
│ Broker 1    Broker 2    Broker 3
│ (Leader)
└──────────────────────────────────┘

Kafka Settings:
  - Replication Factor: 3
  - Min In-Sync Replicas: 2
  - Auto-failover: Yes
  - Unclean leader election: No (data safety)

Recovery Time Objectives (RTO):
  🟢 Service down: 30-60 seconds (ALB detects, routes to healthy)
  🟢 Database down: 1-2 minutes (RDS automatic failover)
  🟢 Kafka broker down: <1 minute (automatic rebalance)
  🟢 Region failure: 5-10 minutes (manual failover to standby region)
```

---

### Disaster Recovery (DR) Strategy

```
Backup Strategy:

1. Daily Snapshots
   ├─ Time: 2:00 AM UTC (off-peak)
   ├─ Storage: S3 (cross-region replication)
   ├─ Retention: 30 days
   ├─ RTO: 4-6 hours (restore to new DB)
   └─ RPO: 1 day

2. Continuous Replication
   ├─ Real-time replication to us-west-2 (standby region)
   ├─ Replication lag: <1 second
   ├─ Failover time: 5-10 minutes (manual)
   └─ RPO: <1 second

3. Kafka Topics Backup
   ├─ Kafka broker replication factor: 3
   ├─ Topic backups to S3: Daily
   ├─ Retention: 14 days of messages in Kafka
   └─ Retention: 90 days in S3

DR Runbook (Database Failure):
  1️⃣ Detect failure (CloudWatch alarm)
  2️⃣ Automatic failover to read replica (2 min)
  3️⃣ Promote read replica to primary
  4️⃣ Update connection strings in app config
  5️⃣ Validate data integrity
  6️⃣ Restore failed primary from snapshot (4 hours)
```

---

### Monitoring & Observability

**Key Metrics by Component:**

```
Coverage Service:
  📊 Request latency: p50, p95, p99
  📊 Error rate: 4xx, 5xx percentage
  📊 Hull calculation time: <100ms target
  📊 Cache hit rate: >85% target

Database (PostgreSQL):
  📊 Query latency: slow queries log
  📊 Connection pool utilization: <80%
  📊 Disk I/O: IOPS, throughput
  📊 Replication lag: read replicas

Kafka:
  📊 Consumer lag: per consumer group
  📊 Broker CPU, memory, disk usage
  📊 Topic replica sync: in-sync replicas count
  📊 Message throughput: msgs/sec

Frontend:
  📊 Map render time: <500ms target
  📊 WebSocket connections: active count
  📊 Message delivery latency: p95 <100ms

Alerting Strategy:
  🔴 Error rate > 5% for 5 min → PagerDuty (critical)
  🟠 Query latency p95 > 1 sec → Slack (warning)
  🟠 Consumer lag > 10K messages → Slack (warning)
  🟡 Disk usage > 80% → Slack (non-urgent)
```

---

## 💰 Cost Estimation (AWS)

### Phase 1-3 (MVP) - Monthly Cost

```
┌────────────────────────────────────────────┐
│ COMPUTE (ECS/EC2)                          │
├────────────────────────────────────────────┤
│ Coverage Service:    3 × t3.medium = $90   │
│ Analytics Service:   2 × t3.small = $30    │
│ Location Streaming:  2 × t3.small = $30    │
│ Subtotal: $150                             │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ DATABASE (RDS)                             │
├────────────────────────────────────────────┤
│ Primary (t3.xlarge): $300                  │
│ Storage (100GB): $11.50                    │
│ Backups (30 snapshots): $70                │
│ Subtotal: $381.50                          │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ KAFKA (MSK)                                │
├────────────────────────────────────────────┤
│ 3 Brokers × $0.15/hour: $108              │
│ Storage (1TB): $100                        │
│ Subtotal: $208                             │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ CACHE (ElastiCache Redis)                  │
├────────────────────────────────────────────┤
│ cache.t3.micro: $20                        │
│ Subtotal: $20                              │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ NETWORKING                                 │
├────────────────────────────────────────────┤
│ ALB: $20 (fixed) + $0.006/LCU = $25       │
│ Data transfer (1GB/day): $50               │
│ Subtotal: $75                              │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ MONITORING                                 │
├────────────────────────────────────────────┤
│ CloudWatch: $50                            │
│ Prometheus/Grafana: $0 (self-hosted)       │
│ Subtotal: $50                              │
└────────────────────────────────────────────┘

╔════════════════════════════════════════════╗
║ TOTAL MONTHLY: ~$785                       ║
║ Cost per user (100 users): $7.85/month     ║
║ Cost per warehouse (1K warehouses): $0.79  ║
╚════════════════════════════════════════════╝
```

**Scaling Economics:**

```
At 1M warehouses:
  ├─ Would need: r6i.4xlarge RDS ($1,500+)
  ├─ More Kafka brokers: $500+
  ├─ More service instances: $500+
  ├─ Read replicas: $500+
  └─ Total: ~$3,000-4,000/month

Recommendation:
  ✅ Start with MVP ($785/month)
  ✅ Monitor costs as you scale
  ✅ Use Reserved Instances (RI) for 30% savings
  ✅ Use Spot instances for non-critical workloads
  ✅ Add multi-region replication only when needed
```

---

## 🔒 Security Architecture

### Authentication & Authorization

```
API Security Model:

1. Service-to-Service (API Gateway → Services)
   ├─ API Key Authentication
   ├─ Keys in AWS Secrets Manager
   ├─ Rotation: Every 90 days
   └─ Header: Authorization: Bearer {API_KEY}

2. Frontend User Authentication
   ├─ OAuth 2.0 (or JWT)
   ├─ Token obtained from auth service
   ├─ Includes in Authorization header
   ├─ Token TTL: 1 hour
   └─ Refresh token TTL: 30 days

3. Role-Based Access Control (RBAC)
   ├─ Admin: Can add/delete warehouses, manage users
   ├─ Manager: View analytics, trigger recalculation
   ├─ Viewer: Read-only access to coverage
   └─ Stored in JWT claims: { sub: user_id, roles: ["admin"] }

Implementation Example:
  @app.get("/api/v1/coverage")
  def get_coverage(request: Request):
      token = request.headers.get("Authorization")
      claims = validate_jwt(token)  # raises HTTPException if invalid
      user_role = claims.get("roles", [])
      if "viewer" not in user_role:
          raise HTTPException(status_code=403)
      return get_coverage_data()
```

### Data Protection

```
In-Transit (TLS):
  ✅ All APIs: HTTPS only (TLS 1.3)
  ✅ Database: SSL/TLS certificate validation
  ✅ Kafka: TLS between brokers and clients
  ✅ Config: Automatic HTTP → HTTPS redirect

At-Rest:
  ✅ Database: RDS encryption (AWS KMS)
  ✅ S3 backups: AES-256 encryption
  ✅ Redis: Encryption enabled
  ✅ Application secrets: AWS Secrets Manager
  ✅ Config secrets: Environment variables (never in repo)

Environment-Specific:
  Dev:  Self-signed certificates
  Prod: AWS ACM (Amazon Certificate Manager) certs
```

### Input Validation & Injection Prevention

```
Validate All User Inputs:

1. Coordinate Validation
   def validate_coordinates(lat: float, lon: float):
       if not (-90 <= lat <= 90):
           raise ValueError("Latitude out of range")
       if not (-180 <= lon <= 180):
           raise ValueError("Longitude out of range")

2. SQL Injection Prevention
   ✅ Use ORM (SQLAlchemy) - parameterized queries
   ✅ Never use string interpolation in SQL
   ❌ WRONG: f"SELECT * FROM warehouses WHERE id = {id}"
   ✅ RIGHT: session.query(Warehouse).filter_by(id=id)

3. Rate Limiting
   @app.middleware("http")
   async def rate_limit(request: Request, call_next):
       ip = request.client.host
       if get_request_count(ip) > 100:  # 100 req/min
           raise HTTPException(status_code=429)
       return await call_next(request)

4. Payload Size Limits
   # Prevent billion-byte uploads
   app.add_middleware(
       GZipMiddleware,
       minimum_size=1000,
       maximum_request_size=10_000_000  # 10MB max
   )
```

---

## 📚 Interview Questions & Follow-Ups

### Q1: System Design - "How would you scale to 1 million warehouses?"

**Expected Answer:**
```
1. Geographic Sharding
   - Shard warehouses by geographic region (lat/lon ranges)
   - Each shard: separate database cluster
   - Router directs queries to appropriate shard

2. Spatial Indexing
   - PostGIS GIST indices for nearest-neighbor queries
   - BRIN indices for time-series data (vehicle_locations)
   - Materialized views for frequently accessed data

3. Distributed Computation
   - Distribute convex hull calculation across workers
   - Compute regional hulls in parallel
   - Merge regional hulls to get global coverage

4. Event-Driven Architecture
   - Kafka topics for location updates
   - Partition by region for horizontal scaling
   - Consumer groups for parallel processing

5. Caching Strategy
   - Redis for hot data (hull polygons, warehouse lists)
   - Cache hit rate: >85%
   - TTL: 5-10 minutes

Result: Can handle 1B locations/day, 100K concurrent users
```

**Follow-up Questions:**
- How would you handle cross-shard queries for global coverage?
  → Answer: Regional hulls merge algorithm, not real-time
- What about consistency between shards?
  → Answer: Eventual consistency, acceptable for this use case
- How do you handle shard rebalancing?
  → Answer: Pre-plan shard ranges, migrate during off-peak

---

### Q2: Algorithm - "Why convex hull? Isn't it too simplistic?"

**Expected Answer:**
```
Convex Hull vs. Alternatives:

1. Convex Hull (CHOSEN)
   ✅ O(n log n) time complexity
   ✅ Optimal mathematical boundary
   ✅ Works with any point distribution
   ✅ Directly computable
   ❌ May include areas between warehouses

2. Alpha Shapes (Concave Hull)
   ✅ More realistic (excludes dead zones)
   ❌ O(n²) time complexity
   ❌ Requires parameter tuning (alpha)

3. Voronoi Diagram
   ✅ Shows individual warehouse service areas
   ✅ Mathematically beautiful
   ❌ Expensive to compute O(n log n)
   ❌ Complex queries for coverage

4. Union of Coverage Circles
   ✅ Most realistic (actual delivery range)
   ❌ Complex computations
   ❌ Not clean boundary

Decision Rationale:
  - Start with convex hull for speed
  - Simple, well-understood algorithm
  - Phase 2+ can switch to alpha shapes if needed
```

**Follow-up Questions:**
- What's the space complexity of convex hull?
  → Answer: O(h) where h = number of hull vertices (typically 20-500)
- How do you compute area of a polygon?
  → Answer: Shoelace formula, O(n) time
- What if points are collinear?
  → Answer: Handle as edge case, remove collinear points

---

### Q3: Database - "How do you store polygons in PostgreSQL?"

**Expected Answer:**
```
PostGIS Polygon Storage:

1. Data Type
   CREATE TABLE coverage_zones (
       id SERIAL PRIMARY KEY,
       warehouse_id INT,
       polygon GEOMETRY(POLYGON, 4326),  -- WGS84 projection
       area_sq_km DECIMAL(10, 2),
       created_at TIMESTAMP DEFAULT NOW()
   );

2. Spatial Indexes
   CREATE INDEX idx_coverage_polygon 
       ON coverage_zones USING GIST (polygon);
   
   Index type choice:
   - GIST: Good for nearest-neighbor
   - BRIN: Memory efficient for large tables

3. Queries
   -- Point in polygon
   SELECT * FROM coverage_zones 
   WHERE ST_Contains(polygon, ST_Point(77.59, 12.97));
   
   -- Distance queries
   SELECT * FROM coverage_zones 
   WHERE ST_DWithin(polygon, point, 5000);  -- 5km
   
   -- Centroid
   SELECT ST_Centroid(polygon) 
   FROM coverage_zones;

4. Polygon Format
   ├─ GeoJSON: {"type": "Polygon", "coordinates": [...]}
   ├─ WKT: "POLYGON ((77.59 12.97, 77.60 12.98, ...))"
   ├─ Binary: EWKB format (compact, efficient)
   └─ Internally stored as: GEOMETRY type
```

**Follow-up Questions:**
- What's the difference between GEOMETRY and GEOGRAPHY?
  → Answer: GEOMETRY = planar (fast, good for local), GEOGRAPHY = spheroidal (accurate globally)
- How do you index multiple columns?
  → Answer: GiST multicolumn indices, or separate indices
- What's the performance impact of complex polygons?
  → Answer: Queries scale with vertex count, typically 100-500 vertices

---

## 📋 NEXT STEPS

✅ **Phase 1 COMPLETE:** Architecture designed (comprehensive)
⏳ **Phase 2:** Implement convex hull algorithms (Graham Scan, Monotonic Chain, Jarvis, QuickHull)
⏳ **Phase 3:** Build FastAPI services and REST endpoints
⏳ **Phase 4:** React + Leaflet frontend
⏳ **Phase 5:** PostgreSQL + PostGIS integration
⏳ **Phase 6+:** Real-time streaming, analytics, distributed processing

---

## ✅ APPROVAL CHECKLIST

Before proceeding to Phase 2, please confirm:

- [ ] Architecture design meets requirements
- [ ] Microservices approach (3 services) acceptable for your team
- [ ] PostgreSQL + PostGIS for spatial database agreed
- [ ] Kafka for event streaming approved
- [ ] Tech stack (Python 3.12, FastAPI, React, Docker) confirmed
- [ ] Scalability targets (1M warehouses, 1B GPS points/day) realistic for your use case
- [ ] Cost estimation (~$785/month MVP) acceptable
- [ ] Security approach (JWT, RBAC, TLS) satisfactory

### Questions for You:

1. **Team size?** (affects complexity of microservices)
2. **Existing AWS account?** (influences deployment choices)
3. **Real-time requirements?** (WebSocket needs?)
4. **Data retention policy?** (affects storage costs)
5. **Compliance requirements?** (GDPR, CCPA, etc.)
6. **Which phases are highest priority?**

### Phase 2 Will Include:

✨ Four convex hull implementations
✨ Unit tests with test cases
✨ Complexity analysis (time, space)
✨ Benchmark comparisons
✨ Production-quality Python code
✨ Mathematical intuition explanations
✨ When/where to use each algorithm

---

**Status**: 🟢 **PHASE 1 COMPLETE - AWAITING APPROVAL**
**Date**: 2026-05-24
**Author**: Principal Software Engineer (Google Maps)
**Next Review**: Ready for Phase 2 kickoff
