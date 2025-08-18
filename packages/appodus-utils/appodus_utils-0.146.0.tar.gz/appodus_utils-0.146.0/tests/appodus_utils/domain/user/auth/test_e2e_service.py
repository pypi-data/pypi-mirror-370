from datetime import timedelta
from unittest import IsolatedAsyncioTestCase

from _pytest.monkeypatch import MonkeyPatch
from kink import di

from appodus_utils.common.utils_settings import utils_settings
from appodus_utils.config.bootstrap import BaseDiBootstrap

from appodus_utils import Utils
from appodus_utils.common.appodus_test_utils import TestUtils
from appodus_utils.common.utils_settings import utils_settings
from appodus_utils.db.redis_utils import RedisUtils
from appodus_utils.db.session import close_db_engine, init_db_engine_and_session
from appodus_utils.decorators.decorate_all_methods import decorate_all_methods
from appodus_utils.decorators.transactional import TransactionSessionPolicy, transactional
from appodus_utils.domain.user.auth.models import LoginSuccessDto, EmailLoginRequest, SocialLoginUserInfo, \
    SocialAuthOperationType, ChangePasswordDto, PasswordResetRequest, PasswordResetConfirm, SocialAuthResponseType
from appodus_utils.domain.user.auth.service import AuthService
from appodus_utils.domain.user.models import User, QueryUserDto
from appodus_utils.domain.user.service import UserService
from tests.appodus_utils.domain.user.test_e2e_service import CreateUserDtoFactory
from tests.appodus_utils.test_utils import mock_active_auditor_service


@decorate_all_methods(transactional(session_policy=TransactionSessionPolicy.ALWAYS_NEW),
                      exclude=['asyncTearDown', 'asyncSetUp'])
