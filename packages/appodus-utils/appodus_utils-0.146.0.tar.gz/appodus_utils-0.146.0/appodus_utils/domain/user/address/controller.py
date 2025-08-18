from http import HTTPStatus

from fastapi import APIRouter
from kink import di

from appodus_utils.db.models import SuccessResponse, Page
from appodus_utils.domain.user.address.models import QueryAddressDto, CreateAddressDto, SearchAddressDto, \
    UpdateAddressDto
from appodus_utils.domain.user.address.service import AddressService

address_service: AddressService = di[AddressService]

address_router = APIRouter(prefix="/addresses", tags=["Addresses"])


@address_router.post('/', response_model=SuccessResponse[QueryAddressDto], status_code=HTTPStatus.CREATED)
async def create_address(create_dto: CreateAddressDto) -> SuccessResponse[QueryAddressDto]:
    return await address_service.create_address(create_dto=create_dto)


@address_router.get('/{address_id}', response_model=SuccessResponse[QueryAddressDto], status_code=HTTPStatus.OK)
async def get_address(address_id: str) -> SuccessResponse[QueryAddressDto]:
    return await address_service.get_address(address_id=address_id)


@address_router.get('/', response_model=Page[QueryAddressDto], status_code=HTTPStatus.OK)
async def get_address_page(search_dto: SearchAddressDto) -> Page[QueryAddressDto]:
    return await address_service.get_address_page(search_dto=search_dto)


@address_router.get('/active-user', response_model=QueryAddressDto, status_code=HTTPStatus.OK)
async def get_address_page_for_active_user():
    return await address_service.get_address_page_for_active_user()


@address_router.patch('/{address_id}', response_model=SuccessResponse[QueryAddressDto], status_code=HTTPStatus.OK)
async def update_address(address_id: str, update_dto: UpdateAddressDto) -> SuccessResponse[QueryAddressDto]:
    return await address_service.update_address(address_id=address_id, update_dto=update_dto)


@address_router.patch('/{address_id}/verify', response_model=SuccessResponse[QueryAddressDto], status_code=HTTPStatus.OK)
async def verify_address(address_id: str) -> SuccessResponse[QueryAddressDto]:
    return await address_service.verify_address(address_id=address_id)


@address_router.delete('/{address_id}', response_model=SuccessResponse[bool], status_code=HTTPStatus.OK)
async def soft_delete_address(address_id: str) -> SuccessResponse[bool]:
    return await address_service.soft_delete_address(address_id=address_id)
