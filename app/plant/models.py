from pydantic import BaseModel
from typing import Optional
from beanie import Document, Indexed

class PlantModel(BaseModel):
    name: str  # type: ignore
    plant_code: str

class Plant(PlantModel, Document):
    pass



class PlantUpdate(BaseModel):
    name: Optional[str]= None
    plant_code: Optional[str] = None