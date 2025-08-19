from typing import Type, Optional

from kink import inject
from sqlalchemy import literal, select
from sqlalchemy.ext.asyncio import AsyncSession

from appodus_utils.db.repo import GenericRepo
from appodus_utils.domain.user.models import User, CreateUserDto, UpdateUserDto, QueryUserDto, SearchUserDto


@inject
class UserRepo(GenericRepo[User, CreateUserDto, UpdateUserDto, QueryUserDto, SearchUserDto]):
    def __init__(self, db: AsyncSession, model: Type[User] = User, query_dto: Type[QueryUserDto] = QueryUserDto):
        super().__init__(db, model, query_dto)
        self.db = db

    async def get_by_email(self, email_address: str) -> Optional[QueryUserDto]:
        stmt = select(self._model).where(
            self._model.deleted.is_(False),
            self._model.email == email_address
        )

        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()

        if row:
            converted_user = self._db_utils.build_row_response(row=row, part_of_a_page=True)
            converted_user.password = row.password

            return converted_user

        return None

    async def exists_by_email(self, email: str) -> bool:
        stmt = select(literal(True)).where(
            self._model.deleted.is_(False),
            self._model.email == email
        )
        result = await self._session.execute(stmt)
        return result.scalar() is not None
