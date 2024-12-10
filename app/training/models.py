from typing import Optional
from pydantic import BaseModel

from app.schemas.db import BaseDocument


class TrainingModel(BaseModel):
    employee_id: str
    name : str
    department : str
    grade : str
    working_location : str
    bussiness_unit : str
    plant : str
    company : str
    batch : str
    year : str
    trainer : str
    category : str
    
    
class Training(TrainingModel, BaseDocument):
    pass

class TrainingRequest(TrainingModel):
    pass

class TrainingUpdate(BaseModel):
    employee_id: Optional[str] | None = None
    name : Optional[str] | None = None
    department : Optional[str] | None = None
    grade : Optional[str] | None = None
    working_location : Optional[str] | None = None
    bussiness_unit : Optional[str] | None = None
    plant : Optional[str] | None = None
    company : Optional[str] | None = None
    batch : Optional[str] | None = None
    year : Optional[str] | None = None
    trainer : Optional[str] | None = None
    category : Optional[str] | None = None