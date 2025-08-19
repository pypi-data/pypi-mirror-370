from appodus_utils import Page, Utils
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from kink import di

from appodus_utils.db.models import SuccessResponse
from appodus_utils.domain.user.auth.models import EmailLoginRequest, Token, LoginSuccessDto, ChangePasswordDto, \
    PasswordResetRequest, PasswordResetConfirm
from appodus_utils.domain.user.auth.service import AuthService
from appodus_utils.domain.user.auth.social_login.controller import social_auth_router
from appodus_utils.domain.user.models import QueryUserDto, SearchUserDto
from appodus_utils.domain.user.service import UserService

auth_path = Utils.get_from_env_fail_if_not_exists("AUTH_URL_PATH")
auth_router = APIRouter(prefix=auth_path, tags=["Auth"])
auth_router.include_router(social_auth_router)

auth_service = di[AuthService]
user_service = di[UserService]


@auth_router.post("/access-token", summary='Authenticate and get access token', response_model=Token,
                  status_code=status.HTTP_200_OK)
async def access_token(auth_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    login_dto = EmailLoginRequest(username=auth_data.username, password=auth_data.password)
    return (await auth_service.basic_login(login_dto)).token


@auth_router.post("/login", summary='Login', response_model=LoginSuccessDto, status_code=status.HTTP_200_OK)
async def login(auth_data: EmailLoginRequest) -> LoginSuccessDto:
    return await auth_service.basic_login(auth_data)


@auth_router.post("/refresh-token", response_model=SuccessResponse[bool])
async def auth_refresh_token() -> SuccessResponse[bool]:
    return await auth_service.refresh_token()


@auth_router.post("/logout", response_model=SuccessResponse[bool])
async def auth_logout() -> SuccessResponse[bool]:
    return await auth_service.logout()


@auth_router.get("/logged-users", response_model=Page[QueryUserDto])
async def auth_logged_users(search_dto: SearchUserDto):
    return await user_service.get_logged_user_page(search_dto)


@auth_router.patch("/change-password", response_model=SuccessResponse[bool])
async def change_password(payload: ChangePasswordDto) -> SuccessResponse[bool]:
    return await auth_service.change_password(payload)


@auth_router.post("/recover-password/message", response_model=SuccessResponse[bool])
async def send_password_recovery_message(payload: PasswordResetRequest) -> SuccessResponse[bool]:
    return await auth_service.send_password_recovery_message(payload)


@auth_router.post("/recover-password", response_model=LoginSuccessDto)
async def recover_password(payload: PasswordResetConfirm):
    return await auth_service.recover_password(payload)


@auth_router.get("/profile", response_model=LoginSuccessDto)
async def get_active_user_profile():
    return {}
