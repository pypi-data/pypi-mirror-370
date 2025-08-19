from kink import inject

from appodus_utils.domain.user.repo import UserRepo
from appodus_utils.exception.exceptions import ResourceNotFoundException, ResourceConflictException


@inject
class UserValidator:
    def __init__(self, user_repo: UserRepo):
        self._user_repo = user_repo

    async def should_exist_by_id(self, _id: str):
        if not (await self._user_repo.exists_by_id(_id)):
            raise ResourceNotFoundException("User")

    async def should_not_exist_by_email(self, email: str):
        if await self._user_repo.exists_by_email(email):
            raise ResourceConflictException(resource="User", message="A user with this email already exists")
