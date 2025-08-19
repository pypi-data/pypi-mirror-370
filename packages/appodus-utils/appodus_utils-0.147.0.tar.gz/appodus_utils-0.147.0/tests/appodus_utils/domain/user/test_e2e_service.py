from datetime import timedelta
from unittest import IsolatedAsyncioTestCase

from _pytest.monkeypatch import MonkeyPatch
from kink import di
from polyfactory.factories.pydantic_factory import ModelFactory


from appodus_utils.common.utils_settings import utils_settings
from appodus_utils.config.bootstrap import BaseDiBootstrap

from appodus_utils import Utils
from appodus_utils.common.appodus_test_utils import TestUtils
from appodus_utils.db.redis_utils import RedisUtils
from appodus_utils.db.session import close_db_engine, init_db_engine_and_session
from appodus_utils.decorators.decorate_all_methods import decorate_all_methods
from appodus_utils.decorators.transactional import TransactionSessionPolicy, transactional
from appodus_utils.domain.user.auth.models import EmailValidationRequest, LoginSuccessDto
from appodus_utils.domain.user.models import User, QueryUserDto, CreateUserDto, SearchUserDto, UpdateNameDto, Gender
from appodus_utils.domain.user.service import UserService
from tests.appodus_utils.test_utils import mock_active_auditor_service


@decorate_all_methods(transactional(session_policy=TransactionSessionPolicy.ALWAYS_NEW),
                      exclude=['asyncTearDown', 'asyncSetUp'])
