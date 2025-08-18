from typing import Optional

from sqlalchemy import Column, String, JSON, Boolean
from sqlalchemy.ext.mutable import MutableDict

from appodus_utils import BaseEntity, PageRequest, BaseQueryDto, Object
from appodus_utils.db.types.loci import Loci


class Address(BaseEntity):
    __tablename__ = 'addresses'
    user_id = Column(String(36), nullable=False, index=True, unique=False)
    street_number = Column(String(10), nullable=False)
    street_name = Column(String(40), nullable=False)
    neighborhood = Column(String(20), nullable=False)
    locality = Column(String(20), nullable=False)
    lga = Column(String(36), nullable=False)
    state = Column(String(36), nullable=False)
    country_id = Column(String(36), nullable=False)
    gps_location = Column(MutableDict.as_mutable(JSON), nullable=False)
    verified = Column(Boolean, default=False, nullable=False)


class AddressBaseDto(Object):
    street_number: str
    street_name: str
    neighborhood: str
    locality: str
    lga: str
    state: str
    country_id: str
    gps_location: Loci


class CreateAddressDto(AddressBaseDto):
    user_id: str


class UpdateAddressDto(AddressBaseDto):
    pass


class _UpdateAddressDto(Object):
    verified: Optional[bool] = None


class SearchAddressDto(PageRequest, BaseQueryDto):
    user_id: Optional[str] = None
    street_number: Optional[str] = None
    street_name: Optional[str] = None
    neighborhood: Optional[str] = None
    locality: Optional[str] = None
    lga: Optional[str] = None
    state: Optional[str] = None
    country_id: Optional[str] = None
    verified: Optional[bool] = None


class QueryAddressDto(AddressBaseDto, _UpdateAddressDto, BaseQueryDto):
    user_id: str
