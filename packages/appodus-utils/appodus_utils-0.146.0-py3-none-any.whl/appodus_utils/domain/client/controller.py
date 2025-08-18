from appodus_utils import Page
from appodus_utils.db.models import SuccessResponse
from fastapi import APIRouter
from kink import di
from starlette import status

from appodus_utils.domain.client.models import QueryClientDto, CreateClientDto, SearchClientDto, ClientAccessRuleDto
from appodus_utils.domain.client.service import ClientService

client_router = APIRouter(prefix="/v1/clients", tags=["Clients"])

client_service: ClientService = di[ClientService]


@client_router.post("/", summary='Create client', response_model=SuccessResponse[QueryClientDto],
                  status_code=status.HTTP_201_CREATED)
async def client_create(
        dto: CreateClientDto
) -> SuccessResponse[QueryClientDto]:
    return await client_service.create_client(dto)

@client_router.put("/{client_id}", summary='Update client details', response_model=bool,
                  status_code=status.HTTP_200_OK)
async def update_client_details(client_id: str, name: str, description: str) -> bool:
    return await client_service.update_client_details(client_id=client_id, name=name, description=description)

@client_router.patch("/{client_id}", summary='Update client access rules', response_model=bool,
                  status_code=status.HTTP_200_OK)
async def update_client_access_rules(
        client_id: str, dto: ClientAccessRuleDto
) -> bool:
    return await client_service.update_client_access_rules(client_id=client_id, dto=dto)

@client_router.get("/{client_id}", summary='Search clients', response_model=SuccessResponse[QueryClientDto],
                  status_code=status.HTTP_200_OK)
async def get_client(client_id: str) -> SuccessResponse[QueryClientDto]:
    return await client_service.get_client(client_id)

@client_router.get("/", summary='Search clients', response_model=Page[QueryClientDto],
                  status_code=status.HTTP_200_OK)
async def get_client_page(search_dto: SearchClientDto) -> Page[QueryClientDto]:
    return await client_service.get_client_page(search_dto)
