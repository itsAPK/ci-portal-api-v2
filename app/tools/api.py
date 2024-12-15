
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends,status
from app.employee.models import Employee
from app.schemas.api import FilterRequest, Response, ResponseStatus
from app.tools.models import ToolsModel, ToolsUpdate
from app.tools.service import ToolsService
from app.utils.class_based_views import cbv
from app.core.security import authenticate  # Assuming this is where the authenticate function is defined


tools_router = APIRouter()


@cbv(tools_router)
class ToolsRouter:
    user: Employee = Depends(authenticate)
    _service: ToolsService = Depends(ToolsService)

    @tools_router.post("/", status_code=status.HTTP_201_CREATED)
    async def create(self, tool: ToolsModel):
        result = await self._service.create(tool)
        return Response(
            message="Tool Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @tools_router.patch("/{id}", status_code=status.HTTP_200_OK)
    async def update(self, id: PydanticObjectId, tool: ToolsUpdate):
        result = await self._service.update(tool, id)
        return Response(
            message="Tool Updated Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result
        )

    @tools_router.delete("/{id}", status_code=status.HTTP_200_OK)
    async def delete(self, id: PydanticObjectId):
        result = await self._service.delete(id)
        return Response(
            message="Tool Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )

    @tools_router.get("/{id}", status_code=status.HTTP_200_OK)
    async def get(self, id: PydanticObjectId):
        result = await self._service.get(id)
        return Response(
            message="Tool Retrieved Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )

    @tools_router.get("/", status_code=status.HTTP_200_OK)
    async def get_all(self, page: int = 1, page_size: int = 10):
                result = await self._service.get_all(page, page_size)
                return Response(
                    message="Tools Retrieved Successfully",
                    success=True,
                    status=ResponseStatus.RETRIEVED,
                    data=result,
                )
            
    @tools_router.post("/query", status_code=status.HTTP_200_OK)
    async def query(self,  data: FilterRequest, page: int = 1, page_size: int = 10):
            result = await self._service.query(data.filter, page, page_size)
            return Response(
                message="Tools Retrieved Successfully",
                success=True,
                status=ResponseStatus.RETRIEVED,
                data=result,
            )
            
    @tools_router.post("/export", status_code=status.HTTP_200_OK)
    async def export(self,  data: FilterRequest):
        result = await self._service.query_export(data.filter)
        return Response(
            message="Tools Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )