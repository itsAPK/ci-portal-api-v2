from pydantic import BaseModel
from typing import Optional 
from beanie import Document, Indexed
class DepartmentModel(BaseModel):
    name: str  # type: ignore
    department_code: str

class Department(DepartmentModel, Document):
    pass



class DepartmentUpdate(BaseModel):
    name: Optional[str]= None        
    department_code: Optional[str] = None