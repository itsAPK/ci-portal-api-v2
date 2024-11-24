import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.core.security import authenticate
from app.employee.models import Employee
from app.files.service import FileService


files_router = APIRouter()

BASE_UPLOAD_FOLDER = "uploads"

class FileRouter:
    user: Employee = Depends(authenticate)
    _service: FileService = Depends(FileService)
    
    @files_router.get("/download/{bucket:path}")
    async def download_file(bucket: str):
        # Calculate the full file path
        file_path = os.path.join(BASE_UPLOAD_FOLDER, bucket)
        
        # Check if file exists
        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="File not found.")
        
        return FileResponse(file_path)