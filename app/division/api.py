from fastapi import UploadFile
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status
from app.core.security import authenticate
from app.division.models import DivisionModel, DivisionUpdate
from app.division.service import DivisionService
from app.employee.models import Employee
from app.utils.class_based_views import cbv
from app.schemas.api import ResponseStatus,Response


division_router = APIRouter()


@cbv(division_router)
class DivisionRouter:
    user: Employee = Depends(authenticate)
    _service: DivisionService = Depends(DivisionService)

    @division_router.post("/", status_code=status.HTTP_201_CREATED)
    async def create(self, division: DivisionModel):
        result = await self._service.create(division)
        return Response(
            message="Division Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @division_router.patch("/{id}", status_code=status.HTTP_200_OK)
    async def update(self, id: PydanticObjectId, division: DivisionUpdate):
        result = await self._service.update(division, id)
        return Response(
            message="Division Updated Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result
        )

    @division_router.delete("/{id}", status_code=status.HTTP_200_OK)
    async def delete(self, id: PydanticObjectId):
        result = await self._service.delete(id)
        return Response(
            message="Division Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )

    @division_router.get("/{id}", status_code=status.HTTP_200_OK)
    async def get(self, id: PydanticObjectId):
        result = await self._service.get(id)
        return Response(
            message="Division Retrieved Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )

    @division_router.get("/", status_code=status.HTTP_200_OK)
    async def get_all(self):
        result = await self._service.get_all()
        return Response(
            message="Division Retrieved Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )

    @division_router.post("/upload", status_code=status.HTTP_201_CREATED)
    async def upload_divisions(self, file: UploadFile):
        return await self._service.upload_excel(await file.read())