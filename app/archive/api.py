import json
import os
import shutil
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, File, Form, UploadFile,status
from app.core.security import authenticate
from app.utils.class_based_views import cbv
from app.employee.models import Employee
from app.schemas.api import FilterRequest, Response, ResponseStatus
from app.archive.models import Archive, ArchiveCumulativeRequest, ArchiveModel, ArchiveRequest
from app.archive.service import ArchiveCumulativeService, ArchiveService

archive_router = APIRouter()

UPLOAD_PATH = "uploads/archive"

@cbv(archive_router)
class ArchiveRouter:
    user: Employee = Depends(authenticate)
    _service: ArchiveService = Depends(ArchiveService)
    _cumulative_service: ArchiveCumulativeService = Depends(ArchiveCumulativeService)

    @archive_router.post("/", status_code=status.HTTP_201_CREATED)
    async def create(self, archive: str = Form(...), file: UploadFile = File(...)):
        os.makedirs(UPLOAD_PATH, exist_ok=True)
        
        file_path = os.path.join(UPLOAD_PATH, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        archive_data = json.loads(archive) 
        print(archive_data) 

        result = await self._service.create(ArchiveRequest(
            **archive_data,
            uploaded_by=PydanticObjectId(self.user.id),
            file_path=file_path,
        ))
        
  
        
        return Response(
            message="Archive Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )
        
        
    @archive_router.get("/{id}", status_code=status.HTTP_200_OK)
    async def get(self, id: PydanticObjectId):
        result = await self._service.get(id)
        return Response(
            message="Archive Retrieved Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )

    @archive_router.post("/query", status_code=status.HTTP_200_OK)
    async def query(self, data: FilterRequest, page: int = 1, page_size: int = 10):
        result = await self._service.query(data.filter, page, page_size)
        return Response(
            message="Archive Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )
        
    @archive_router.get("/", status_code=status.HTTP_200_OK)
    async def get_all(self, page: int = 1, page_size: int = 10):
        result = await self._service.get_all(page, page_size)
        return Response(
            message="Archive Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )

    @archive_router.delete("/{id}", status_code=status.HTTP_200_OK)
    async def delete(self, id: PydanticObjectId):
        result = await self._service.delete(id)
        return Response(
            message="Archive Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )
        
    @archive_router.post("/earse-all",status_code=status.HTTP_200_OK)
    async def delete_all(self):
        result = await self._service.delete_all()
        return Response(
            message="Archive Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )
        
        
    @archive_router.get("/cumulative", status_code=status.HTTP_200_OK)
    async def get_cumulative(self, page: int = 1, page_size: int = 10):
        result = await self._cumulative_service.get_all(page, page_size)
        return Response(
            message="Archive Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )
    
    @archive_router.post("/cumulative/export", status_code=status.HTTP_200_OK)
    async def export_cumulative(self, data: FilterRequest):
        result = await self._cumulative_service.export(data.filter)
        return Response(
            message="Archive Retrieved Successfully",
            success=True,
            status=ResponseStatus.RETRIEVED,
            data=result,
        )
    
    @archive_router.post("/cumulative", status_code=status.HTTP_201_CREATED)
    async def create_cumulative(self, data: ArchiveCumulativeRequest):
        result = await self._cumulative_service.create(data)
        return Response(
            message="Archive Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )
    
   

    @archive_router.delete("/cumulative/{id}", status_code=status.HTTP_200_OK)
    async def delete_cumulative(self, id: PydanticObjectId):
        result = await self._cumulative_service.delete(id)
        return Response(
            message="Archive Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )
        
