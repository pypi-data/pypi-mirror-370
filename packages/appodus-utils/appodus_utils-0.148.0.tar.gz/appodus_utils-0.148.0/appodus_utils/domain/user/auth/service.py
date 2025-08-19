from datetime import timedelta
from logging import Logger

from appodus_utils import Utils
from kink import inject, di

from appodus_utils.common.auth_utils import JwtAuthUtils
from appodus_utils.db.models import SuccessResponse
from appodus_utils.db.redis_utils import RedisUtils
from appodus_utils.decorators.decorate_all_methods import decorate_all_methods
from appodus_utils.decorators.method_trace_logger import method_trace_logger
from appodus_utils.decorators.transactional import transactional, TransactionSessionPolicy
from appodus_utils.domain.user.auth.active_auditor.service import ActiveAuditorService
from appodus_utils.domain.user.auth.models import EmailLoginRequest, LoginSuccessDto, SocialLoginUserInfo, \
    SocialAuthOperationType, ChangePasswordDto, TokenType, PasswordResetRequest, PasswordResetConfirm, \
    SocialAuthResponseType
from appodus_utils.domain.user.auth.validator import AuthValidator
from appodus_utils.domain.user.models import CreateUserOptionalPasswordDto
from appodus_utils.domain.user.service import UserService
from appodus_utils.exception.exceptions import InvalidCredentialsException, InvalidTokenException, \
    NotImplementedException
from appodus_utils.integrations.messaging.models import MessageRecipientUserId, MessageContextModule

logger: Logger = di['logger']


