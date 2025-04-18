 
from fastapi import APIRouter, Depends,status
from app.auth.models import ChangePasswordRequest, Login, PasswordUpdateRequest
from app.auth.service import AuthService
from app.core.security import authenticate
from app.employee.models import Employee
from app.utils.class_based_views import cbv
from app.schemas.api import Response, ResponseStatus



auth_router = APIRouter()


@cbv(auth_router)
class AuthRouter:
    # user: User = Depends(get_current_active_user)
    _service: AuthService = Depends(AuthService)

    @auth_router.post("/login", status_code=status.HTTP_200_OK)
    async def login(self, data: Login):
        result = await self._service.login(data)
        return Response(
            message="Login Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )

    @auth_router.post("/password-reset", status_code=status.HTTP_200_OK)
    async def password_reset(self, data: PasswordUpdateRequest):
        result = await self._service.password_reset(data)
        return Response(
            message="Password Reset Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )
        
    @auth_router.post("/change-password", status_code=status.HTTP_200_OK)
    async def change_password(self, data: ChangePasswordRequest,   user: Employee = Depends(authenticate)):
        result = await self._service.change_password(data, user_id=user.id)
        return Response(
            message="Password Updated Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )