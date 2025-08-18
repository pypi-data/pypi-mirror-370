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
from appodus_utils.domain.user.address.models import Address, CreateAddressDto, QueryAddressDto, SearchAddressDto, \
    UpdateAddressDto
from appodus_utils.domain.user.address.service import AddressService
from appodus_utils.domain.user.auth.models import LoginSuccessDto
from appodus_utils.domain.user.models import CreateUserDto, QueryUserDto, User
from appodus_utils.domain.user.service import UserService
from tests.appodus_utils.domain.user.test_e2e_service import CreateUserDtoFactory
from tests.appodus_utils.test_utils import mock_active_auditor_service


@decorate_all_methods(transactional(session_policy=TransactionSessionPolicy.ALWAYS_NEW),
                      exclude=['asyncTearDown', 'asyncSetUp'])
class TestAddressService(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        init_db_engine_and_session()

        self.address_service: AddressService = di[AddressService]
        self.user_service: UserService = di[UserService]
        self.monkeypatch = MonkeyPatch()

    async def asyncTearDown(self):
        self.monkeypatch.undo()
        await self._truncate_tables()
        await close_db_engine()

    @staticmethod
    async def _truncate_tables():
        await TestUtils.truncate_entities([Address, User])

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

    async def create_address(self, user_id: str) -> QueryAddressDto:
        create_address_dto = CreateAddressDtoFactory.build()
        create_address_dto.user_id = user_id

        created_address_response = await self.address_service.create_address(create_address_dto)
        created_address = created_address_response.data

        return created_address


    async def test_create_address(self):
        create_address_dto = CreateAddressDtoFactory.build()

        created_address_response = await self.address_service.create_address(create_address_dto)
        created_address = created_address_response.data

        self.assertIsNotNone(created_address.id)

    async def test_get_address(self):
        created_user = await self.create_user_and_mock_active_auditor_service()
        created_address = await self.create_address(user_id=created_user.id)

        get_address_response = await self.address_service.get_address(address_id=created_address.id)
        gotten_address = get_address_response.data

        self.assertIsNotNone(gotten_address.id)

    async def test_get_address_page(self):
        created_user = await self.create_user_and_mock_active_auditor_service()
        count = 2
        for _ in range(count):
            await self.create_address(user_id=created_user.id)

        search_dto: SearchAddressDto = SearchAddressDto(
            page_size=10,
            page=0
        )

        address_page = await self.address_service.get_address_page(search_dto=search_dto)

        self.assertEqual(count, address_page.meta.count)

    async def test_get_address_page_for_active_user(self):
        created_user = await self.create_user_and_mock_active_auditor_service()
        count = 2
        for _ in range(count):
            await self.create_address(user_id=created_user.id)

        address_page = await self.address_service.get_address_page_for_active_user()

        self.assertEqual(count, address_page.meta.count)

    async def test_update_address(self):
        created_user = await self.create_user_and_mock_active_auditor_service()
        created_address = await self.create_address(user_id=created_user.id)

        update_dto = UpdateAddressDto(**created_address.model_dump())
        update_dto.lga = "Eti Osa"

        update_address_response = await self.address_service.update_address(
            address_id=created_address.id,
            update_dto=update_dto
        )
        updated_address = update_address_response.data

        self.assertEqual(update_dto.lga, updated_address.lga)

    async def test_verify_address(self):
        created_user = await self.create_user_and_mock_active_auditor_service()
        created_address = await self.create_address(user_id=created_user.id)

        get_address_response = await self.address_service.verify_address(address_id=created_address.id)
        gotten_address = get_address_response.data

        self.assertTrue(gotten_address.verified)

    async def test_soft_delete_address(self):
        created_user = await self.create_user_and_mock_active_auditor_service()
        created_address = await self.create_address(user_id=created_user.id)

        get_address_response = await self.address_service.soft_delete_address(address_id=created_address.id)
        gotten_address = get_address_response.data

        self.assertTrue(gotten_address)

# OBJECT FAKER FACTORIES using polyfactory
class CreateAddressDtoFactory(ModelFactory[CreateAddressDto]):
    __model__ = CreateAddressDto
    __check_model__ = False
    street_number = "23B"
