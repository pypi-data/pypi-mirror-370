from datetime import timedelta, date
from logging import Logger
from typing import Optional, List

from appodus_utils import Page
from appodus_utils import Utils
from fastapi.encoders import jsonable_encoder
from kink import inject, di

from appodus_utils.common.auth_utils import JwtAuthUtils
from appodus_utils.db.models import SuccessResponse
from appodus_utils.db.redis_utils import RedisUtils
from appodus_utils.decorators.decorate_all_methods import decorate_all_methods
from appodus_utils.decorators.method_trace_logger import method_trace_logger
from appodus_utils.decorators.transactional import transactional, TransactionSessionPolicy
from appodus_utils.domain.user.auth.active_auditor.service import ActiveAuditorService
from appodus_utils.domain.user.auth.models import LoginSuccessDto, EmailValidationRequest
from appodus_utils.domain.user.models import CreateUserDto, _CreateUserDto, User, QueryUserDto, SearchUserDto, \
    _UpdateUserDto, UpdateNameDto, UserStatus, Gender, KYCAgent, CreateUserOptionalPasswordDto
from appodus_utils.domain.user.repo import UserRepo
from appodus_utils.domain.user.validator import UserValidator
from appodus_utils.exception.exceptions import InvalidTokenException
from appodus_utils.integrations.messaging.models import MessageRecipientUserId, MessageContextModule, \
    MessageRequestRecipient

logger: Logger = di['logger']