@inject
@decorate_all_methods(transactional())
@decorate_all_methods(method_trace_logger)
class AuthService:
    def __init__(self, user_service: UserService, auth_validator: AuthValidator,
                 active_auditor_service: ActiveAuditorService,):
        self._user_service = user_service
        self._auth_validator = auth_validator
        self._active_auditor_service = active_auditor_service
        self.otp_token_expire_seconds = int(Utils.get_from_env_fail_if_not_exists("OTP_TOKEN_EXPIRE_SECONDS"))


    async def get_account_security_messages(self):
        """
        Returns an instance of AccountSecurityMessages from our dependency injector, kink.
        This method is here to avoid static dependency issues.
        :return:
        """
        from appodus_utils.domain.user.user_messages import AccountSecurityMessages

        return di[AccountSecurityMessages]

    async def basic_login(self, login_dto: EmailLoginRequest, verify_password: bool = True) -> LoginSuccessDto:
        user = await self._user_service.get_by_email(login_dto.username)
        if user:
            password_is_valid = False
            if verify_password:
                password_is_valid = Utils.verify_password(login_dto.password, user.password)
            if not verify_password or password_is_valid:
                user_id = user.id
                await self._user_service.update_last_active(user_id)
                user = await self._user_service.combine_profile_data(user)

                is_login_suspicious = False
                if is_login_suspicious: # TODO: implement this feature
                    await (await self.get_account_security_messages()).send_login_security_alert_message(
                        recipient_user_id=MessageRecipientUserId(user_id=user_id),
                        context_modules=[MessageContextModule.USER])

                authorizer = await self._active_auditor_service.get_authorizer_from_context()
                return await JwtAuthUtils.login_success(user, authorizer)
            else:
                logger.info('Authentication failed: password invalid')
        else:
            logger.info(f'Authentication failed: user "{login_dto.username}" not found')

        raise InvalidCredentialsException()


    async def social_login_signup(self, user_info: SocialLoginUserInfo, auth_granularity: bool = False) -> SocialLoginUserInfo:
        if not auth_granularity:
            login_dto = EmailLoginRequest(username=user_info.email, password="password")  # Used a dummy password
            await self.basic_login(login_dto, False)

            return user_info

        # GO BELOW WHEN HANDLING GRANULAR SOCIAL AUTH, Like allowing a user merge existing password account with social account

        user_exists = await self._user_service.exists_by_email(user_info.email)

        if user_exists:
            if user_info.operation_type == SocialAuthOperationType.LOGIN:
                login_dto = EmailLoginRequest(username=user_info.email, password="password") # Used a dummy password
                await self.basic_login(login_dto, False)

                return user_info
            elif user_info.operation_type == SocialAuthOperationType.SIGNUP:
                user = await self._user_service.get_by_email(user_info.email)
                existing_user_info = SocialLoginUserInfo(
                    email=user.email,
                    firstname=user.firstname,
                    lastname=user.lastname,
                    operation_type=user_info.operation_type,
                    frontend_origin=user_info.frontend_origin,
                    otp=user_info.otp,
                    response_code = SocialAuthResponseType.SOCIALAUTH_EXISTS,
                    response_message = "User already exists, is that you?"
                )

                await RedisUtils.set_redis(key=user_info.email, value=user_info) # just to use it when user confirms

                return existing_user_info
            else:
                raise NotImplementedException(message=f"Unknown SocialAuthOperationType: {user_info.operation_type}")
        else:
            if user_info.operation_type == SocialAuthOperationType.LOGIN:
                await RedisUtils.set_redis(key=user_info.email, value=user_info) # just to use it when user confirms

                user_info.response_code = SocialAuthResponseType.SOCIALAUTH_NOTFOUND
                user_info.response_message = "No user found with your details, do you wish to signup?"

                return user_info
            elif user_info.operation_type == SocialAuthOperationType.SIGNUP:
                await self._user_service.store_verified_email_otp(email=user_info.email, otp=user_info.otp)
                create_user_dto = CreateUserOptionalPasswordDto(
                    otp=user_info.otp,
                    email=user_info.email,
                    firstname=user_info.firstname,
                    lastname=user_info.lastname
                )
                await self._user_service.create_user_optional_password(obj_in=create_user_dto)

                return user_info
            else:
                raise NotImplementedException(message=f"Unknown SocialAuthOperationType: {user_info.operation_type}")

    async def refresh_token(self) -> SuccessResponse[bool]:
        _, authorizer = await self._active_auditor_service.get_combined_authorizer_from_context()

        await JwtAuthUtils.refresh_access_token(authorizer)

        return SuccessResponse(
            data=True
        )

    async def logout(self) -> SuccessResponse[bool]:
        _, authorizer = await self._active_auditor_service.get_combined_authorizer_from_context()

        await JwtAuthUtils.revoke_token(authorizer)

        await self._user_service.update_last_active(authorizer.get_jwt_subject())

        return SuccessResponse(
            data=True
        )

    async def change_password(self, change_password_dto: ChangePasswordDto) -> SuccessResponse[bool]:
        _, authorizer = await self._active_auditor_service.get_combined_authorizer_from_context()

        user_id = await self._active_auditor_service.get_active_user_id(authorizer=authorizer, jwt_required=True)
        await self._auth_validator.should_exist_by_id(user_id)

        user = await self._user_service.get_user_model(user_id, "password")
        old_password_is_valid = Utils.verify_password(change_password_dto.old_password, user.password)
        if not old_password_is_valid:
            raise InvalidCredentialsException(message='Old password mismatch')

        await self._user_service.update_user_change_password(new_password=change_password_dto.new_password)

        await JwtAuthUtils.revoke_token(authorizer, TokenType.REFRESH)

        return SuccessResponse(
            data=True
        )

    async def send_password_recovery_message(self, payload: PasswordResetRequest) -> SuccessResponse[bool]:
        user = await self._user_service.get_by_email(payload.email)
        if user:
            otp = Utils.get_otp_code('i')
            time_to_live = timedelta(seconds=self.otp_token_expire_seconds)
            await RedisUtils.set_redis(otp, payload.email, time_to_live)

            await (await self.get_account_security_messages()).send_password_reset_request_message(
                recipient_user_id=MessageRecipientUserId(user_id=user.id),
                context_modules=[MessageContextModule.USER],
                extra_context={"otp": otp}
            )

        return SuccessResponse(
            data=True
        )

    async def recover_password(self, payload: PasswordResetConfirm) -> LoginSuccessDto:
        email = await RedisUtils.get_redis(payload.token)
        if not email:
            raise InvalidTokenException(message='Token expired')
        user_exists = await self._user_service.exists_by_email(email)
        if not user_exists:
            raise InvalidCredentialsException(message='No active user found')

        updated_user_response = await self._user_service.update_user_change_password(new_password=payload.new_password)
        updated_user = updated_user_response.data

        user_data = await self._user_service.combine_profile_data(updated_user)

        _, authorizer = await self._active_auditor_service.get_combined_authorizer_from_context()
        return await JwtAuthUtils.login_success(user_data, authorizer)
