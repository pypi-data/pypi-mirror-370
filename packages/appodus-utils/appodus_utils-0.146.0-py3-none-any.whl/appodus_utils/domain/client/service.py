from logging import Logger

from cryptography.fernet import Fernet

from appodus_utils import Page
from appodus_utils.common.client_utils import ClientUtils
from appodus_utils.db.models import SuccessResponse
from kink import inject, di

from appodus_utils.decorators.decorate_all_methods import decorate_all_methods
from appodus_utils.decorators.method_trace_logger import method_trace_logger
from appodus_utils.decorators.transactional import transactional, TransactionSessionPolicy
from appodus_utils.domain.client.models import CreateClientDto, QueryClientDto, ClientAccessRuleDto, \
    SearchClientDto, _CreateClientDto, _UpdateClientDto
from appodus_utils.domain.client.repo import ClientRepo
from appodus_utils.domain.client.validator import ClientValidator

logger: Logger = di['logger']


@inject
@decorate_all_methods(transactional(session_policy=TransactionSessionPolicy.FALLBACK_NEW), exclude=['get_account_security_messages'])
@decorate_all_methods(method_trace_logger, exclude=['get_account_security_messages'])
class ClientService:
    def __init__(self, client_repo: ClientRepo,
                 client_validator: ClientValidator
                 ):
        self._client_repo = client_repo
        self._client_validator = client_validator

    async def seed_client(self, obj_in: _CreateClientDto) -> SuccessResponse[QueryClientDto]:
        obj_in.client_secret = ClientUtils.encrypt_api_secret(obj_in.client_secret.encode())

        return await self._client_repo.create(obj_in)

    async def create_client(self, obj_in: CreateClientDto) -> SuccessResponse[QueryClientDto]:

        client_secret = Fernet.generate_key()
        client_secret_encrypted = ClientUtils.encrypt_api_secret(client_secret)

        create_obj = _CreateClientDto.model_validate({
            **obj_in.model_dump(),
            "client_secret": client_secret_encrypted
        })

        return await self._client_repo.create(create_obj)

    async def client_exists(self, client_id: str) -> bool:
        return await self._client_repo.exists_by_id(client_id)

    async def get_client(self, client_id: str) -> SuccessResponse[QueryClientDto]:
        await self._client_validator.should_exist_by_id(client_id)
        return await self._client_repo.get(client_id)

    async def get_client_page(self, search_dto: SearchClientDto) -> Page[QueryClientDto]:
        return await self._client_repo.get_page(search_dto)

    async def get_client_access_rules(self, client_id: str) -> ClientAccessRuleDto:
        await self._client_validator.should_exist_by_id(client_id)
        client = await self._client_repo.get_model(client_id)
        return ClientAccessRuleDto(**client.access_rules)

    async def get_client_secret(self, client_id: str) -> str:
        await self._client_validator.should_exist_by_id(client_id)
        client = await self._client_repo.get_model(client_id)

        return client.client_secret

    async def update_client_details(self, client_id: str, name: str, description: str) -> bool:
        await self._client_validator.should_exist_by_id(client_id)
        update_obj = _UpdateClientDto(name=name, description=description)

        await self._client_repo.update(update_obj.model_dump())

        return True

    async def update_client_access_rules(self, client_id: str, dto: ClientAccessRuleDto) -> bool:
        await self._client_validator.should_exist_by_id(client_id)
        client = await self._client_repo.get_model(client_id)
        client.access_rules.clear()
        client.access_rules.update(dto.model_dump())

        return True
