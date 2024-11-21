from fastapi import UploadFile,APIRouter, Depends,status
from beanie import PydanticObjectId
from app.department.models import DepartmentModel, DepartmentUpdate
from app.department.service import DepartmentService
from app.utils.class_based_views import cbv
from app.schemas.api import ResponseStatus,Response

department_router = APIRouter()

@cbv(department_router)
class DepartmentRouter:
    # user: User = Depends(get_current_active_user)
    _service: DepartmentService = Depends(DepartmentService)

    @department_router.post("/", status_code=status.HTTP_201_CREATED)
    async def create(self, department: DepartmentModel):
        result = await self._service.create(department)
        return Response(
            message="Department Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @department_router.patch("/{id}", status_code=status.HTTP_200_OK)
    async def update(self, id: PydanticObjectId, department: DepartmentUpdate):
        result = await self._service.update(department, id)
        return Response(
            message="Department Updated Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result
        )

    @department_router.delete("/{id}", status_code=status.HTTP_200_OK)
    async def delete(self, id: PydanticObjectId):        
        result = await self._service.delete(id)
        return Response(
            message="Department Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )

    @department_router.get("/{id}", status_code=status.HTTP_200_OK)
    async def get(self, id: PydanticObjectId):
        result = await self._service.get(id)
        return Response(
            message="Department Retrieved Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )

    @department_router.get("/", status_code=status.HTTP_200_OK)
    async def get_all(self):
        result = await self._service.get_all()
        return Response(
            message="Department Retrieved Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )

    @department_router.post("/upload", status_code=status.HTTP_201_CREATED)
    async def upload_departments(self, file: UploadFile):
        return await self._service.upload_excel(await file.read())