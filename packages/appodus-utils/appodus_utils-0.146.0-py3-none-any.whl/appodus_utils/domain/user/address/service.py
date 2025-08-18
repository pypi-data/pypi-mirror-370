from logging import Logger

from kink import inject, di

from appodus_utils import Page
from appodus_utils.db.models import SuccessResponse
from appodus_utils.decorators.decorate_all_methods import decorate_all_methods
from appodus_utils.decorators.method_trace_logger import method_trace_logger
from appodus_utils.decorators.transactional import transactional
from appodus_utils.domain.user.address.models import CreateAddressDto, QueryAddressDto, SearchAddressDto, \
    UpdateAddressDto, _UpdateAddressDto
from appodus_utils.domain.user.address.repo import AddressRepo
from appodus_utils.domain.user.address.validator import AddressValidator
from appodus_utils.domain.user.auth.active_auditor.service import ActiveAuditorService

logger: Logger = di['logger']


@inject
@decorate_all_methods(transactional())
@decorate_all_methods(method_trace_logger)
class AddressService:
    def __init__(self, address_repo: AddressRepo,
                 address_validator: AddressValidator,
                 active_auditor_service: ActiveAuditorService):
        self._address_repo = address_repo
        self._address_validator = address_validator
        self._active_auditor_service = active_auditor_service

    async def create_address(self, create_dto: CreateAddressDto) -> SuccessResponse[QueryAddressDto]:
        return await self._address_repo.create(create_dto)

    async def get_address(self, address_id: str) -> SuccessResponse[QueryAddressDto]:
        await self._address_validator.should_exist_by_id(address_id)
        return await self._address_repo.get(address_id)

    async def get_address_page(self, search_dto: SearchAddressDto) -> Page[QueryAddressDto]:
        return await self._address_repo.get_page(search_dto=search_dto)

    async def get_address_page_for_active_user(self) -> Page[QueryAddressDto]:
        _, authorizer = await self._active_auditor_service.get_combined_authorizer_from_context()
        user_id = authorizer.get_jwt_subject()
        search_dto: SearchAddressDto = SearchAddressDto(user_id=user_id)
        return await self._address_repo.get_page(search_dto=search_dto)

    async def update_address(self, address_id: str, update_dto: UpdateAddressDto) -> SuccessResponse[QueryAddressDto]:
        await self._address_validator.should_exist_by_id(address_id)
        return await self._address_repo.update(address_id, update_dto)

    async def verify_address(self, address_id: str) -> SuccessResponse[QueryAddressDto]:
        await self._address_validator.should_exist_by_id(address_id)
        update_dto = _UpdateAddressDto(verified=True)
        return await self._address_repo.update(address_id, update_dto.model_dump(exclude_none=True))

    async def soft_delete_address(self, address_id: str) -> SuccessResponse[bool]:
        await self._address_validator.should_exist_by_id(address_id)
        await self._address_repo.soft_delete(address_id)

        return SuccessResponse(
                    data=True
                )
