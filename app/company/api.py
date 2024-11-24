from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, UploadFile, status
from app.company.models import CompanyModel, CompanyUpdate
from app.company.service import CompanyService
from app.core.security import authenticate
from app.employee.models import Employee
from app.schemas.api import Response, ResponseStatus
from app.utils.class_based_views import cbv


company_router = APIRouter()


@cbv(company_router)
class CompanyRouter:
    user: Employee = Depends(authenticate)
    _service: CompanyService = Depends(CompanyService)

    @company_router.post("/", status_code=status.HTTP_201_CREATED)
    async def create(self, company: CompanyModel):
        result = await self._service.create(company)
        return Response(
            message="Company Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @company_router.patch("/{id}", status_code=status.HTTP_200_OK)
    async def update(self, id: PydanticObjectId, company: CompanyUpdate):
        result = await self._service.update(company,id)
        return Response(
            message="Company Updated Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result
        )

    @company_router.delete("/{id}", status_code=status.HTTP_200_OK)
    async def delete(self, id: PydanticObjectId):
        result = await self._service.delete(id)
        return Response(
            message="Company Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )

    @company_router.get("/{id}", status_code=status.HTTP_200_OK)
    async def get(self, id: PydanticObjectId):
        result = await self._service.get(id)
        return Response(
            message="Company Retrieved Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )

    @company_router.get("/", status_code=status.HTTP_200_OK)
    async def get_all(self):
        result = await self._service.get_all()
        return Response(
            message="Company Retrieved Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )

    @company_router.post("/upload", status_code=status.HTTP_201_CREATED)
    async def upload_companies(self, file: UploadFile):
        return await self._service.upload_excel(await file.read())
