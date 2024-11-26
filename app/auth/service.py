from fastapi import HTTPException, status
from app.auth.models import Login, PasswordUpdateRequest
from app.core.security import create_access_token, get_password_hash, verify_password
from app.employee.service import EmployeeService
from app.schemas.api import ResponseStatus
from app.core.config import settings
from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Optional

import jwt

class AuthService:
    user_service: EmployeeService = EmployeeService()

    async def login(self, data: Login):
        user = await self.user_service.get_by_employee_id(data.employee_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Employee not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
            
        user_obj = user.model_dump()
        print(user_obj)
        
        authenticate = await verify_password(data.password, user_obj['password'])

        if not authenticate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Invalid Credintials",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        access_token = create_access_token(
            subject=user_obj["employee_id"],
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            ).total_seconds(),
            "user": {
                "id" : str(user_obj["id"]),
                "employee_id": user.employee_id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "plant": user.plant,
                "company": user.company,
                "department": user.department,
                "business_unit": user.bussiness_unit,
            },
        }


    def create_reset_token(email: str) -> str:
        expire = datetime.now() + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)
        token_data = {"sub": email, "exp": expire}
        return jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")

    def verify_reset_token(token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            email = payload.get("sub")
            return email
        except jwt.PyJWTError as err:
            print("error", err)
            return None
        
    async def password_reset(self, data : PasswordUpdateRequest):
        user = await self.user_service.get_by_email(data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Employee not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        
        if not verify_password(data.old_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Invalid Old Password",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        
        hashed_password = get_password_hash(data.new_password)
        
        await user.set({"password": hashed_password})
        await user.save()
        return {
            "message": "Password updated successfully",
            "success": True,
            "status": ResponseStatus.UPDATED,
            "data": None,
        }
    