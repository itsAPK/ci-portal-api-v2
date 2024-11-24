from pydantic import BaseModel
from typing import Optional 
from beanie import Document, Indexed

from app.schemas.db import BaseDocument

class DocumentsModel(BaseModel):
    name: str  # type: ignore

class Documents(DocumentsModel, BaseDocument):
    path : str
    author : str
    author_id : str

class DocumentsUpdate(BaseModel):
    name: Optional[str] = None
