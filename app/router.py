from fastapi import APIRouter

from app.company.api import company_router
from app.division.api import division_router
from app.plant.api import plant_router
from app.department.api import department_router
from app.employee.api import employee_router
from app.auth.api import auth_router
from app.files.api import files_router
from app.tools.api import tools_router
from app.documents.api import document_router
from app.archive.api import archive_router
from app.opportunity.api import opportunity_router
from app.bussiness_unit.api import bussiness_unit_router
from app.training.api import training_router

router = APIRouter(prefix=f"/api")
router.include_router(employee_router, prefix="/employee", tags=["Employee"])
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(company_router, prefix="/company", tags=["Company"])
router.include_router(division_router, prefix="/division", tags=["Division"])
router.include_router(plant_router, prefix="/plant", tags=["Plant"])
router.include_router(department_router, prefix="/department", tags=["Department"])
router.include_router(files_router, prefix="/files", tags=["Files"])
router.include_router(tools_router, prefix="/tools", tags=["Tools"])
router.include_router(document_router, prefix="/document", tags=["Document"])
router.include_router(archive_router, prefix="/archive", tags=["Archive"])
router.include_router(opportunity_router, prefix="/opportunity", tags=["Opportunity"])
router.include_router(bussiness_unit_router, prefix="/bussiness-unit", tags=["Bussiness Unit"])
router.include_router(training_router, prefix="/training", tags=["Training"])