class TestUserService(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        init_db_engine_and_session()

        self.user_service: UserService = di[UserService]
        self.monkeypatch = MonkeyPatch()

    async def asyncTearDown(self):
        self.monkeypatch.undo()
        await self._truncate_tables()
        await close_db_engine()

    @staticmethod
    async def _truncate_tables():
        await TestUtils.truncate_entities([User])

    async def create_user_and_mock_active_auditor_service(self, count: int = 1) -> LoginSuccessDto:

        create_user_dto = CreateUserDtoFactory.build()

        # Handle Unique Email
        create_user_dto.email = f"{count}_{create_user_dto.email}"

        # mock_active_auditor_service
        mock_active_auditor_service(monkeypatch=self.monkeypatch, user=QueryUserDto.model_copy(create_user_dto))

        await self.user_service.store_verified_email_otp(
            email=create_user_dto.email,
            otp=create_user_dto.otp
        )

        created_user_response = await self.user_service.create_user(create_user_dto)

        # re-mock_active_auditor_service to include User ID
        mock_active_auditor_service(monkeypatch=self.monkeypatch, user=QueryUserDto.model_copy(created_user_response))

        return created_user_response


    async def test_create_user(self):
        # PREPARE
        create_user_dto = CreateUserDtoFactory.build()
        # mock_active_auditor_service
        mock_active_auditor_service(monkeypatch=self.monkeypatch, user=QueryUserDto.model_copy(create_user_dto))
        await self.user_service.store_verified_email_otp(
            email=create_user_dto.email,
            otp=create_user_dto.otp
        )

        # ACT
        created_user_response = await self.user_service.create_user(create_user_dto)

        # ASSERT
        self.assertIsNotNone(created_user_response.id)

    async def test_get_user(self):
        # PREPARE
        created_user = await self.create_user_and_mock_active_auditor_service()

        # ACT
        get_user_response = await self.user_service.get_user(user_id=created_user.id)
        gotten_user = get_user_response.data

        # ASSERT
        self.assertIsNotNone(gotten_user.id)

    async def test_get_user_model(self):
        # PREPARE
        created_user = await self.create_user_and_mock_active_auditor_service()

        # ACT
        user = await self.user_service.get_user_model(user_id=created_user.id)

        # ASSERT
        self.assertIsNotNone(user.id)

    async def test_exists_by_email(self):
        # PREPARE
        created_user = await self.create_user_and_mock_active_auditor_service()

        # ACT
        user_exists = await self.user_service.exists_by_email(email=created_user.email)

        # ASSERT
        self.assertTrue(user_exists)

    async def test_get_by_email(self):
        # PREPARE
        created_user = await self.create_user_and_mock_active_auditor_service()

        # ACT
        get_user_response = await self.user_service.get_by_email(email=created_user.email)

        # ASSERT
        self.assertIsNotNone(get_user_response.id)

    async def test_get_user_page(self):
        # PREPARE
        count = 2
        for index in range(count):
            await self.create_user_and_mock_active_auditor_service(count=index)
        search_dto: SearchUserDto = SearchUserDto(
            page_size=10,
            page=0
        )

        # ACT
        user_page = await self.user_service.get_user_page(search_dto=search_dto)

        # ASSERT
        self.assertEqual(count, user_page.meta.count)

    async def test_update_user_change_password(self):
        # PREPARE
        await self.create_user_and_mock_active_auditor_service()
        new_password = "new_password"

        # ACT
        update_user_response = await self.user_service.update_user_change_password(
            new_password=new_password
        )
        updated_user = update_user_response.data

        # ASSERT
        self.assertEqual(2, updated_user.version)

    async def test_update_last_active(self):
        # PREPARE
        created_user = await self.create_user_and_mock_active_auditor_service()

        # ACT
        update_user_response = await self.user_service.update_last_active(
            user_id=created_user.id
        )
        updated_user = update_user_response.data

        # ASSERT
        self.assertEqual(2, updated_user.version)

    async def test_update_active_user_name(self):
        # PREPARE
        await self.create_user_and_mock_active_auditor_service()
        update_dto = UpdateNameDto(
            firstname="firstname",
            middle_name="middle_name",
            lastname="lastname"
        )

        # ACT
        update_user_response = await self.user_service.update_active_user_name(
            update_dto=update_dto
        )
        updated_user = update_user_response.data

        # ASSERT
        self.assertEqual(2, updated_user.version)

    async def test_soft_delete_user(self):
        # PREPARE
        created_user = await self.create_user_and_mock_active_auditor_service()

        # ACT
        get_user_response = await self.user_service.soft_delete_by_admin(user_id=created_user.id)
        user_deleted = get_user_response.data

        # ASSERT
        self.assertTrue(user_deleted)

    async def test_deactivate_active_user(self):
        # PREPARE
        await self.create_user_and_mock_active_auditor_service()
        reason = "deactivation reason"

        # ACT
        update_user_response = await self.user_service.deactivate_active_user(
            reason=reason
        )
        user_deactivated = update_user_response.data

        # ASSERT
        self.assertTrue(user_deactivated)

    async def test_activate_user(self):
        # PREPARE
        created_user = await self.create_user_and_mock_active_auditor_service()
        reason = "activation reason"

        # ACT
        update_user_response = await self.user_service.activate_user(
            user_id=created_user.id,
            reason=reason
        )
        user_activated = update_user_response.data

        # ASSERT
        self.assertTrue(user_activated)

    async def test_send_phone_validation_message(self):
        # PREPARE
        created_user = await self.create_user_and_mock_active_auditor_service()

        # ACT
        update_user_response = await self.user_service.send_phone_validation_message(
            phone_ext=created_user.phone_ext,
            phone=created_user.phone
        )
        user_activated = update_user_response.data

        # ASSERT
        self.assertTrue(user_activated)

    async def test_update_phone(self):
        # PREPARE
        created_user = await self.create_user_and_mock_active_auditor_service()

        otp="mock_otp"
        time_to_live = timedelta(seconds=30)
        phone_delimited = f'{created_user.phone_ext}:{created_user.phone}'

        store_key = f'{created_user.id}:{otp}'
        await RedisUtils.set_redis(store_key, phone_delimited, time_to_live)

        # ACT
        update_user_response = await self.user_service.update_phone(
            otp=otp
        )
        user_activated = update_user_response.data

        # ASSERT
        self.assertTrue(user_activated)

    async def test_send_email_validation_message(self):
        # PREPARE
        await self.create_user_and_mock_active_auditor_service()
        payload = EmailValidationRequest(
            email="kingsley.ezenwere@gmail.com"
        )
        is_a_new_user = False

        # ACT
        update_user_response = await self.user_service.send_email_validation_message(
            payload=payload,
            is_a_new_user=is_a_new_user
        )
        user_activated = update_user_response.data

        # ASSERT
        self.assertTrue(user_activated)

    async def test_store_verified_email_otp(self):
        # PREPARE
        created_user = await self.create_user_and_mock_active_auditor_service()
        otp="mock_otp"
        await self.user_service.store_verified_email_otp(
            email=created_user.email,
            otp=otp
        )

        # ACT
        await self.user_service._validate_email_verification_otp(
            email=created_user.email,
            otp=otp
        )

    async def test_validate_and_store_email_verification_otp(self):
        # PREPARE
        created_user = await self.create_user_and_mock_active_auditor_service()

        otp = Utils.get_otp_code()
        store_key = f'{created_user.email}:{otp}'

        time_to_live = timedelta(seconds=30)
        await RedisUtils.set_redis(store_key, created_user.email, time_to_live)

        # ACT
        store_validate_otp_response = await self.user_service.validate_and_store_email_verification_otp(
            email=created_user.email,
            otp=otp
        )
        validated_otp_stored = store_validate_otp_response.data

        # ASSERT
        self.assertTrue(validated_otp_stored)

    async def test_update_email(self):
        # PREPARE
        created_user = await self.create_user_and_mock_active_auditor_service()

        otp="mock_otp"

        await self.user_service.store_verified_email_otp(
            email=created_user.email,
            otp=otp
        )

        # ACT
        update_user_response = await self.user_service.update_email(
            email=created_user.email,
            otp=otp
        )
        user_activated = update_user_response.data

        # ASSERT
        self.assertTrue(user_activated)

    async def test_update_gender(self):
        # PREPARE
        await self.create_user_and_mock_active_auditor_service()

        # ACT
        update_user_response = await self.user_service.update_gender(
            gender=Gender.FEMALE
        )
        gender_updated = update_user_response.data

        # ASSERT
        self.assertTrue(gender_updated)

    async def test_update_dob(self):
        # PREPARE
        await self.create_user_and_mock_active_auditor_service()

        # ACT
        update_user_response = await self.user_service.update_dob(
            dob=Utils.datetime_now_to_db().date()
        )
        dob_updated = update_user_response.data

        # ASSERT
        self.assertTrue(dob_updated)


# OBJECT FAKER FACTORIES using polyfactory
class CreateUserDtoFactory(ModelFactory[CreateUserDto]):
    __model__ = CreateUserDto
    __check_model__ = False
    email="kingsley.ezenwere@gmail.com"
    phone="7039018727"
    phone_ext="234"