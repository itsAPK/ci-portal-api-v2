from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, UploadFile, status, BackgroundTasks

from app.bussiness_unit.models import BussinessUnitRequest
from app.bussiness_unit.service import BussinessUnitService
from app.core.security import authenticate
from app.employee.models import Employee
from app.schemas.api import Response, ResponseStatus
from app.utils.class_based_views import cbv


bussiness_unit_router = APIRouter()


@cbv(bussiness_unit_router)
class bussiness_unitRouter:
    _service: BussinessUnitService = Depends(BussinessUnitService)

    @bussiness_unit_router.post("/", status_code=status.HTTP_201_CREATED)
    async def create(self, bussiness_unit: BussinessUnitRequest):
        result = await self._service.create(bussiness_unit)
        return Response(
            message="bussiness_unit Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @bussiness_unit_router.patch("/{id}", status_code=status.HTTP_200_OK)
    async def update(self, id: PydanticObjectId, bussiness_unit: BussinessUnitRequest):
        result = await self._service.update(bussiness_unit, id)
        return Response(
            message="bussiness_unit Updated Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result,
        )

    @bussiness_unit_router.delete("/{id}", status_code=status.HTTP_200_OK)
    async def delete(self, id: PydanticObjectId):
        result = await self._service.delete(id)
        return Response(
            message="bussiness_unit Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )

    @bussiness_unit_router.get("/{id}", status_code=status.HTTP_200_OK)
    async def get(self, id: PydanticObjectId):
        result = await self._service.get(id)
        return Response(
            message="bussiness_unit Retrieved Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )

    @bussiness_unit_router.get("/", status_code=status.HTTP_200_OK)
    async def get_all(self):
        result = await self._service.get_all()
        return Response(
            message="bussiness_unit Retrieved Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )

    @bussiness_unit_router.post("/upload", status_code=status.HTTP_201_CREATED)
    async def upload_bussiness_units(
        self, file: UploadFile, background_tasks: BackgroundTasks
    ):
        result = await self._service.upload_excel_in_background(
            background_tasks, await file.read()
        )
        return Response(
            message="Company are uploading, It will take sometime..",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )
        
    @bussiness_unit_router.post("/erase-all", status_code=status.HTTP_200_OK)
    async def delete_all(self):
        result = await self._service.delete_all_bussiness_unit()
        return Response(
            message="Bussiness Unit deleted successfully",
            success=True,
            status=ResponseStatus.ACCEPTED,
            data={},
        )
