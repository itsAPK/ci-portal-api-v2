from fastapi import APIRouter

from app.company.api import company_router
from app.division.api import division_router
from app.plant.api import plant_router
from app.department.api import department_router

router = APIRouter(prefix=f"/api")
router.include_router(company_router, prefix="/company", tags=["Company"])
router.include_router(division_router, prefix="/division", tags=["Division"])
router.include_router(plant_router, prefix="/plant", tags=["Plant"])
router.include_router(department_router, prefix="/department", tags=["Department"])