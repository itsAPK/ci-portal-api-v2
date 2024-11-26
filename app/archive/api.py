import os
import shutil
from fastapi import APIRouter, Depends, File, UploadFile,status
from app.core.security import authenticate
from app.utils.class_based_views import cbv
from app.employee.models import Employee
from app.schemas.api import FilterRequest, Response, ResponseStatus
from app.archive.models import Archive, ArchiveModel, ArchiveRequest
from app.archive.service import ArchiveService

archive_router = APIRouter()

UPLOAD_PATH = "uploads/archive"

@cbv(archive_router)
class ArchiveRouter:
    user: Employee = Depends(authenticate)
    _service: ArchiveService = Depends(ArchiveService)

    @archive_router.post("/", status_code=status.HTTP_201_CREATED)
    async def create(self, archive: ArchiveModel, file: UploadFile = File(...)):
        os.makedirs(UPLOAD_PATH, exist_ok=True)
        
        file_path = os.path.join(UPLOAD_PATH, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        archive.file_path = file_path
        result = await self._service.create(ArchiveRequest(
            **archive.model_dump(),
            uploaded_by=self.user._id,
            file_path=file_path,
        ))
        
        return Response(
            message="Archive Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )
        
        
    @archive_router.get("/{id}", status_code=status.HTTP_200_OK)
    async def get(self, id: str):
        result = await self._service.get(id)
        return Response(
            message="Archive Retrieved Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )

    @archive_router.post("/query", status_code=status.HTTP_200_OK)
    async def query(self, data: FilterRequest, page: int = 1, page_size: int = 10):
        result = await self._service.query(data.query, page, page_size)
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
    async def delete(self, id: str):
        result = await self._service.delete(id)
        return Response(
            message="Archive Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )