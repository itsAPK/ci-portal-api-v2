
from pydantic import BaseModel
from typing import Optional 
from beanie import Document, Indexed, Link

from app.employee.models import Employee
from app.schemas.db import BaseDocument


class ArchiveModel(BaseModel):
    company : str
    department : str
    category : str
    year: str
    project_title : str
    baseline : str
    target : str
    result : str
    

class Archive(ArchiveModel, BaseDocument):
    uploaded_by : Link[Employee]
    file_path : str



class ArchiveRequest(ArchiveModel,BaseModel):
    file_path : str
    uploaded_by : str
    


class ArchiveUpdate(BaseModel): 
    company : Optional[str] = None
    department : Optional[str] = None
    category : Optional[str] = None
    year: Optional[str] = None
    project_title : Optional[str] = None
    baseline : Optional[str] = None
    target : Optional[str] = None
    result : Optional[str] = None
    file_path : Optional[str] = None
    uploaded_by : Optional[Link[Employee]] = None