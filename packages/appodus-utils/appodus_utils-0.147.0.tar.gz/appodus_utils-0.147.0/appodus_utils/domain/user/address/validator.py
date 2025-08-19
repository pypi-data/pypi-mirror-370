from kink import inject

from appodus_utils.domain.user.address.repo import AddressRepo
from appodus_utils.exception.exceptions import ResourceNotFoundException


@inject
class AddressValidator:
    def __init__(self, address_repo: AddressRepo):
        self._address_repo = address_repo

    async def should_exist_by_id(self, _id: str):
        if not (await self._address_repo.exists_by_id(_id)):
            raise ResourceNotFoundException("Address")
