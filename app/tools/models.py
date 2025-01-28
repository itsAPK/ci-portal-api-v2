from pydantic import BaseModel
from typing import Optional 
from beanie import Document, Indexed

class ToolsModel(BaseModel):
    name: str  # type: ignore
    category : list[str]
    status : Optional[bool] = True

class Tools(ToolsModel, Document):
    pass



class ToolsUpdate(BaseModel):
    name: Optional[str] = None
    category : Optional[list[str]] = None
    status : Optional[bool] = None