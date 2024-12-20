from pydantic import BaseModel
from typing import Optional
from beanie import Document, Indexed, PydanticObjectId

from app.employee.models import Employee

class PlantModel(BaseModel):
    name: str  # type: ignore
    plant_code: str
    ci_head : Optional[Employee] = None
    ci_team : Optional[Employee] = None
    cs_head : Optional[Employee] = None
    lof : Optional[Employee] = None
    hod : Optional[Employee] = None  

class Plant(PlantModel, Document):
    pass




class PlantUpdate(BaseModel):
    name: Optional[str]= None
    plant_code: Optional[str] = None
    

class AssignCIHeadUser(BaseModel):
    plant_id : PydanticObjectId
    hod : PydanticObjectId
    ci_head : PydanticObjectId
    lof : PydanticObjectId
    cs_head : PydanticObjectId
    ci_team : PydanticObjectId