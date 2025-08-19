from typing import Type

from kink import inject
from sqlalchemy.ext.asyncio import AsyncSession

from appodus_utils.db.repo import GenericRepo
from appodus_utils.domain.client.models import Client, CreateClientDto, UpdateClientDto, QueryClientDto, SearchClientDto


@inject
class ClientRepo(GenericRepo[Client, CreateClientDto, UpdateClientDto, QueryClientDto, SearchClientDto]):
    def __init__(self, db: AsyncSession, model: Type[Client] = Client,
                 query_dto: Type[QueryClientDto] = QueryClientDto):
        super().__init__(db, model, query_dto)
        self.db = db
