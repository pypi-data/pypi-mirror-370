from typing import Type

from kink import inject
from sqlalchemy.ext.asyncio import AsyncSession

from appodus_utils.db.repo import GenericRepo
from appodus_utils.domain.user.address.models import Address, CreateAddressDto, UpdateAddressDto, QueryAddressDto, \
    SearchAddressDto


@inject
class AddressRepo(GenericRepo[Address, CreateAddressDto, UpdateAddressDto, QueryAddressDto, SearchAddressDto]):
    def __init__(self, db: AsyncSession, model: Type[Address] = Address, query_dto: Type[QueryAddressDto] = QueryAddressDto):
        super().__init__(db, model, query_dto)
        self.db = db
