from appodus_utils.exception.exceptions import ResourceNotFoundException
from kink import inject

from appodus_utils.domain.client.repo import ClientRepo


@inject
class ClientValidator:
    def __init__(self, client_repo: ClientRepo):
        self._client_repo = client_repo

    async def should_exist_by_id(self, _id: str):
        if not (await self._client_repo.exists_by_id(_id)):
            raise ResourceNotFoundException("Client")
