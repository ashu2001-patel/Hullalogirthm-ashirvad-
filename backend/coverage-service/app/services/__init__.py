"""Services package with shared instances."""

from app.services.warehouse_service import WarehouseService
from app.services.coverage_service import CoverageService

# Shared service instances
warehouse_service = WarehouseService()
coverage_service = CoverageService()
