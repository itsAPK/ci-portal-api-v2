
from pydantic import BaseModel
from app.schemas.db import BaseDocument


class BussinessUnitModel(BaseModel):
    name : str
    
    
class BussinessUnit(BaseDocument,BussinessUnitModel):
    pass

class BussinessUnitRequest(BaseModel):
    name : str