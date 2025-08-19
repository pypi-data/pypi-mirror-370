from datetime import date

from fastapi import APIRouter
from kink import di
from appodus_utils.common.utils_settings import utils_settings
from appodus_utils.config.bootstrap import BaseDiBootstrap

from appodus_utils import Page, RouterUtils
from appodus_utils.db.models import SuccessResponse
from appodus_utils.domain.user.address.controller import address_router
from appodus_utils.domain.user.auth.controller import auth_router
from appodus_utils.domain.user.auth.models import LoginSuccessDto, EmailValidationRequest
from appodus_utils.domain.user.models import CreateUserDto, UpdateNameDto, Gender, SearchUserDto, QueryUserDto
from appodus_utils.domain.user.service import UserService

user_router = APIRouter(prefix="/users", tags=["Users"])

RouterUtils.add_routers(user_router, [auth_router, address_router])

BaseDiBootstrap.register_subclass_if_exists(UserService)
user_service: UserService = di[UserService]


@user_router.post("/")
async def user_create(
        dto: CreateUserDto
) -> LoginSuccessDto:
    return await user_service.create_user(dto)


@user_router.patch("/active-user/name", response_model=SuccessResponse[QueryUserDto])
async def update_active_user_name(
        update_dto: UpdateNameDto
) -> SuccessResponse[QueryUserDto]:
    return await user_service.update_active_user_name(update_dto=update_dto)


@user_router.patch("/active-user/deactivate", response_model=SuccessResponse[bool])
async def deactivate_active_user(
        reason: str
) -> SuccessResponse[bool]:
    return await user_service.deactivate_active_user(reason)


@user_router.patch("/active-user/activate", response_model=SuccessResponse[bool])
async def activate_active_user(
        user_id: str,
        reason: str
) -> SuccessResponse[bool]:
    return await user_service.activate_user(user_id, reason)


@user_router.post("/active-user/validate-phone", response_model=SuccessResponse[bool])
async def send_phone_validation_message(
        phone_ext: str,
        phone: str
) -> SuccessResponse[bool]:
    return await user_service.send_phone_validation_message(phone_ext, phone)


@user_router.post("/active-user/validate-email", response_model=SuccessResponse[bool])
async def send_email_validation_message(
        payload: EmailValidationRequest
) -> SuccessResponse[bool]:
    return await user_service.send_email_validation_message(payload)


@user_router.patch("/active-user/phone", response_model=SuccessResponse[bool])
async def update_phone(
        otp: str
) -> SuccessResponse[bool]:
    return await user_service.update_phone(
        otp
    )


@user_router.patch("/active-user/email", response_model=SuccessResponse[bool])
async def update_email(
        email: str, otp: str
) -> SuccessResponse[bool]:
    return await user_service.update_email(email, otp)

@user_router.patch("/active-user/gender", response_model=SuccessResponse[bool])
async def update_gender(
        gender: Gender
) -> SuccessResponse[bool]:
    return await user_service.update_gender(gender)


@user_router.patch("/active-user/dob", response_model=SuccessResponse[bool])
async def update_dob(
        dob: date
) -> SuccessResponse[bool]:
    return await user_service.update_dob(dob)

@user_router.post("/validate-email-otp", response_model=SuccessResponse[bool])
async def validate_email_verification_otp(
            email: str, otp: str
) -> SuccessResponse[bool]:
    """
    This should only be used pre-user creation.
    To validate email verification otp, and store the email for use during user creation.

    :param email:
    :param otp:
    :return:
    """
    return await user_service.validate_and_store_email_verification_otp(email, otp)


@user_router.post("/search", response_model=Page[QueryUserDto])
async def search_users(dto: SearchUserDto) -> Page[QueryUserDto]:
    return await user_service.get_user_page(dto)

# @user_router.post("/search-profile")
# async def search_users_profile_page(dto: SearchUserAndProfileDto) -> Page[QueryUserAndProfileDto]:
#     return await user_service.get_user_with_profile_page(dto)


@user_router.get("/{user_id}", response_model=SuccessResponse[QueryUserDto])
async def get_user(user_id: str) -> SuccessResponse[QueryUserDto]:
    return await user_service.get_user(user_id)
