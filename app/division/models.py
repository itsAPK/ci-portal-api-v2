from typing import Optional
from beanie import Document, Indexed
from pydantic import BaseModel

class DivisionModel(BaseModel):
    name: str  # type: ignore
    division_code: str

class Division(DivisionModel, Document):
    pass



class DivisionUpdate(BaseModel):
    name: Optional[str]= None
    division_code: Optional[str] = None
