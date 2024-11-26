import secrets
from datetime import datetime, timedelta
from hashlib import md5
from typing import Any, Optional, Union

from fastapi import Depends, HTTPException,status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.employee.models import Employee
from app.schemas.api import ResponseStatus

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a hashed password and a plain password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    payload = {
        "exp": expire,
        "sub": str(subject),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)



def verify_token(access_token: str):
    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        sub: str = payload.get("sub")
        if not sub:
            return {"success": False, "message": "Missing subject"}
        return {"success": True, "message": "Token is valid", "sub": sub}
    except jwt.InvalidTokenError as err:
        return {"success": False, "message": str(err)}
    except jwt.ExpiredSignatureError as err:
        return {"success": False, "message": str(err)}
    


async def authenticate(credentials : HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> Employee:
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[ALGORITHM])
        employee_id: str = payload.get("sub")
        if not employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Missing subject",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        employee = await Employee.find_one(Employee.employee_id == employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Employee not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        return employee
    
    except jwt.ExpiredSignatureError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": str(err),
                "success": False,
                "status": ResponseStatus.FAILED.value,
                "data": None,
            },
        )