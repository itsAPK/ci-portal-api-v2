
from pydantic import BaseModel


class Login(BaseModel):
    employee_id: str
    password: str
    
    
class ForgotPassword(BaseModel):
    email: str
    
    
class ResetPassword(BaseModel):
    token: str
    password: str
    
class PasswordUpdateRequest(BaseModel):
    old_password: str
    new_password: str
    email: str
    
    
class ChangePasswordRequest(BaseModel):
    new_password: str
    old_password: str