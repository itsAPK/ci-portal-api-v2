from pydantic import BaseModel
from typing import Optional
from beanie import Document, Indexed, Link, PydanticObjectId

from app.employee.models import Employee
from app.schemas.db import BaseDocument


class ArchiveModel(BaseModel):
    company: str
    department: str
    category: str
    year: str
    project_title: str
    baseline: str
    target: str
    result: str
    plant: str


class Archive(ArchiveModel, BaseDocument):
    uploaded_by: Employee
    file_path: str
    project_leader: Employee


class ArchiveRequest(ArchiveModel, BaseModel):
    file_path: str
    uploaded_by: PydanticObjectId
    project_leader: PydanticObjectId


class ArchiveUpdate(BaseModel):
    company: Optional[str] = None
    department: Optional[str] = None
    category: Optional[str] = None
    year: Optional[str] = None
    project_title: Optional[str] = None
    baseline: Optional[str] = None
    target: Optional[str] = None
    result: Optional[str] = None
    file_path: Optional[str] = None
    uploaded_by: Optional[PydanticObjectId] = None
    project_leader: Optional[PydanticObjectId] = None


class ArchiveCumulativeBase(BaseModel):
    year: str
    cumulative: int
    projects: int


class ArchiveCumulative(ArchiveCumulativeBase, BaseDocument):
    pass


class ArchiveCumulativeRequest(ArchiveCumulativeBase):
    pass


class ArchiveCumulativeUpdate(BaseModel):
    year: Optional[str] = None
    cumulative: Optional[int] = None
    total: Optional[int] = None
