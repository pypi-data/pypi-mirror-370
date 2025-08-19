from kink import inject

from appodus_utils.domain.user.repo import UserRepo
from appodus_utils.exception.exceptions import ResourceNotFoundException


@inject
class AuthValidator:
    def __init__(self, user_repo: UserRepo):
        self._user_repo = user_repo

    async def should_exist_by_id(self, _id: str):
        if not (await self._user_repo.exists_by_id(_id)):
            raise ResourceNotFoundException("User")
