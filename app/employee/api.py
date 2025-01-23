from beanie import PydanticObjectId
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, status

from app.core.security import authenticate
from app.employee.models import  Employee, EmployeeModel, EmployeeUpdate, PlantChangeRequest, Role
from app.employee.service import EmployeeService
from app.schemas.api import FilterRequest, Response, ResponseStatus
from app.utils.class_based_views import cbv


employee_router = APIRouter()


@cbv(employee_router)
class EmployeeRouter:
    _service: EmployeeService = Depends(EmployeeService)
  

    @employee_router.post("/", status_code=status.HTTP_201_CREATED)
    async def create(self, employee: EmployeeModel):
        print(employee)
        result = await self._service.create(employee)
        return Response(
            message="Employee Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=None
        )
        
    @employee_router.patch("/{id}", status_code=status.HTTP_200_OK)
    async def update(self, id: PydanticObjectId, employee: EmployeeUpdate):
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
        
    @employee_router.get("/by-id/{employee_id}", status_code=status.HTTP_200_OK)
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
        
    @employee_router.post("/upload", status_code=status.HTTP_200_OK)
    async def upload(self, file: UploadFile,background_tasks: BackgroundTasks):
        result = await self._service.upload_excel_in_background(background_tasks, await file.read())
        return Response(
            message="Employees are uploading, It will take sometime..",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )
        
    @employee_router.post("/query", status_code=status.HTTP_200_OK)
    async def query(self, data: FilterRequest, page: int = 1, page_size: int = 10):
        result = await self._service.query(data.filter, page, page_size)
        return Response(
            message="Employee Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )
        
    @employee_router.post("/export", status_code=status.HTTP_200_OK)
    async def query_export(self, data: FilterRequest):
        result = await self._service.export_query(data.filter)
        return Response(
            message="Employee Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )
        
    @employee_router.post("/plant-change", status_code=status.HTTP_201_CREATED)
    async def create_plant_change(self, data: PlantChangeRequest):
        print(data)
        result = await self._service.create_plant_change(PlantChangeRequest(
            **data.model_dump(),
           
        ))
        return Response(
            message="Plant Change Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )
        
    @employee_router.get("/plant-change", status_code=status.HTTP_200_OK)
    async def get_plant_changes(self, employee_id: str):
        result = await self._service.get_plant_changes(employee_id)
        return Response(
            message="Plant Change Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )
        
    @employee_router.post('/plant-change/query',status_code=status.HTTP_200_OK)
    async def query_plant_change(self, data: FilterRequest, page: int = 1, page_size: int = 10):
        result = await self._service.plant_change_query(data.filter, page, page_size)
        return Response(
            message="Plant Change Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )
        
    @employee_router.get("/plant-change/approve/{id}", status_code=status.HTTP_200_OK)
    async def approve_plant_change(self, id:  PydanticObjectId):
        if self.user.role != Role.admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Only admin can approve plant change",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        result = await self._service.approve_plant_change(id)
        return Response(
            message="Plant Change Approved Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result,
        )
        
    @employee_router.get("/plant-change/reject/{id}", status_code=status.HTTP_200_OK)
    async def reject_plant_change(self, id: PydanticObjectId):
        if self.user.role != Role.admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Only admin can reject plant change",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        result = await self._service.reject_plant_change(id)
        return Response(
            message="Plant Change Rejected Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result,
        )
        
        
    @employee_router.get("/count/", status_code=status.HTTP_200_OK)
    async def count(self):
        result = await self._service.count()
        return Response(
            message="Employee Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data={"employee" : result},
        )

    
    
    
    