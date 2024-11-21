from datetime import datetime
from enum import Enum
from typing import Optional
from beanie import Document
from pydantic import BaseModel

class Role(str, Enum):
    ci_head = "ci_head"
    admin = "admin"
    hod = "hod"
    project_leader = "project_leader"
    lof="lof"
    cs_head="cs_head"
    employee = "employee"

class EmployeeModel(BaseModel):
    employee_id: str
    name: str
    email: str
    password: str
    plant : str
    company : str
    department : str
    date_of_birth : datetime
    date_of_joining : datetime
    role  : Optional[Role] = Role.employee
    grade : str
    is_active : Optional[bool] = True
    working_location : Optional[str] = None
    designation : Optional[str] = None
    bussiness_unit : Optional[str] = None

class Employee(Document, EmployeeModel):
    pass


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    plant : Optional[str] = None
    company : Optional[str] = None
    department : Optional[str] = None
    date_of_birth : Optional[datetime] = None
    date_of_joining : Optional[datetime] = None
    role  : Optional[Role] = None
    grade : Optional[str] = None
    employee_id: Optional[str] = None
    is_active : Optional[bool] = None
    working_location : Optional[str] = None
    designation : Optional[str] = None
    bussiness_unit : Optional[str] = None