from typing import Optional
from beanie import Document, Indexed
from pydantic import BaseModel


class CompanyModel(BaseModel):
    name: str  # type: ignore
    company_code: int

class Company(CompanyModel, Document):
    pass



class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    company_code: Optional[int] = None
