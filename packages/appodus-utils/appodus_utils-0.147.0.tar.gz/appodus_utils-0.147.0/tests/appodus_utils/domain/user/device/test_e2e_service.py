from unittest import IsolatedAsyncioTestCase

from _pytest.monkeypatch import MonkeyPatch
from kink import di
from polyfactory.factories.pydantic_factory import ModelFactory


from appodus_utils.common.utils_settings import utils_settings
from appodus_utils.config.bootstrap import BaseDiBootstrap

from appodus_utils.common.appodus_test_utils import TestUtils
from appodus_utils.db.session import close_db_engine, init_db_engine_and_session
from appodus_utils.decorators.decorate_all_methods import decorate_all_methods
from appodus_utils.decorators.transactional import TransactionSessionPolicy, transactional
from appodus_utils.domain.user.device.models import Device, CreateDeviceDto, QueryDeviceDto, SearchDeviceDto
from appodus_utils.domain.user.device.service import DeviceService
from appodus_utils.domain.user.auth.models import LoginSuccessDto
from appodus_utils.domain.user.models import CreateUserDto, QueryUserDto, User
from appodus_utils.domain.user.service import UserService
from appodus_utils.integrations.messaging.models import PushToken
from tests.appodus_utils.domain.user.test_e2e_service import CreateUserDtoFactory
from tests.appodus_utils.test_utils import mock_active_auditor_service


@decorate_all_methods(transactional(session_policy=TransactionSessionPolicy.ALWAYS_NEW),
                      exclude=['asyncTearDown', 'asyncSetUp'])
class TestDeviceService(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        init_db_engine_and_session()

        self.device_service: DeviceService = di[DeviceService]
        self.user_service: UserService = di[UserService]
        self.monkeypatch = MonkeyPatch()

    async def asyncTearDown(self):
        self.monkeypatch.undo()
        await self._truncate_tables()
        await close_db_engine()

    @staticmethod
    async def _truncate_tables():
        await TestUtils.truncate_entities([Device, User])

    async def create_user_and_mock_active_auditor_service(self) -> LoginSuccessDto:

        create_user_dto = CreateUserDtoFactory.build()
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

    async def create_device(self, user_id: str) -> QueryDeviceDto:
        create_device_dto = CreateDeviceDtoFactory.build()
        create_device_dto.user_id = user_id

        created_device_response = await self.device_service.create_device(create_device_dto)
        created_device = created_device_response.data

        return created_device


    async def test_create_device(self):
        create_device_dto = CreateDeviceDtoFactory.build()

        created_device_response = await self.device_service.create_device(create_device_dto)
        created_device = created_device_response.data

        self.assertIsNotNone(created_device.id)

    async def test_get_device_page(self):
        created_user = await self.create_user_and_mock_active_auditor_service()
        count = 2
        for _ in range(count):
            await self.create_device(user_id=created_user.id)

        search_dto: SearchDeviceDto = SearchDeviceDto(
            page_size=10,
            page=0
        )

        device_page = await self.device_service.get_device_page(search_dto=search_dto)

        self.assertEqual(count, device_page.meta.count)

    async def test_update_device(self):
        created_user = await self.create_user_and_mock_active_auditor_service()
        created_device = await self.create_device(user_id=created_user.id)

        push_token: PushToken = PushToken(
            token="token",
        device_id="device_id"
        )

        update_device_response = await self.device_service.update_device_push_token(
            device_id=created_device.id,
            push_token=push_token
        )
        device_updated = update_device_response.data

        self.assertIsNotNone(device_updated)

# OBJECT FAKER FACTORIES using polyfactory
class CreateDeviceDtoFactory(ModelFactory[CreateDeviceDto]):
    __model__ = CreateDeviceDto
    __check_model__ = False
    street_number = "23B"