@inject
@decorate_all_methods(transactional(), exclude=['get_account_security_messages'])
@decorate_all_methods(method_trace_logger, exclude=['get_account_security_messages'])
class UserService:
    def __init__(self, user_repo: UserRepo,
                 user_validator: UserValidator,
                 active_auditor_service: ActiveAuditorService
                 ):
        self._user_repo = user_repo
        self._user_validator = user_validator
        self._active_auditor_service = active_auditor_service
        self._otp_token_expire_seconds = int(Utils.get_from_env_fail_if_not_exists("EMAIL_OTP_TOKEN_EXPIRE_SECONDS"))
        self._email_otp_token_expire_seconds = int(Utils.get_from_env_fail_if_not_exists("EMAIL_OTP_TOKEN_EXPIRE_SECONDS"))

    async def get_account_security_messages(self):
        """
        Returns an instance of AccountSecurityMessages from our dependency injector, kink.
        This method is here to avoid static dependency issues.
        :return:
        """
        from appodus_utils.domain.user.user_messages import AccountSecurityMessages

        return di[AccountSecurityMessages]

    async def create_user_optional_password(self, obj_in: CreateUserOptionalPasswordDto) -> LoginSuccessDto:
        await self._user_validator.should_not_exist_by_email(obj_in.email)
        await self._validate_email_verification_otp(email=str(obj_in.email), otp=obj_in.otp)

        obj_in_copy = obj_in.model_copy()

        if obj_in.password:
            obj_in_copy.password = Utils.get_password_hash(obj_in.password)

        create_user_dto = _CreateUserDto(**obj_in_copy.model_dump())
        user_response = await self._user_repo.create(create_user_dto.model_dump(exclude={'otp', 'timezone', 'locale'}))
        user = user_response.data

        await self.post_create_user(created_user=user)

        user_data = await self.combine_profile_data(user)

        # Welcome message
        await (await self.get_account_security_messages()).send_new_user_welcome_message(
            recipient_user_id=MessageRecipientUserId(user_id=user.id),
            context_modules=[MessageContextModule.USER]
        )

        authorizer = await self._active_auditor_service.get_authorizer_from_context()
        return await JwtAuthUtils.login_success(user_data, authorizer)

    async def create_user(self, obj_in: CreateUserDto) -> LoginSuccessDto:
        return await self.create_user_optional_password(obj_in=obj_in)

    async def post_create_user(self, created_user: QueryUserDto):
        """
        Use to handle all post user creation operations like, settings and profile creation. Please override

        :param created_user:
        :return:
        """
        pass

    async def combine_profile_data(self, user: QueryUserDto):
        """
        Use to combine user and profile data for return user details after successful auth

        :param user:
        :return:
        """
        user_data = jsonable_encoder(user)
        return user_data

    async def get_user(self, user_id: str) -> SuccessResponse[QueryUserDto]:
        await self._user_validator.should_exist_by_id(user_id)
        return await self._user_repo.get(user_id)

    async def get_user_model(self, user_id: str, query_fields: Optional[str] = None) -> User:
        await self._user_validator.should_exist_by_id(user_id)
        return await self._user_repo.get_model(user_id, query_fields)

    async def exists_by_email(self, email: str) -> bool:
        return await self._user_repo.exists_by_email(email)

    async def get_by_email(self, email: str) -> Optional[QueryUserDto]:
        user = await self._user_repo.get_by_email(email)

        return user

    async def get_user_page(self, search_dto: SearchUserDto) -> Page[QueryUserDto]:
        return await self._user_repo.get_page(search_dto=search_dto)

    # async def update_by_admin(self, user_id: str, obj_in: Union[UpdateUserDto, Dict[str, Any]]) -> bool:
    #     await self._user_validator.should_exist_by_id(user_id)
    #     await self._user_repo.update(user_id, obj_in)
    #
    #     return True

    async def update_user_change_password(self, new_password: str) -> SuccessResponse[QueryUserDto]:
        _, authorizer = await self._active_auditor_service.get_combined_authorizer_from_context()
        authorizer.fresh_jwt_required()

        user_id = authorizer.get_jwt_subject()

        password_last_updated = Utils.datetime_now_to_db()
        obj_in = _UpdateUserDto(password=Utils.get_password_hash(new_password),
                                password_last_updated=password_last_updated)

        updated_user = await self._user_repo.update(user_id, obj_in.model_dump(exclude_none=True))

        await (await self.get_account_security_messages()).send_password_updated_message(
            recipient_user_id=MessageRecipientUserId(user_id=user_id),
            context_modules=[MessageContextModule.USER])

        return updated_user

    async def update_last_active(self, user_id: str) -> SuccessResponse[QueryUserDto]:
        obj_in = _UpdateUserDto(last_active_date=Utils.datetime_now_to_db())
        return await self._user_repo.update(user_id, obj_in.model_dump(exclude_none=True))

    async def update_active_user_name(self, update_dto: UpdateNameDto) -> SuccessResponse[QueryUserDto]:
        _, authorizer = await self._active_auditor_service.get_combined_authorizer_from_context()
        authorizer.fresh_jwt_required()

        user_id = authorizer.get_jwt_subject()
        dto_data = jsonable_encoder(update_dto)
        obj_in = _UpdateUserDto(**dto_data)
        updated_user = await self._user_repo.update(user_id, obj_in.model_dump(exclude_none=True))

        await (await self.get_account_security_messages()).send_name_updated_message(
            recipient_user_id=MessageRecipientUserId(user_id=user_id),
            context_modules=[MessageContextModule.USER])

        return updated_user

    async def soft_delete_by_admin(self, user_id: str) -> SuccessResponse[bool]:
        await self._user_validator.should_exist_by_id(user_id)
        await self._user_repo.soft_delete(user_id)

        return SuccessResponse(
            data=True
        )

    async def deactivate_active_user(self, reason: str) -> SuccessResponse[bool]:
        _, authorizer = await self._active_auditor_service.get_combined_authorizer_from_context()
        authorizer.fresh_jwt_required()
        user_id = authorizer.get_jwt_subject()

        obj_in = _UpdateUserDto(status=UserStatus.DEACTIVATED, notes=reason)
        await self._user_repo.update(user_id, obj_in.model_dump(exclude_none=True))

        await (await self.get_account_security_messages()).send_account_deactivation_message(
            recipient_user_id=MessageRecipientUserId(user_id=user_id),
            context_modules=[MessageContextModule.USER],
            extra_context={
                "reason": reason
            }
        )

        return SuccessResponse(
            data=True
        )

    async def activate_user(self, user_id: str, reason: str) -> SuccessResponse[bool]:
        _, authorizer = await self._active_auditor_service.get_combined_authorizer_from_context()
        authorizer.jwt_required()

        obj_in = _UpdateUserDto(status=UserStatus.ACTIVE, notes=reason)
        await self._user_repo.update(user_id, obj_in.model_dump(exclude_none=True))

        await (await self.get_account_security_messages()).send_account_activation_message(
            recipient_user_id=MessageRecipientUserId(user_id=user_id),
            context_modules=[MessageContextModule.USER],
            extra_context={
                "reason": reason
            }
        )

        return SuccessResponse(
            data=True
        )

    async def send_phone_validation_message(self, phone_ext: str, phone: str) -> SuccessResponse[bool]:
        _, authorizer = await self._active_auditor_service.get_combined_authorizer_from_context()
        authorizer.jwt_required()
        user_id = authorizer.get_jwt_subject()
        otp = Utils.get_otp_code('i')

        time_to_live = timedelta(seconds=self._otp_token_expire_seconds)
        phone_delimited = f'{phone_ext}:{phone}'

        store_key = f'{user_id}:{otp}'
        await RedisUtils.set_redis(store_key, phone_delimited, time_to_live)


        await (await self.get_account_security_messages()).send_phone_verification_message(
            recipient_user_id=MessageRecipientUserId(user_id=user_id),
            context_modules=[MessageContextModule.USER],
            extra_context={
                "otp": otp,
                "phone_ext": phone_ext,
                "phone": phone
            }
        )

        return SuccessResponse(
            data=True
        )

    async def update_phone(self, otp: str) -> SuccessResponse[bool]:
        _, authorizer = await self._active_auditor_service.get_combined_authorizer_from_context()
        authorizer.fresh_jwt_required()
        user_id = authorizer.get_jwt_subject()

        store_key = f'{user_id}:{otp}'
        phone_str = await RedisUtils.get_redis(store_key)
        if not phone_str:
            raise InvalidTokenException()

        phone_arr = phone_str.split(":")
        phone_ext = phone_arr[0]
        phone = phone_arr[1]

        obj_in = _UpdateUserDto(
            phone_ext=phone_ext,
            phone=phone,
            phone_validated=True
        )
        await self._user_repo.update(user_id, obj_in.model_dump(exclude_none=True))

        return SuccessResponse(
            data=True
        )

    async def send_email_validation_message(self, payload: EmailValidationRequest, is_a_new_user: bool = True) -> SuccessResponse[bool]:
        if is_a_new_user:
            await self._user_validator.should_not_exist_by_email(payload.email)

        otp = Utils.get_otp_code()
        store_key = f'{payload.email}:{otp}'

        time_to_live = timedelta(seconds=self._otp_token_expire_seconds)
        await RedisUtils.set_redis(store_key, payload.email, time_to_live)

        if is_a_new_user:
            await (await self.get_account_security_messages()).send_direct_email_verification_message(
                recipient=MessageRequestRecipient(
                    user_id="pending_user_id",
                    fullname="Guest",
                    email=payload.email
                ),
                context={
                    "otp": otp,
                }
            )
        else:
            _, authorizer = await self._active_auditor_service.get_combined_authorizer_from_context()
            authorizer.fresh_jwt_required()
            user_id = authorizer.get_jwt_subject()

            await (await self.get_account_security_messages()).send_email_verification_message(
                recipient_user_id=MessageRecipientUserId(user_id=user_id),
                context_modules=[MessageContextModule.USER],
                extra_context={
                    "otp": otp,
                }
            )

        return SuccessResponse(
            data=True
        )

    @staticmethod
    async def _validate_email_verification_otp(email: str, otp: str) -> SuccessResponse[bool]:
        store_key = f'{email}:{otp}'
        new_email = await RedisUtils.get_redis(store_key)
        if not new_email:
            raise InvalidTokenException()

        return SuccessResponse(
            data=True
        )

    async def store_verified_email_otp(self, email: str, otp: str):
        store_key = f'{email}:{otp}'
        time_to_live = timedelta(minutes=self._email_otp_token_expire_seconds)
        await RedisUtils.set_redis(store_key, email, time_to_live)

    async def validate_and_store_email_verification_otp(self, email: str, otp: str) -> SuccessResponse[bool]:
        await self._validate_email_verification_otp(email=email, otp=otp)

        await self.store_verified_email_otp(email=email, otp=otp)

        return SuccessResponse(
            data=True
        )

    async def update_email(self, email: str, otp: str) -> SuccessResponse[bool]:
        await self._validate_email_verification_otp(email=email, otp=otp)

        _, authorizer = await self._active_auditor_service.get_combined_authorizer_from_context()
        authorizer.fresh_jwt_required()
        user_id = authorizer.get_jwt_subject()

        obj_in = _UpdateUserDto(
            email=email,
            email_validated=True
        )
        await self._user_repo.update(user_id, obj_in.model_dump(exclude_none=True))

        return SuccessResponse(
            data=True
        )

    async def update_gender(self, gender: Gender) -> SuccessResponse[bool]:
        _, authorizer = await self._active_auditor_service.get_combined_authorizer_from_context()
        authorizer.fresh_jwt_required()
        user_id = authorizer.get_jwt_subject()

        obj_in = _UpdateUserDto(gender=gender)
        await self._user_repo.update(user_id, obj_in.model_dump(exclude_none=True))

        return SuccessResponse(
            data=True
        )

    async def update_dob(self, dob: date) -> SuccessResponse[bool]:
        _, authorizer = await self._active_auditor_service.get_combined_authorizer_from_context()
        authorizer.fresh_jwt_required()
        user_id = authorizer.get_jwt_subject()


        obj_in = _UpdateUserDto(dob=dob)
        await self._user_repo.update(user_id, obj_in.model_dump(exclude_none=True))

        return SuccessResponse(
            data=True
        )

    async def get_logged_user_page(self, search_dto: SearchUserDto) -> Page[QueryUserDto]:
        return await self._user_repo.get_page(search_dto=search_dto)

    async def get_user_pending_kyc(self) -> List[KYCAgent]:
        _, authorizer = await self._active_auditor_service.get_combined_authorizer_from_context()
        authorizer.jwt_required()
        user_id = authorizer.get_jwt_subject()

        user_response = await self.get_user(user_id=user_id)
        user = user_response.data

        pending_kyc = []

        if not user.email_validated:
            pending_kyc.append(KYCAgent.EMAIL)
        if not user.phone_validated:
            pending_kyc.append(KYCAgent.PHONE)
        if not user.bvn_validated:
            pending_kyc.append(KYCAgent.BVN)
        if not user.address_validated:
            pending_kyc.append(KYCAgent.ADDRESS)
        if not user.has_profile_picture:
            pending_kyc.append(KYCAgent.PROFILE_PICTURE)
        if not user.identity_validated:
            pending_kyc.append(KYCAgent.IDENTITY)

        return pending_kyc




    # async def update_active_user_picture(self, profile_picture: UploadFile) -> bool:
    #     profile_id = await self._active_auditor_service.get_profile_id()
    #
    #     file_dto = CreateStoredFileDto(
    #         owner=FileOwner.GUEST,
    #         owner_id=user_id,
    #         type=FileType.PROFILE,
    #         files=[profile_picture]
    #     )
    #
    #     if background_tasks:
    #         background_tasks.add_task(self._stored_file_service.create_file, file_dto, authorizer, background_tasks)
    #     else:
    #         await self._stored_file_service.create_file(file_dto, authorizer, background_tasks)
    #
    #     await self._profile_validator.should_exist_by_id(profile_id)
    #     obj_in = _UpdateProfileDto(has_profile_picture=True)
    #     updated = await self._profile_repo.update(profile_id, obj_in.model_dump(exclude_none=True))
    #
    #     return updated.has_profile_picture
    #
    # async def update_active_user_selfie(self, profile_selfie: UploadFile,
    #                                     background_tasks: BackgroundTasks = None) -> bool:
    #     profile_id = await self._active_auditor_service.get_profile_id()
    #     await self._profile_validator.should_exist_by_id(profile_id)
    #
    #     file_dto = CreateStoredFileDto(
    #         owner=FileOwner.GUEST,
    #         owner_id=user_id,
    #         type=FileType.SELFIE,
    #         files=[profile_selfie]
    #     )
    #
    #     if background_tasks:
    #         background_tasks.add_task(self._stored_file_service.create_file, file_dto, authorizer, background_tasks)
    #     else:
    #         await self._stored_file_service.create_file(file_dto, authorizer, background_tasks)
    #
    #     obj_in = _UpdateProfileDto(has_selfie_picture=True)
    #     updated = await self._profile_repo.update(profile_id, obj_in.model_dump(exclude_none=True))
    #
    #     return updated.has_selfie_picture



    # async def update_active_user_bvn(self, bvn: str) -> bool:
    #     profile_id = await self._active_auditor_service.get_profile_id()
    #     await self._profile_validator.should_exist_by_id(profile_id)
    #     obj_in = _UpdateProfileDto(bvn=bvn)
    #     updated = await self._profile_repo.update(profile_id, obj_in.model_dump(exclude_none=True))
    #     return updated.bvn == bvn
    #
    # async def bvn_validated(self) -> bool:
    #     profile_id = await self._active_auditor_service.get_profile_id()
    #     await self._profile_validator.should_exist_by_id(profile_id)
    #     obj_in = _UpdateProfileDto(bvn_validated=True)
    #     updated = await self._profile_repo.update(profile_id, obj_in.model_dump(exclude_none=True))
    #     return updated.bvn_validated
    #
    # async def identity_validated(self) -> bool:
    #     profile_id = await self._active_auditor_service.get_profile_id()
    #     await self._profile_validator.should_exist_by_id(profile_id)
    #     obj_in = _UpdateProfileDto(identity_validated=True)
    #     updated = await self._profile_repo.update(profile_id, obj_in.model_dump(exclude_none=True))
    #
    #     return updated.identity_validated