class TestAuthService(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        init_db_engine_and_session()

        self.auth_service: AuthService = di[AuthService]
        self.user_service: UserService = di[UserService]
        self.monkeypatch = MonkeyPatch()

        self.create_user_dto = CreateUserDtoFactory.build()

    async def asyncTearDown(self):
        self.monkeypatch.undo()
        await self._truncate_tables()
        await close_db_engine()

    @staticmethod
    async def _truncate_tables():
        await TestUtils.truncate_entities([User])



    async def create_user_and_mock_active_auditor_service(self) -> LoginSuccessDto:
        # mock_active_auditor_service
        mock_active_auditor_service(monkeypatch=self.monkeypatch, user=QueryUserDto.model_copy(self.create_user_dto))

        await self.user_service.store_verified_email_otp(
            email=self.create_user_dto.email,
            otp=self.create_user_dto.otp
        )

        created_user_response = await self.user_service.create_user(self.create_user_dto)

        # re-mock_active_auditor_service to include User ID
        mock_active_auditor_service(monkeypatch=self.monkeypatch, user=QueryUserDto.model_copy(created_user_response))

        return created_user_response


    async def test_basic_login(self):
        await self.create_user_and_mock_active_auditor_service()

        login_dto: EmailLoginRequest = EmailLoginRequest(
            username=self.create_user_dto.email,
            password=self.create_user_dto.password
        )

        login_success_response = await self.auth_service.basic_login(login_dto=login_dto)

        self.assertIsNotNone(login_success_response.id)

    async def test_social_login_signup__on_login_and_user_exists(self):
        await self.create_user_and_mock_active_auditor_service()

        user_info: SocialLoginUserInfo = SocialLoginUserInfo(
            email=self.create_user_dto.email,
            firstname=self.create_user_dto.firstname,
            lastname=self.create_user_dto.lastname,
            otp=self.create_user_dto.otp,
            operation_type=SocialAuthOperationType.LOGIN,
            frontend_origin="/"
        )

        response: SocialLoginUserInfo = await self.auth_service.social_login_signup(user_info=user_info, auth_granularity=True)

        self.assertEqual(SocialAuthResponseType.SOCIALAUTH_SUCCEEDED, response.response_code)

    async def test_social_login_signup__on_login_and_user_dont_exist(self):
        await self.create_user_and_mock_active_auditor_service()

        user_info: SocialLoginUserInfo = SocialLoginUserInfo(
            email="non_existing.email@gmail.com",
            firstname=self.create_user_dto.firstname,
            lastname=self.create_user_dto.lastname,
            otp=self.create_user_dto.otp,
            operation_type=SocialAuthOperationType.LOGIN,
            frontend_origin="/"
        )

        response: SocialLoginUserInfo = await self.auth_service.social_login_signup(user_info=user_info, auth_granularity=True)

        self.assertEqual(SocialAuthResponseType.SOCIALAUTH_NOTFOUND, response.response_code)

    async def test_social_login_signup__on_signup_and_user_exists(self):
        await self.create_user_and_mock_active_auditor_service()

        user_info: SocialLoginUserInfo = SocialLoginUserInfo(
            email=self.create_user_dto.email,
            firstname=self.create_user_dto.firstname,
            lastname=self.create_user_dto.lastname,
            otp=self.create_user_dto.otp,
            operation_type=SocialAuthOperationType.SIGNUP,
            frontend_origin="/"
        )

        response: SocialLoginUserInfo = await self.auth_service.social_login_signup(user_info=user_info, auth_granularity=True)

        self.assertEqual(SocialAuthResponseType.SOCIALAUTH_EXISTS, response.response_code)

    async def test_social_login_signup__on_signup_and_user_dont_exist(self):
        await self.create_user_and_mock_active_auditor_service()

        user_info: SocialLoginUserInfo = SocialLoginUserInfo(
            email="non_existing.email@gmail.com",
            firstname=self.create_user_dto.firstname,
            lastname=self.create_user_dto.lastname,
            otp=self.create_user_dto.otp,
            operation_type=SocialAuthOperationType.SIGNUP,
            frontend_origin="/"
        )

        response: SocialLoginUserInfo = await self.auth_service.social_login_signup(user_info=user_info, auth_granularity=True)

        self.assertEqual(SocialAuthResponseType.SOCIALAUTH_SUCCEEDED, response.response_code)

    async def test_refresh_token(self):
        await self.create_user_and_mock_active_auditor_service()

        refresh_token_response = await self.auth_service.refresh_token()
        token_refreshed = refresh_token_response.data

        self.assertTrue(token_refreshed)

    async def test_logout(self):
        await self.create_user_and_mock_active_auditor_service()

        logout_response = await self.auth_service.logout()
        logged_out = logout_response.data

        self.assertTrue(logged_out)

    async def test_change_password(self):
        await self.create_user_and_mock_active_auditor_service()

        change_password_dto: ChangePasswordDto = ChangePasswordDto(
            old_password=self.create_user_dto.password,
            new_password="new_password"
        )

        change_password_response = await self.auth_service.change_password(change_password_dto=change_password_dto)
        password_changed = change_password_response.data

        self.assertTrue(password_changed)

    async def test_send_password_recovery_message(self):
        await self.create_user_and_mock_active_auditor_service()

        payload: PasswordResetRequest = PasswordResetRequest(
            email=self.create_user_dto.email
        )

        send_message_response = await self.auth_service.send_password_recovery_message(payload=payload)
        message_changed = send_message_response.data

        self.assertTrue(message_changed)

    async def test_recover_password(self):
        await self.create_user_and_mock_active_auditor_service()

        # SET TOKEN
        otp = Utils.get_otp_code('i')
        time_to_live = timedelta(seconds=utils_settings.OTP_TOKEN_EXPIRE_SECONDS)
        await RedisUtils.set_redis(otp, self.create_user_dto.email, time_to_live)

        payload: PasswordResetConfirm = PasswordResetConfirm(
            token=otp,
            new_password="new_password"
        )

        recover_password_response = await self.auth_service.recover_password(payload=payload)

        self.assertIsNotNone(recover_password_response.id)
