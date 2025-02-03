
import json
import os
import shutil
from fastapi import APIRouter, Depends, File, Form, UploadFile,status
from app.core.security import authenticate
from app.documents.models import Documents, DocumentsModel
from app.documents.service import DocumentsService
from app.employee.models import Employee
from app.schemas.api import Response, ResponseStatus
from app.utils.class_based_views import cbv


document_router = APIRouter()

UPLOAD_PATH = "uploads/template"

@cbv(document_router)
class DocumentRouter:
    user: Employee = Depends(authenticate)
    _service: DocumentsService = Depends(DocumentsService)

    @document_router.post("/", status_code=status.HTTP_201_CREATED)
    async def create(self, document: str = Form(...), file: UploadFile = File(...)):
        os.makedirs(UPLOAD_PATH, exist_ok=True)
        
        file_path = os.path.join(UPLOAD_PATH, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        archive_data = json.loads(document)
         
        result = await self._service.create(Documents(
            name=archive_data.get("name"),
            path=file_path,
            author=self.user.name,
            author_id=self.user.employee_id,
        ))
        
        return Response(
            message="Document Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )
        
    @document_router.get("/{id}", status_code=status.HTTP_200_OK)
    async def get(self, id: str):
        result = await self._service.get(id)
        return Response(
            message="Document Retrieved Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )

    @document_router.get("/", status_code=status.HTTP_200_OK)
    async def get_all(self):
        result = await self._service.get_all()
        return Response(
            message="Document Retrieved Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )

    @document_router.delete("/{id}", status_code=status.HTTP_200_OK)
    async def delete(self, id: str):
        result = await self._service.delete(id)
        return Response(
            message="Document Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )
        
    @document_router.post("/earse-all",status_code=status.HTTP_200_OK)
    async def delete_all(self):
        result = await self._service.delete_all()
        return Response(
            message="Document Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )