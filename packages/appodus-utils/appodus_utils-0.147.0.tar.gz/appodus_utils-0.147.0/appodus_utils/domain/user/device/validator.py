from kink import inject

from appodus_utils.domain.user.device.repo import DeviceRepo
from appodus_utils.exception.exceptions import ResourceNotFoundException


@inject
class DeviceValidator:
    def __init__(self, device_repo: DeviceRepo):
        self._device_repo = device_repo

    async def should_exist_by_id(self, _id: str):
        if not (await self._device_repo.exists_by_id(_id)):
            raise ResourceNotFoundException("Device")

    async def should_exist_by_device_id(self, device_id: str):
        if not (await self._device_repo.exists_by_device_id(device_id)):
            raise ResourceNotFoundException("Device", )
