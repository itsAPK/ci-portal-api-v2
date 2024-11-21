from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status

from app.employee.models import EmployeeModel
from app.employee.service import EmployeeService
from app.schemas.api import Response, ResponseStatus
from app.utils.class_based_views import cbv


employee_router = APIRouter()


@cbv(employee_router)
class EmployeeRouter:
    # user: User = Depends(get_current_active_user)
    _service: EmployeeService = Depends(EmployeeService)

    @employee_router.post("/", status_code=status.HTTP_201_CREATED)
    async def create(self, employee: EmployeeModel):
        result = await self._service.create(employee)
        return Response(
            message="Employee Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )
        
    @employee_router.patch("/{id}", status_code=status.HTTP_200_OK)
    async def update(self, id: PydanticObjectId, employee: EmployeeModel):
        result = await self._service.update(employee, id)
        return Response(
            message="Division Updated Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result
        )

    @employee_router.delete("/{id}", status_code=status.HTTP_200_OK)
    async def delete(self, id: PydanticObjectId):
        result = await self._service.delete(id)
        return Response(
            message="Division Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )
        
    @employee_router.get("/{id}", status_code=status.HTTP_200_OK)
    async def get(self, id: PydanticObjectId):
        result = await self._service.get(id)
        return Response(
            message="Employee Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )
        
    @employee_router.get("/{employee_id}", status_code=status.HTTP_200_OK)
    async def get_by_employee_id(self, employee_id: str):
        result = await self._service.get_by_employee_id(employee_id)
        return Response(
            message="Employee Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )

    @employee_router.get("/", status_code=status.HTTP_200_OK)
    async def get_all(self, page: int = 1, page_size: int = 10):
        result = await self._service.get_all(page, page_size)
        return Response(
            message="Employee Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )
        
    @employee_router.post("/query", status_code=status.HTTP_200_OK)
    async def query(self, filter: list[dict], page: int = 1, page_size: int = 10):
        result = await self._service.query(filter, page, page_size)
        return Response(
            message="Employee Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )