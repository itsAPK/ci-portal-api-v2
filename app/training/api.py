
from beanie import PydanticObjectId
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile,status

from app.core.security import authenticate
from app.employee.models import Employee
from app.schemas.api import FilterRequest, Response, ResponseStatus
from app.training.models import CumulativeTrainingRequest, CumulativeTrainingUpdate, TrainingRequest
from app.training.service import CumulativeTrainingService, TrainingService
from app.utils.class_based_views import cbv


training_router = APIRouter()

@cbv(training_router)
class TrainingRouter:
    user : Employee = Depends(authenticate)
    _service : TrainingService = Depends(TrainingService)
    _cumulative_service : CumulativeTrainingService = Depends(CumulativeTrainingService)
    
    @training_router.post("/", status_code=status.HTTP_201_CREATED)
    async def create(self, training : TrainingRequest):
        result = await self._service.create_training(training)
        return Response(
            message="Training Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )
    
    @training_router.get("/{id}", status_code=status.HTTP_200_OK)
    async def get(self, id : PydanticObjectId):
        result = await self._service.get_training(id)
        return Response(
            message="Training Retrieved Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )
    
    @training_router.post("/query", status_code=status.HTTP_200_OK)
    async def query(self, data : FilterRequest, page : int = 1, page_size : int = 10):
        print(data)
        result = await self._service.query_training(data.filter, page, page_size)
        return Response(
            message="Training Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )
        
    @training_router.post("/export", status_code=status.HTTP_200_OK)
    async def query_export(self, data : FilterRequest):
        result = await self._service.export_query_training(data.filter)
        return Response(
            message="Training Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )
        
    @training_router.patch("/{id}", status_code=status.HTTP_200_OK)
    async def update(self, id : PydanticObjectId, training : TrainingRequest):
        result = await self._service.update_training(training, id)
        return Response(
            message="Training Updated Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result,
        )
        
    @training_router.get("/", status_code=status.HTTP_200_OK)
    async def get_all(self, page : int = 1, page_size : int = 10):
        result = await self._service.get_all_training(page, page_size)
        return Response(
            message="Training Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )

    @training_router.delete("/{id}", status_code=status.HTTP_200_OK)
    async def delete(self, id : PydanticObjectId):
        result = await self._service.delete_training(id)
        print(result)
        return Response(
            message="Training Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )
    
    @training_router.post("/upload", status_code=status.HTTP_201_CREATED)
    async def upload(self, file : UploadFile,background_tasks: BackgroundTasks):
        result = await self._service.upload_training_in_background(background_tasks, await file.read())
        return Response(
            message="Certified Belts are uploading, It will take sometime..",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )
       
       
    @training_router.post("/erase-all", status_code=status.HTTP_201_CREATED)
    async def delete_all(self):
            results = await self._service.delete_all_trainings()
            return Response(
                message="All Trainings Deleted Successfully",
                success=True,
                status=ResponseStatus.CREATED,
                data=results,
            )

    
    @training_router.get("/get/cumulative", status_code=status.HTTP_200_OK)
    async def get_cumulative(self):
        result = await self._cumulative_service.get_all()
        return Response(
            message="Training Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )

    @training_router.post("/cumulative", status_code=status.HTTP_201_CREATED)
    async def create_cumulative(self, data: CumulativeTrainingRequest):
        result = await self._cumulative_service.create(data)
        return Response(
            message="Cumulative Training Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @training_router.patch("/cumulative/{id}", status_code=status.HTTP_200_OK)
    async def update_cumulative(self, id: PydanticObjectId, data: CumulativeTrainingUpdate):
        result = await self._cumulative_service.update(id, data)
        return Response(
            message="Cumulative Training Updated Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result,
        )

    @training_router.delete("/cumulative/{id}", status_code=status.HTTP_200_OK)
    async def delete_cumulative(self, id: PydanticObjectId):
        result = await self._cumulative_service.delete(id)
        return Response(
            message="Cumulative Training Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )
        
    @training_router.post('/cumulative/export', status_code=status.HTTP_200_OK)
    async def query_cumulative_export(self, data : FilterRequest):
        result = await self._cumulative_service.export_query(data.filter)
        return Response(
            message="Cumulative Training Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )
  