from logging import Logger

from appodus_utils import Page
from kink import inject, di

from appodus_utils.db.models import SuccessResponse
from appodus_utils.decorators.decorate_all_methods import decorate_all_methods
from appodus_utils.decorators.method_trace_logger import method_trace_logger
from appodus_utils.decorators.transactional import transactional
from appodus_utils.domain.user.device.models import CreateDeviceDto, QueryDeviceDto, SearchDeviceDto, _UpdateDeviceDto, \
    _CreateDeviceDto
from appodus_utils.domain.user.device.repo import DeviceRepo
from appodus_utils.domain.user.device.validator import DeviceValidator
from appodus_utils.integrations.messaging.models import PushToken

logger: Logger = di['logger']


@inject
@decorate_all_methods(transactional())
@decorate_all_methods(method_trace_logger)
class DeviceService:
    def __init__(self, device_repo: DeviceRepo, device_validator: DeviceValidator):
        self._device_repo = device_repo
        self._device_validator = device_validator

    async def create_device(self, obj_in: CreateDeviceDto) -> SuccessResponse[QueryDeviceDto]:
        create_dto = _CreateDeviceDto.model_validate(obj_in.model_dump())
        return await self._device_repo.create(create_dto)

    async def get_device_page(self, search_dto: SearchDeviceDto) -> Page[QueryDeviceDto]:
        return await self._device_repo.get_page(search_dto=search_dto)

    async def update_device_push_token(self, device_id: str, push_token: PushToken) -> SuccessResponse[bool]:
        await self._device_validator.should_exist_by_id(device_id)

        obj_in = _UpdateDeviceDto(push_token=push_token)
        await self._device_repo.update(device_id, obj_in.model_dump(exclude_none=True))

        return SuccessResponse(
            data=True
        )
